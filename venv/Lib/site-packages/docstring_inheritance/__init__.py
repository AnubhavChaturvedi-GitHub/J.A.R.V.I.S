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
"""Docstring inheritance entry point."""

from __future__ import annotations

import os
from typing import Any
from typing import Callable
from warnings import simplefilter

from .class_docstrings_inheritor import ClassDocstringsInheritor
from .class_docstrings_inheritor import DocstringInheritorClass
from .docstring_inheritors.bases.inheritor import DocstringInheritanceWarning
from .docstring_inheritors.google import GoogleDocstringInheritor
from .docstring_inheritors.numpy import NumpyDocstringInheritor


def inherit_google_docstring(
    parent_doc: str | None,
    child_func: Callable[..., Any],
) -> None:
    """Inherit the docstring in Google format of a function.

    Args:
        parent_doc: The docstring of the parent.
        child_func: The child function which docstring inherit from the parent.
    """
    return GoogleDocstringInheritor.inherit(parent_doc, child_func)


def inherit_numpy_docstring(
    parent_doc: str | None,
    child_func: Callable[..., Any],
) -> None:
    """Inherit the docstring in NumPy format of a function.

    Args:
        parent_doc: The docstring of the parent.
        child_func: The child function which docstring inherit from the parent.
    """
    return NumpyDocstringInheritor.inherit(parent_doc, child_func)


class _BaseDocstringInheritanceMeta(type):
    """Base metaclass for inheriting class docstrings."""

    def __init__(
        cls,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
        docstring_inheritor: DocstringInheritorClass,
        init_in_class: bool,
    ) -> None:
        super().__init__(class_name, class_bases, class_dict)
        if class_bases:
            ClassDocstringsInheritor.inherit_docstrings(
                cls, docstring_inheritor, init_in_class
            )


class GoogleDocstringInheritanceMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Google format."""

    def __init__(
        cls,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            GoogleDocstringInheritor,
            init_in_class=False,
        )


class GoogleDocstringInheritanceInitMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Google format with init-in-class."""

    def __init__(
        cls,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            GoogleDocstringInheritor,
            init_in_class=True,
        )


class NumpyDocstringInheritanceMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Numpy format."""

    def __init__(
        cls,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            NumpyDocstringInheritor,
            init_in_class=False,
        )


class NumpyDocstringInheritanceInitMeta(_BaseDocstringInheritanceMeta):
    """Metaclass for inheriting docstrings in Numpy format with init-in-class."""

    def __init__(
        cls,
        class_name: str,
        class_bases: tuple[type],
        class_dict: dict[str, Any],
    ) -> None:
        super().__init__(
            class_name,
            class_bases,
            class_dict,
            NumpyDocstringInheritor,
            init_in_class=True,
        )


# Ignore our warnings unless explicitly asked.
if not {
    "DOCSTRING_INHERITANCE_WARNS",
    "DOCSTRING_INHERITANCE_SIMILARITY_RATIO",
}.intersection(os.environ.keys()):
    simplefilter("ignore", DocstringInheritanceWarning)
