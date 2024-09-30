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
"""Docstrings inheritor class."""

from __future__ import annotations

from types import FunctionType
from types import WrapperDescriptorType
from typing import Any
from typing import Callable
from typing import Type

from docstring_inheritance.docstring_inheritors.bases.inheritor import (
    BaseDocstringInheritor,
)

DocstringInheritorClass = Type[BaseDocstringInheritor]


class ClassDocstringsInheritor:
    """A class for inheriting class docstrings."""

    _cls: type
    """The class to process."""

    _docstring_inheritor: DocstringInheritorClass
    """The docstring inheritor."""

    _init_in_class: bool
    """Whether the ``__init__`` arguments documentation is in the class docstring."""

    __mro_classes: list[type]
    """The MRO classes."""

    def __init__(
        self,
        cls: type,
        docstring_inheritor: DocstringInheritorClass,
        init_in_class: bool,
    ) -> None:
        """
        Args:
            cls: The class to process.
            docstring_inheritor: The docstring inheritor.
            init_in_class: Whether the ``__init__`` arguments documentation is in the
                class docstring.
        """  # noqa: D205, D212
        # Remove the new class itself and the object class from the mro,
        # object's docstrings have no interest.
        self.__mro_classes = cls.mro()[1:-1]
        self._cls = cls
        self._docstring_inheritor = docstring_inheritor
        self._init_in_class = init_in_class

    @classmethod
    def inherit_docstrings(
        cls,
        class_: type,
        docstring_inheritor: DocstringInheritorClass,
        init_in_class: bool,
    ) -> None:
        """Inherit all the docstrings of the class.

        Args:
            class_: The class to process.
            docstring_inheritor: The docstring inheritor.
            init_in_class: Whether the ``__init__`` arguments documentation is in the
                class docstring.
        """
        inheritor = cls(class_, docstring_inheritor, init_in_class)
        inheritor._inherit_attrs_docstrings()
        inheritor._inherit_class_docstring()

    def _inherit_class_docstring(
        self,
    ) -> None:
        """Create the inherited docstring for the class docstring."""
        func = None
        old_init_doc = None
        init_doc_changed = False

        if self._init_in_class:
            init_method: Callable[..., None] = self._cls.__init__  # type: ignore
            # Ignore the case when __init__ is from object since there is no docstring
            # and its __doc__ cannot be assigned.
            if not isinstance(init_method, WrapperDescriptorType):
                old_init_doc = init_method.__doc__
                init_method.__doc__ = self._cls.__doc__
                func = init_method
                init_doc_changed = True

        if func is None:
            func = self._create_dummy_func_with_doc(self._cls.__doc__)

        for parent_cls in self.__mro_classes:
            # As opposed to the attribute inheritance, and following the way a class is
            # assembled by type(), the docstring of a class is the combination of the
            # docstrings of its parents.
            self._docstring_inheritor.inherit(parent_cls.__doc__, func)

        self._cls.__doc__ = func.__doc__

        if self._init_in_class and init_doc_changed:
            init_method.__doc__ = old_init_doc

    def _inherit_attrs_docstrings(
        self,
    ) -> None:
        """Create the inherited docstrings for the class attributes."""
        for attr_name, attr in self._cls.__dict__.items():
            if not isinstance(attr, FunctionType):
                continue

            for parent_cls in self.__mro_classes:
                parent_method = getattr(parent_cls, attr_name, None)
                if parent_method is not None:
                    parent_doc = parent_method.__doc__
                    if parent_doc is not None:
                        self._docstring_inheritor.inherit(parent_doc, attr)
                        # As opposed to the class docstring inheritance, and following
                        # the MRO for methods,
                        # we inherit only from the first found parent.
                        break
                    # TODO: else WARN that no docstring is defined and
                    # none can be inherited.

    @staticmethod
    def _create_dummy_func_with_doc(docstring: str | None) -> Callable[..., Any]:
        """Create a dummy function with a given docstring.

        Args:
            docstring: The docstring to be assigned.

        Returns:
            The function with the given docstring.
        """

        def func() -> None:  # pragma: no cover
            pass

        func.__doc__ = docstring
        return func
