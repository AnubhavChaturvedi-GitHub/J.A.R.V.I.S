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
"""Classes for inheriting Google docstrings."""

from __future__ import annotations

import textwrap
from typing import ClassVar

from .bases import SUMMARY_SECTION_NAME
from .bases import SubSectionType
from .bases.inheritor import BaseDocstringInheritor
from .bases.parser import BaseDocstringParser
from .bases.parser import NoSectionFound
from .bases.renderer import BaseDocstringRenderer


class DocstringRenderer(BaseDocstringRenderer):
    """The renderer for Google docstrings."""

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
        section_body = textwrap.indent(section_body, " " * 4)
        return f"{section_name}:\n{section_body}"


class DocstringParser(BaseDocstringParser):
    """The parser for Google docstrings."""

    ARGS_SECTION_NAME: ClassVar[str] = "Args"
    SECTION_NAMES: ClassVar[list[str]] = list(BaseDocstringParser.SECTION_NAMES)
    SECTION_NAMES[1] = ARGS_SECTION_NAME
    SECTION_NAMES_WITH_ITEMS: ClassVar[set[str]] = {
        ARGS_SECTION_NAME,
        "Attributes",
        "Methods",
    }

    @classmethod
    def _get_section_body(
        cls,
        reversed_section_body_lines: list[str],
    ) -> str:
        return textwrap.dedent(super()._get_section_body(reversed_section_body_lines))

    @classmethod
    def _parse_one_section(
        cls,
        line1: str,
        line2_rstripped: str,
        reversed_section_body_lines: list[str],
    ) -> tuple[str, str]:
        # See https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings  # noqa: E501
        # The parsing of a section is complete when the first line line1 has:
        # - no leading blank spaces,
        # - ends with :,
        # - has a second line indented by at least 2 blank spaces,
        # - has a section name.
        line1_rstripped = line1.rstrip()
        if (
            not line1_rstripped.startswith(" ")
            and line1_rstripped.endswith(":")
            and line2_rstripped.startswith("  ")
            and line1_rstripped[:-1].strip() in cls.SECTION_NAMES
        ):
            reversed_section_body_lines += [line2_rstripped]
            return line1_rstripped.rstrip(" :"), cls._get_section_body(
                reversed_section_body_lines
            )
        raise NoSectionFound


class GoogleDocstringInheritor(BaseDocstringInheritor):
    """The inheritor for Google docstrings."""

    _MISSING_ARG_TEXT = f": {BaseDocstringInheritor.MISSING_ARG_DESCRIPTION}"
    _DOCSTRING_PARSER = DocstringParser
    _DOCSTRING_RENDERER = DocstringRenderer
