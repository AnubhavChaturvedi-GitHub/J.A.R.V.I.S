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
"""Base class for docstrings parsers."""

from __future__ import annotations

import inspect
import operator
import re
import sys
from abc import ABC
from abc import abstractmethod
from itertools import dropwhile
from itertools import tee
from typing import TYPE_CHECKING
from typing import ClassVar

from . import SUMMARY_SECTION_NAME

if TYPE_CHECKING:
    from . import SectionsType

if sys.version_info >= (3, 10):  # pragma: >=3.10 cover
    from itertools import pairwise
else:  # pragma: <3.10 cover
    # See https://docs.python.org/3/library/itertools.html#itertools.pairwise
    def pairwise(iterable):  # noqa: D103
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


class NoSectionFound(BaseException):
    """Exception raised when no section has been found when parsing one section."""


class BaseDocstringParser(ABC):
    """The base class for docstring parsers."""

    SECTION_NAMES: ClassVar[list[str]] = [
        SUMMARY_SECTION_NAME,
        "Parameters",
        "Returns",
        "Yields",
        "Receives",
        "Other Parameters",
        "Attributes",
        "Methods",
        "Raises",
        "Warns",
        "Warnings",
        "See Also",
        "Notes",
        "References",
        "Examples",
    ]
    """Names of the sections."""

    ARGS_SECTION_NAME: ClassVar[str]
    """The name of the section with methods arguments."""

    SECTION_NAMES_WITH_ITEMS: ClassVar[set[str]]
    """The Names of all the sections with items, including `ARGS_SECTION_NAME`."""

    _SECTION_ITEMS_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"(\**\w+)(.*?)(?:$|(?=\n\**\w+))", flags=re.DOTALL
    )

    @classmethod
    @abstractmethod
    def _parse_one_section(
        cls,
        line1: str,
        line2_rstripped: str,
        reversed_section_body_lines: list[str],
    ) -> tuple[str, str]:
        """Parse the name and body of a docstring section.

        It does not parse section_items items.

        Returns:
            The name and docstring body parts of a section.

        Raises:
            NoSectionFound: If no section is found.
        """

    @classmethod
    def _get_section_body(
        cls,
        reversed_section_body_lines: list[str],
    ) -> str:
        """Return the docstring of a section.

        Args:
            reversed_section_body_lines: The lines of docstrings in reversed order.

        Returns:
            The docstring of a section.
        """
        reversed_section_body_lines = list(
            dropwhile(operator.not_, reversed_section_body_lines)
        )
        reversed_section_body_lines.reverse()
        return "\n".join(reversed_section_body_lines)

    @classmethod
    def parse(cls, docstring: str | None) -> SectionsType:
        """Parse the sections of a docstring.

        Args:
            docstring: The docstring to parse.

        Returns:
            The parsed sections.
        """
        if not docstring:
            return {}

        lines = inspect.cleandoc(docstring).splitlines()

        # It seems easier to work reversed.
        lines_pairs = iter(pairwise(reversed(lines)))

        reversed_section_body_lines: list[str] = []
        reversed_sections: SectionsType = {}

        # Iterate 2 lines at a time to look for the section_items headers
        # that are underlined.
        for line2, line1 in lines_pairs:
            line2_rstripped = line2.rstrip()

            try:
                section_name, section_body = cls._parse_one_section(
                    line1, line2_rstripped, reversed_section_body_lines
                )
            except NoSectionFound:
                pass
            else:
                if section_name in cls.SECTION_NAMES_WITH_ITEMS:
                    reversed_sections[section_name] = cls._parse_section_items(
                        section_body
                    )
                else:
                    reversed_sections[section_name] = section_body

                # We took into account line1 in addition to line2,
                # we no longer need to process line1.
                try:
                    next(lines_pairs)
                except StopIteration:
                    # The docstring has no summary section_items.
                    has_summary = False
                    break

                reversed_section_body_lines = []
                continue

            reversed_section_body_lines += [line2_rstripped]
        else:
            has_summary = True

        sections: SectionsType = {}

        if has_summary:
            # Add the missing first line because it is not taken into account
            # by the above loop.
            reversed_section_body_lines += [lines[0]]

            # Add the section_items with the short and extended summaries.
            sections[SUMMARY_SECTION_NAME] = cls._get_section_body(
                reversed_section_body_lines
            )

        for section_name_, section_body_ in reversed(reversed_sections.items()):
            sections[section_name_] = section_body_

        return sections

    @classmethod
    def _parse_section_items(cls, section_body: str) -> dict[str, str]:
        """Parse the section items for numpy and google docstrings.

        Args:
            section_body: The body of a docstring section.

        Returns:
            The parsed section body.
        """
        return dict(cls._SECTION_ITEMS_REGEX.findall(section_body))
