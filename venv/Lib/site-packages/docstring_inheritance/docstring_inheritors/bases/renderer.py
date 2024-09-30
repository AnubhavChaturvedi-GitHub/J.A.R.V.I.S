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
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from . import SUMMARY_SECTION_NAME
from . import SubSectionType

if TYPE_CHECKING:
    from . import SectionsType


class BaseDocstringRenderer(ABC):
    """The docstring base class renderer."""

    @classmethod
    def render(cls, sections: SectionsType) -> str:
        """Render a docstring.

        Args:
            sections: The docstring sections to render.

        Returns:
            The rendered docstring.
        """
        if not sections:
            return ""

        rendered_sections = []

        for section_name, section_body in sections.items():
            rendered_sections += [cls._render_section(section_name, section_body)]

        rendered = "\n\n".join(rendered_sections)

        if SUMMARY_SECTION_NAME not in sections:
            # Add an empty summary line,
            # Sphinx will not behave correctly otherwise with the Google format.
            return "\n" + rendered

        return rendered

    @staticmethod
    @abstractmethod
    def _render_section(
        section_name: str,
        section_body: SubSectionType,
    ) -> str:
        """Return a rendered docstring section.

        Args:
            section_name: The name of a docstring section.
            section_body: The body of a docstring section.

        Returns:
            The rendered docstring.
        """
