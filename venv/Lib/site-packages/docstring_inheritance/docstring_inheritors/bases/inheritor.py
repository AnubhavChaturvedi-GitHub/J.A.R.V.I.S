# Copyright 2021 Antoine DECHAUME
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Base class for docstrings inheritors."""

from __future__ import annotations

import difflib
import os
import warnings
from inspect import getfile
from inspect import getfullargspec
from inspect import getmodule
from inspect import getsourcelines
from inspect import unwrap
from textwrap import indent
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import cast

if TYPE_CHECKING:
    from . import SectionsType
    from .parser import BaseDocstringParser
    from .renderer import BaseDocstringRenderer


def get_similarity_ratio(env_ratio: str | None) -> float:
    """Check the value of the similarity ratio.

    If the passed ratio is ``None`` then the default value of 0. is returned.

    Args:
        env_ratio: The raw value of the ratio from the environment variable.

    Returns:
        The value of the ratio.

    Raises:
        ValueError: If the ratio cannot be determined or has a bad value.
    """
    if env_ratio is None:
        return 0.0
    try:
        ratio = float(env_ratio)
    except ValueError:
        msg = (
            "The docstring inheritance similarity ratio cannot be determined from "
            f"'{env_ratio}'."
        )
        raise ValueError(msg) from None
    if not (0.0 <= ratio <= 1.0):
        msg = "The docstring inheritance similarity ratio must be in [0,1]."
        raise ValueError(msg)
    return ratio


class DocstringInheritanceWarning(UserWarning):
    """A warning for docstring inheritance."""


class BaseDocstringInheritor:
    """Base class for inheriting a docstring."""

    MISSING_ARG_DESCRIPTION: ClassVar[str] = "The description is missing."
    """The fall back description stub for a method argument without a description."""

    _MISSING_ARG_TEXT: ClassVar[str]
    """The actual formatted text bound to a missing method argument."""

    _DOCSTRING_PARSER: ClassVar[type[BaseDocstringParser]]
    """The docstring parser."""

    _DOCSTRING_RENDERER: ClassVar[type[BaseDocstringRenderer]]
    """The docstring renderer."""

    __child_func: Callable[..., Any]
    """The function or method to inherit the docstrings of."""

    __similarity_ratio: ClassVar[float] = get_similarity_ratio(
        os.environ.get("DOCSTRING_INHERITANCE_SIMILARITY_RATIO")
    )
    """The similarity ratio for comparing child to parent docstrings."""

    def __init__(
        self,
        child_func: Callable[..., Any],
    ) -> None:
        self.__child_func = child_func

    @classmethod
    def inherit(
        cls,
        parent_doc: str | None,
        child_func: Callable[..., Any],
    ) -> None:
        """
        Args:
            parent_doc: The docstring of the parent.
            child_func: The child function which docstring inherit from the parent.
        """  # noqa: D205, D212
        if parent_doc is not None:
            cls(child_func)._inherit(parent_doc)

    def _inherit(self, parent_doc: str) -> None:
        """Inherit the docstrings of a class.

        Args:
            parent_doc: The docstring of the parent.
        """
        parse = self._DOCSTRING_PARSER.parse
        parent_sections = parse(parent_doc)
        child_sections = parse(self.__child_func.__doc__)
        self._warn_similar_sections(parent_sections, child_sections)
        self._inherit_sections(
            parent_sections,
            child_sections,
        )
        # Get the original function eventually behind decorators.
        unwrap(self.__child_func).__doc__ = self._DOCSTRING_RENDERER.render(
            child_sections
        )

    def _warn_similar_sections(
        self,
        parent_sections: SectionsType | dict[str, str],
        child_sections: SectionsType | dict[str, str],
        super_section_name: str = "",
    ) -> None:
        """Issue a warning when the parent and child sections are similar.

        Args:
            parent_sections: The parent sections.
            child_sections: The child sections.
            super_section_name: The name of the parent section.
        """
        if self.__similarity_ratio == 0.0:
            return

        for section_name, child_section in child_sections.items():
            parent_section = parent_sections.get(section_name)
            if parent_section is None:
                continue

            # TODO: add Raises section?
            if section_name in self._DOCSTRING_PARSER.SECTION_NAMES_WITH_ITEMS:
                self._warn_similar_sections(
                    cast(Dict[str, str], parent_section),
                    cast(Dict[str, str], child_section),
                    super_section_name=section_name,
                )
            else:
                self._warn_similar_section(
                    cast(str, parent_section),
                    cast(str, child_section),
                    super_section_name,
                    section_name,
                )

    def _warn_similar_section(
        self,
        parent_doc: str,
        child_doc: str,
        super_section_name: str,
        section_name: str,
    ) -> None:
        """Issue a warning when the parent and child docs are similar.

        Args:
            parent_doc: The parent documentation.
            child_doc: The child documentation.
            super_section_name: The name of the parent section.
            section_name: The name of the section.
        """
        ratio = difflib.SequenceMatcher(None, parent_doc, child_doc).ratio()
        if ratio >= self.__similarity_ratio:
            if super_section_name:
                parent_doc = f"{super_section_name}: {parent_doc}"
                child_doc = f"{super_section_name}: {child_doc}"
            msg = (
                f"the docstrings have a similarity ratio of {ratio}, "
                f"the parent doc is\n{indent(parent_doc, ' ' * 4)}\n"
                f"the child doc is\n{indent(child_doc, ' ' * 4)}"
            )
            self._warn(section_name, msg)

    def _warn(self, section_path: str, msg: str) -> None:
        """Issue a warning.

        Args:
            section_path: The hierarchy of section names.
            msg: The warning message.
        """
        msg = f"in {self.__child_func.__qualname__}: section {section_path}: {msg}"
        module = getmodule(self.__child_func)
        module_name = module.__name__ if module is not None else None
        warnings.warn_explicit(
            msg,
            DocstringInheritanceWarning,
            getfile(self.__child_func),
            getsourcelines(self.__child_func)[1],
            module=module_name,
        )

    def _inherit_sections(
        self,
        parent_sections: SectionsType,
        child_sections: SectionsType,
    ) -> None:
        """Inherit the sections of a child from the parent sections.

        Args:
            parent_sections: The parent docstring sections.
            child_sections: The child docstring sections.
        """
        # TODO:
        # prnt_only_raises = "Raises" in parent_sections and not (
        #     "Returns" in parent_sections or "Yields" in parent_sections
        # )
        #
        # if prnt_only_raises and (
        #     "Returns" in sections or "Yields" in sections
        # ):
        #     parent_sections["Raises"] = None
        parent_section_names = parent_sections.keys()
        child_section_names = child_sections.keys()

        temp_sections = {}

        # Sections in parent but not child.
        parent_section_names_to_copy = parent_section_names - child_section_names
        for section_name in parent_section_names_to_copy:
            temp_sections[section_name] = parent_sections[section_name]

        # Remaining sections in child.
        child_sections_names_to_copy = (
            child_section_names - parent_section_names_to_copy
        )
        for section_name in child_sections_names_to_copy:
            temp_sections[section_name] = child_sections[section_name]

        # For sections with items, the sections common to parent and child are merged.
        common_section_names_with_items = (
            parent_section_names
            & child_section_names
            & self._DOCSTRING_PARSER.SECTION_NAMES_WITH_ITEMS
        )

        for section_name in common_section_names_with_items:
            temp_section_items = cast(
                Dict[str, str], parent_sections[section_name]
            ).copy()
            temp_section_items.update(
                cast(Dict[str, str], child_sections[section_name])
            )

            temp_sections[section_name] = temp_section_items

        # Args section shall be filtered.
        args_section = self._filter_args_section(
            self._MISSING_ARG_TEXT,
            cast(
                Dict[str, str],
                temp_sections.get(self._DOCSTRING_PARSER.ARGS_SECTION_NAME, {}),
            ),
            self._DOCSTRING_PARSER.ARGS_SECTION_NAME,
        )

        if args_section:
            temp_sections[self._DOCSTRING_PARSER.ARGS_SECTION_NAME] = args_section
        elif self._DOCSTRING_PARSER.ARGS_SECTION_NAME in temp_sections:
            # The args section is empty, there is nothing to document.
            del temp_sections[self._DOCSTRING_PARSER.ARGS_SECTION_NAME]

        # Reorder the standard sections.
        child_sections.clear()
        child_sections.update({
            section_name: temp_sections.pop(section_name)
            for section_name in self._DOCSTRING_PARSER.SECTION_NAMES
            if section_name in temp_sections
        })

        # Add the remaining non-standard sections.
        child_sections.update(temp_sections)

    def _filter_args_section(
        self,
        missing_arg_text: str,
        section_items: dict[str, str],
        section_name: str = "",
    ) -> dict[str, str]:
        """Filter the args section items with the args of a signature.

        The argument ``self`` is removed. The arguments are ordered according to the
        signature of ``func``. An argument of ``func`` missing in ``section_items`` gets
        a default description defined in :attr:`._MISSING_ARG_TEXT`.

        Args:
            missing_arg_text: This text for the missing arguments.
            section_name: The name of the section.
            section_items: The docstring section items.

        Returns:
            The section items filtered with the function signature.
        """
        full_arg_spec = getfullargspec(self.__child_func)

        all_args = full_arg_spec.args
        if "self" in all_args:
            all_args.remove("self")

        if full_arg_spec.varargs is not None:
            all_args += [f"*{full_arg_spec.varargs}"]

        all_args += full_arg_spec.kwonlyargs

        if full_arg_spec.varkw is not None:
            all_args += [f"**{full_arg_spec.varkw}"]

        ordered_section = {}
        for arg in all_args:
            if arg in section_items:
                doc = section_items[arg]
            else:
                doc = missing_arg_text
                self._warn(
                    section_name, f"the docstring for the argument '{arg}' is missing."
                )
            ordered_section[arg] = doc

        return ordered_section
