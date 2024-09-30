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

import inspect
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Literal

from griffe import Alias
from griffe import Attribute
from griffe import Class
from griffe import Docstring
from griffe import Extension
from griffe import Inspector
from griffe import Object
from griffe import ObjectNode
from griffe import Visitor
from griffe import dynamic_import
from griffe import get_logger

if TYPE_CHECKING:
    import ast

    from griffe import Parser

_logger = get_logger(__name__)


class DocstringInheritance(Extension):
    """Inherit docstrings when the package docstring-inheritance is used."""

    __parser: Literal["google", "numpy", "sphinx"] | Parser | None = None
    """The docstring parser."""

    __parser_options: ClassVar[dict[str, Any]] = {}
    """The docstring parser options."""

    def on_class_members(  # noqa: D102
        self,
        *,
        node: ast.AST | ObjectNode,
        cls: Class,
        agent: Visitor | Inspector,
        **kwargs: Any,
    ) -> None:
        if isinstance(node, ObjectNode):
            # Skip runtime objects, their docstrings are already OK.
            return

        runtime_cls = self.__import_dynamically(cls)

        if not self.__has_docstring_inheritance(runtime_cls):
            return

        # Inherit the class docstring.
        self.__set_docstring(cls, runtime_cls)

        # Inherit the methods docstrings.
        for member in cls.members.values():
            if not isinstance(member, Attribute):
                runtime_obj = self.__import_dynamically(member)
                self.__set_docstring(member, runtime_obj)

    @staticmethod
    def __import_dynamically(obj: Object | Alias) -> Any:
        """Import dynamically and return an object."""
        try:
            return dynamic_import(obj.path)
        except ImportError:
            _logger.debug("Could not get dynamic docstring for %s", obj.path)

    @classmethod
    def __set_docstring(cls, obj: Object | Alias, runtime_obj: Any) -> None:
        """Set the docstring from a runtime object.

        Args:
            obj: The griffe object.
            runtime_obj: The runtime object.
        """
        if runtime_obj is None:
            return

        try:
            docstring = runtime_obj.__doc__
        except AttributeError:
            _logger.debug("Object %s does not have a __doc__ attribute", obj.path)
            return

        if docstring is None:
            return

        # Update the object instance with the evaluated docstring.
        if obj.docstring:
            obj.docstring.value = inspect.cleandoc(docstring)
        else:
            assert not isinstance(obj, Alias)
            cls.__find_parser(obj)
            obj.docstring = Docstring(
                docstring,
                parent=obj,
                parser=cls.__parser,
                parser_options=cls.__parser_options,
            )

    @staticmethod
    def __has_docstring_inheritance(cls: type[Any]) -> bool:
        """Return whether a class has docstring inheritance."""
        for base in cls.__class__.__mro__:
            if base.__name__.endswith("DocstringInheritanceMeta"):
                return True
        return False

    @classmethod
    def __find_parser(cls, obj: Object) -> None:
        """Search a docstring parser recursively from an object parents."""
        if cls.__parser is not None:
            return

        parent = obj.parent
        if parent is None:
            msg = f"Cannot find a parent of the object {obj}"
            raise RuntimeError(msg)

        if parent.docstring is None:
            msg = f"Cannot find a docstring for the parent of the object {obj}"
            raise RuntimeError(msg)

        parser = parent.docstring.parser

        if parser is None:
            cls.__find_parser(parent)
        else:
            cls.__parser = parser
            cls.__parser_options = parent.docstring.parser_options
