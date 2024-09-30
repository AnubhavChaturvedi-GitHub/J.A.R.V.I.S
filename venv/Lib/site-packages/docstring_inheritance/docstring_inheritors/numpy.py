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
"""Classes for inheriting NumPy docstrings."""

from __future__ import annotations

from typing import ClassVar

from .bases import SUMMARY_SECTION_NAME
from .bases import SubSectionType
from .bases.inheritor import BaseDocstringInheritor
from .bases.parser import BaseDocstringParser
from .bases.parser import NoSectionFound
from .bases.renderer import BaseDocstringRenderer


class DocstringRenderer(BaseDocstringRenderer):
    """The renderer for NumPy docstrings."""

    @staticmethod
    def _render_section(
        section_name: str,
        section_body: SubSectionType,
    ) -> str:
        if section_name is SUMMARY_SECTION_NAME:
            assert isinstance(section_body, str)
            return section_body
        if isinstance(section_body, dict):
            section_body = "\n".join(
                f"{key}{value}" for key, value in section_body.items()
            )
        return f"{section_name}\n{'-' * len(section_name)}\n{section_body}"


class DocstringParser(BaseDocstringParser):
    """The parser for NumPy docstrings."""

    ARGS_SECTION_NAME: ClassVar[str] = "Parameters"

    SECTION_NAMES_WITH_ITEMS: ClassVar[set[str]] = {
        ARGS_SECTION_NAME,
        "Other Parameters",
        "Attributes",
        "Methods",
    }

    @classmethod
    def _parse_one_section(
        cls,
        line1: str,
        line2_rstripped: str,
        reversed_section_body_lines: list[str],
    ) -> tuple[str, str]:
        # See https://github.com/numpy/numpydoc/blob/d85f54ea342c1d223374343be88da94ce9f58dec/numpydoc/docscrape.py#L179  # noqa: E501
        if len(line2_rstripped) >= 3 and (set(line2_rstripped) in ({"-"}, {"="})):
            line1s = line1.rstrip()
            min_line_length = len(line1s)
            if line2_rstripped.startswith((
                "-" * min_line_length,
                "=" * min_line_length,
            )):
                return line1s, cls._get_section_body(reversed_section_body_lines)
        raise NoSectionFound


class NumpyDocstringInheritor(BaseDocstringInheritor):
    """The inheritor for NumPy docstrings."""

    _MISSING_ARG_TEXT = f"\n    {BaseDocstringInheritor.MISSING_ARG_DESCRIPTION}"
    _DOCSTRING_PARSER = DocstringParser
    _DOCSTRING_RENDERER = DocstringRenderer
