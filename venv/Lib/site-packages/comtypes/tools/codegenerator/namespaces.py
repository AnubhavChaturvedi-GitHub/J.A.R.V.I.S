import textwrap
from typing import Dict, List, Set, Tuple


class ImportedNamespaces(object):
    def __init__(self):
        self.data = {}

    def add(self, name1, name2=None, symbols=None):
        """Adds a namespace will be imported.

        Examples:
            >>> imports = ImportedNamespaces()
            >>> imports.add('datetime')
            >>> imports.add('ctypes', '*')
            >>> imports.add('decimal', 'Decimal')
            >>> imports.add('GUID', symbols={'GUID': 'comtypes'})
            >>> for name in ('COMMETHOD', 'DISPMETHOD', 'IUnknown', 'dispid',
            ...              'CoClass', 'BSTR', 'DISPPROPERTY'):
            ...     imports.add('comtypes', name)
            >>> imports.add('ctypes.wintypes')
            >>> print(imports.getvalue())
            from ctypes import *
            import datetime
            from decimal import Decimal
            from comtypes import (
                BSTR, CoClass, COMMETHOD, dispid, DISPMETHOD, DISPPROPERTY, GUID,
                IUnknown
            )
            import ctypes.wintypes
            >>> assert imports.get_symbols() == {
            ...     'Decimal', 'GUID', 'COMMETHOD', 'DISPMETHOD', 'IUnknown',
            ...     'dispid', 'CoClass', 'BSTR', 'DISPPROPERTY'
            ... }
        """
        if name2 is None:
            import_ = name1
            if not symbols:
                self.data[import_] = None
                return
            from_ = symbols[import_]
        else:
            from_, import_ = name1, name2
        self.data[import_] = from_

    def __contains__(self, item):
        """Returns item has already added.

        Examples:
            >>> imports = ImportedNamespaces()
            >>> imports.add('datetime')
            >>> imports.add('ctypes', '*')
            >>> 'datetime' in imports
            True
            >>> ('ctypes', '*') in imports
            True
            >>> 'os' in imports
            False
            >>> 'ctypes' in imports
            False
            >>> ('ctypes', 'c_int') in imports
            False
        """
        if isinstance(item, tuple):
            from_, import_ = item
        else:
            from_, import_ = None, item
        if import_ in self.data:
            return self.data[import_] == from_
        return False

    def get_symbols(self) -> Set[str]:
        names = set()
        for key, val in self.data.items():
            if val is None or key == "*":
                continue
            names.add(key)
        return names

    def _make_line(self, from_, imports):
        import_ = ", ".join(imports)
        code = "from %s import %s" % (from_, import_)
        if len(code) <= 80:
            return code
        wrapper = textwrap.TextWrapper(
            subsequent_indent="    ", initial_indent="    ", break_long_words=False
        )
        import_ = "\n".join(wrapper.wrap(import_))
        code = "from %s import (\n%s\n)" % (from_, import_)
        return code

    def getvalue(self):
        ns = {}
        lines = []
        for key, val in self.data.items():
            if val is None:
                ns[key] = val
            elif key == "*":
                lines.append("from %s import *" % val)
            else:
                ns.setdefault(val, set()).add(key)
        for key, val in ns.items():
            if val is None:
                lines.append("import %s" % key)
            else:
                names = sorted(val, key=lambda s: s.lower())
                lines.append(self._make_line(key, names))
        return "\n".join(lines)


class DeclaredNamespaces(object):
    def __init__(self):
        self.data = {}

    def add(self, alias, definition, comment=None):
        """Adds a namespace will be declared.

        Examples:
            >>> declarations = DeclaredNamespaces()
            >>> declarations.add('STRING', 'c_char_p')
            >>> declarations.add('_lcid', '0', 'change this if required')
            >>> print(declarations.getvalue())
            STRING = c_char_p
            _lcid = 0  # change this if required
            >>> assert declarations.get_symbols() == {
            ...     'STRING', '_lcid'
            ... }
        """
        self.data[(alias, definition)] = comment

    def get_symbols(self) -> Set[str]:
        names = set()
        for alias, _ in self.data.keys():
            names.add(alias)
        return names

    def getvalue(self):
        lines = []
        for (alias, definition), comment in self.data.items():
            code = "%s = %s" % (alias, definition)
            if comment:
                code = code + "  # %s" % comment
            lines.append(code)
        return "\n".join(lines)


class EnumerationNamespaces(object):
    def __init__(self):
        self.data: Dict[str, List[Tuple[str, int]]] = {}

    def add(self, enum_name: str, member_name: str, value: int) -> None:
        """Adds a namespace will be enumeration and its member.

        Examples:
            <BLANKLINE> is necessary for doctest
            >>> enums = EnumerationNamespaces()
            >>> assert not enums
            >>> enums.add('Foo', 'ham', 1)
            >>> assert enums
            >>> enums.add('Foo', 'spam', 2)
            >>> enums.add('Bar', 'bacon', 3)
            >>> assert 'Foo' in enums
            >>> assert 'Baz' not in enums
            >>> print(enums.to_intflags())
            class Foo(IntFlag):
                ham = 1
                spam = 2
            <BLANKLINE>
            <BLANKLINE>
            class Bar(IntFlag):
                bacon = 3
            >>> print(enums.to_constants())
            # values for enumeration 'Foo'
            ham = 1
            spam = 2
            Foo = c_int  # enum
            <BLANKLINE>
            # values for enumeration 'Bar'
            bacon = 3
            Bar = c_int  # enum
        """
        self.data.setdefault(enum_name, []).append((member_name, value))

    def __contains__(self, item: str) -> bool:
        return item in self.data

    def __bool__(self) -> bool:
        return bool(self.data)

    def get_symbols(self) -> Set[str]:
        return set(self.data)

    def to_constants(self) -> str:
        blocks = []
        for enum_name, enum_members in self.data.items():
            lines = []
            lines.append(f"# values for enumeration '{enum_name}'")
            for n, v in enum_members:
                lines.append(f"{n} = {v}")
            lines.append(f"{enum_name} = c_int  # enum")
            blocks.append("\n".join(lines))
        return "\n\n".join(blocks)

    def to_intflags(self) -> str:
        blocks = []
        for enum_name, enum_members in self.data.items():
            lines = []
            lines.append(f"class {enum_name}(IntFlag):")
            for member_name, value in enum_members:
                lines.append(f"    {member_name} = {value}")
            blocks.append("\n".join(lines))
        return "\n\n\n".join(blocks)
