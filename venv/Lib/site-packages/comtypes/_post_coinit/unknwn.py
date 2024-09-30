# https://learn.microsoft.com/en-us/windows/win32/api/unknwn/

from ctypes import byref, c_ulong, c_void_p, HRESULT, POINTER
from _ctypes import COMError

import logging
import sys
import types
from typing import ClassVar, TYPE_CHECKING, TypeVar
from typing import Optional
from typing import List, Type

from comtypes import GUID, patcher, _ole32_nohresult, com_interface_registry
from comtypes._idl_stuff import STDMETHOD
from comtypes._memberspec import ComMemberGenerator, DispMemberGenerator
from comtypes._memberspec import _ComMemberSpec, _DispMemberSpec
from comtypes._py_instance_method import instancemethod


_all_slice = slice(None, None, None)

logger = logging.getLogger(__name__)


def _shutdown(
    func=_ole32_nohresult.CoUninitialize,
    _debug=logger.debug,
    _exc_clear=getattr(sys, "exc_clear", lambda: None),
):
    # Make sure no COM pointers stay in exception frames.
    _exc_clear()
    # Sometimes, CoUninitialize, running at Python shutdown,
    # raises an exception.  We suppress this when __debug__ is
    # False.
    _debug("Calling CoUninitialize()")
    if __debug__:
        func()
    else:
        try:
            func()
        except WindowsError:
            pass
    # Set the flag which means that calling obj.Release() is no longer
    # needed.
    if _cominterface_meta is not None:
        _cominterface_meta._com_shutting_down = True
    _debug("CoUninitialize() done.")


################################################################
# The metaclasses...


class _cominterface_meta(type):
    """Metaclass for COM interfaces.  Automatically creates high level
    methods from COMMETHOD lists.
    """

    _case_insensitive_: bool
    _iid_: GUID
    _methods_: List[_ComMemberSpec]
    _disp_methods_: List[_DispMemberSpec]

    # This flag is set to True by the atexit handler which calls
    # CoUninitialize.
    _com_shutting_down = False

    # Creates also a POINTER type for the newly created class.
    def __new__(cls, name, bases, namespace):
        methods = namespace.pop("_methods_", None)
        dispmethods = namespace.pop("_disp_methods_", None)
        new_cls = type.__new__(cls, name, bases, namespace)

        if methods is not None:
            new_cls._methods_ = methods
        if dispmethods is not None:
            new_cls._disp_methods_ = dispmethods

        # If we sublass a COM interface, for example:
        #
        # class IDispatch(IUnknown):
        #     ....
        #
        # then we need to make sure that POINTER(IDispatch) is a
        # subclass of POINTER(IUnknown) because of the way ctypes
        # typechecks work.
        if bases == (object,):
            _ptr_bases = (new_cls, _compointer_base)
        else:
            _ptr_bases = (new_cls, POINTER(bases[0]))

        # The interface 'new_cls' is used as a mixin.
        p = type(_compointer_base)(
            "POINTER(%s)" % new_cls.__name__,
            _ptr_bases,
            {"__com_interface__": new_cls, "_needs_com_addref_": None},
        )

        from ctypes import _pointer_type_cache

        _pointer_type_cache[new_cls] = p

        if new_cls._case_insensitive_:

            @patcher.Patch(p)
            class CaseInsensitive(object):
                # case insensitive attributes for COM methods and properties
                def __getattr__(self, name):
                    """Implement case insensitive access to methods and properties"""
                    try:
                        fixed_name = self.__map_case__[name.lower()]
                    except KeyError:
                        raise AttributeError(name)
                    if fixed_name != name:  # prevent unbounded recursion
                        return getattr(self, fixed_name)
                    raise AttributeError(name)

                # __setattr__ is pretty heavy-weight, because it is called for
                # EVERY attribute assignment.  Settings a non-com attribute
                # through this function takes 8.6 usec, while without this
                # function it takes 0.7 sec - 12 times slower.
                #
                # How much faster would this be if implemented in C?
                def __setattr__(self, name, value):
                    """Implement case insensitive access to methods and properties"""
                    object.__setattr__(
                        self, self.__map_case__.get(name.lower(), name), value
                    )

        @patcher.Patch(POINTER(p))
        class ReferenceFix(object):
            def __setitem__(self, index, value):
                # We override the __setitem__ method of the
                # POINTER(POINTER(interface)) type, so that the COM
                # reference count is managed correctly.
                #
                # This is so that we can implement COM methods that have to
                # return COM pointers more easily and consistent.  Instead of
                # using CopyComPointer in the method implementation, we can
                # simply do:
                #
                # def GetTypeInfo(self, this, ..., pptinfo):
                #     if not pptinfo: return E_POINTER
                #     pptinfo[0] = a_com_interface_pointer
                #     return S_OK
                if index != 0:
                    # CopyComPointer, which is in _ctypes, does only
                    # handle an index of 0.  This code does what
                    # CopyComPointer should do if index != 0.
                    if bool(value):
                        value.AddRef()
                    super(POINTER(p), self).__setitem__(index, value)
                    return
                from _ctypes import CopyComPointer

                CopyComPointer(value, self)

        return new_cls

    def __setattr__(self, name, value):
        if name == "_methods_":
            # XXX I'm no longer sure why the code generator generates
            # "_methods_ = []" in the interface definition, and later
            # overrides this by "Interface._methods_ = [...]
            # assert self.__dict__.get("_methods_", None) is None
            self._make_methods(value)
            self._make_specials()
        elif name == "_disp_methods_":
            assert self.__dict__.get("_disp_methods_", None) is None
            self._make_dispmethods(value)
            self._make_specials()
        type.__setattr__(self, name, value)

    def _make_specials(self):
        # This call installs methods that forward the Python protocols
        # to COM protocols.

        def has_name(name):
            # Determine whether a property or method named 'name'
            # exists
            if self._case_insensitive_:
                return name.lower() in self.__map_case__
            return hasattr(self, name)

        # XXX These special methods should be generated by the code generator.
        if has_name("Count"):

            @patcher.Patch(self)
            class _(object):
                def __len__(self):
                    "Return the the 'self.Count' property."
                    return self.Count

        if has_name("Item"):

            @patcher.Patch(self)
            class _(object):
                # 'Item' is the 'default' value.  Make it available by
                # calling the instance (Not sure this makes sense, but
                # win32com does this also).
                def __call__(self, *args, **kw):
                    "Return 'self.Item(*args, **kw)'"
                    return self.Item(*args, **kw)

                # does this make sense? It seems that all standard typelibs I've
                # seen so far that support .Item also support ._NewEnum
                @patcher.no_replace
                def __getitem__(self, index):
                    "Return 'self.Item(index)'"
                    # Handle tuples and all-slice
                    if isinstance(index, tuple):
                        args = index
                    elif index == _all_slice:
                        args = ()
                    else:
                        args = (index,)

                    try:
                        result = self.Item(*args)
                    except COMError as err:
                        (hresult, text, details) = err.args
                        if hresult == -2147352565:  # DISP_E_BADINDEX
                            raise IndexError("invalid index")
                        else:
                            raise

                    # Note that result may be NULL COM pointer. There is no way
                    # to interpret this properly, so it is returned as-is.

                    # Hm, should we call __ctypes_from_outparam__ on the
                    # result?
                    return result

                @patcher.no_replace
                def __setitem__(self, index, value):
                    "Attempt 'self.Item[index] = value'"
                    try:
                        self.Item[index] = value
                    except COMError as err:
                        (hresult, text, details) = err.args
                        if hresult == -2147352565:  # DISP_E_BADINDEX
                            raise IndexError("invalid index")
                        else:
                            raise
                    except TypeError:
                        msg = "%r object does not support item assignment"
                        raise TypeError(msg % type(self))

        if has_name("_NewEnum"):

            @patcher.Patch(self)
            class _(object):
                def __iter__(self):
                    "Return an iterator over the _NewEnum collection."
                    # This method returns a pointer to _some_ _NewEnum interface.
                    # It relies on the fact that the code generator creates next()
                    # methods for them automatically.
                    #
                    # Better would maybe to return an object that
                    # implements the Python iterator protocol, and
                    # forwards the calls to the COM interface.
                    enum = self._NewEnum
                    if isinstance(enum, types.MethodType):
                        # _NewEnum should be a propget property, with dispid -4.
                        #
                        # Sometimes, however, it is a method.
                        enum = enum()
                    if hasattr(enum, "Next"):
                        return enum
                    # _NewEnum returns an IUnknown pointer, QueryInterface() it to
                    # IEnumVARIANT
                    from comtypes.automation import IEnumVARIANT

                    return enum.QueryInterface(IEnumVARIANT)

    def _make_case_insensitive(self):
        # The __map_case__ dictionary maps lower case names to the
        # names in the original spelling to enable case insensitive
        # method and attribute access.
        try:
            self.__dict__["__map_case__"]
        except KeyError:
            d = {}
            d.update(getattr(self, "__map_case__", {}))
            self.__map_case__ = d

    def _make_dispmethods(self, methods: List[_DispMemberSpec]) -> None:
        if self._case_insensitive_:
            self._make_case_insensitive()
        # create dispinterface methods and properties on the interface 'self'
        member_gen = DispMemberGenerator(self.__name__)
        for m in methods:
            member_gen.add(m)
        for name, func_or_prop, is_prop in member_gen.items():
            setattr(self, name, func_or_prop)
            # COM is case insensitive.
            # For a method, this is the real name.  For a property,
            # this is the name WITHOUT the _set_ or _get_ prefix.
            if self._case_insensitive_:
                self.__map_case__[name.lower()] = name
                if is_prop:
                    self.__map_case__[name[5:].lower()] = name[5:]
        for name, accessor in member_gen.properties():
            setattr(self, name, accessor)
            # COM is case insensitive
            if self._case_insensitive_:
                self.__map_case__[name.lower()] = name

    def __get_baseinterface_methodcount(self):
        "Return the number of com methods in the base interfaces"
        try:
            result = 0
            for itf in self.mro()[1:-1]:
                result += len(itf.__dict__["_methods_"])
            return result
        except KeyError as err:
            (name,) = err.args
            if name == "_methods_":
                raise TypeError("baseinterface '%s' has no _methods_" % itf.__name__)
            raise

    def _make_methods(self, methods: List[_ComMemberSpec]) -> None:
        if self._case_insensitive_:
            self._make_case_insensitive()
        # register com interface. we insist on an _iid_ in THIS class!
        try:
            iid = self.__dict__["_iid_"]
        except KeyError:
            raise AttributeError("this class must define an _iid_")
        else:
            com_interface_registry[str(iid)] = self
        # create members
        vtbl_offset = self.__get_baseinterface_methodcount()
        member_gen = ComMemberGenerator(self.__name__, vtbl_offset, self._iid_)
        # create private low level, and public high level methods
        for m in methods:
            member_gen.add(m)
        for name, func, raw_func, is_prop in member_gen.methods():
            raw_mth = instancemethod(raw_func, None, self)
            setattr(self, "_%s__com_%s" % (self.__name__, name), raw_mth)
            mth = instancemethod(func, None, self)
            if not is_prop:
                # We install the method in the class, except when it's a property.
                # And we make sure we don't overwrite a property that's already present.
                mthname = name if not hasattr(self, name) else ("_%s" % name)
                setattr(self, mthname, mth)
            # For a method, this is the real name.
            # For a property, this is the name WITHOUT the _set_ or _get_ prefix.
            if self._case_insensitive_:
                self.__map_case__[name.lower()] = name
                if is_prop:
                    self.__map_case__[name[5:].lower()] = name[5:]
        # create public properties / attribute accessors
        for name, accessor in member_gen.properties():
            # Again, we should not overwrite class attributes that are already present.
            propname = name if not hasattr(self, name) else ("_%s" % name)
            setattr(self, propname, accessor)
            # COM is case insensitive
            if self._case_insensitive_:
                self.__map_case__[name.lower()] = name


################################################################


class _compointer_meta(type(c_void_p), _cominterface_meta):
    "metaclass for COM interface pointer classes"
    # no functionality, but needed to avoid a metaclass conflict


class _compointer_base(c_void_p, metaclass=_compointer_meta):
    "base class for COM interface pointer classes"

    def __del__(self, _debug=logger.debug):
        "Release the COM refcount we own."
        if self:
            # comtypes calls CoUninitialize() when the atexit handlers
            # runs.  CoUninitialize() cleans up the COM objects that
            # are still alive. Python COM pointers may still be
            # present but we can no longer call Release() on them -
            # this may give a protection fault.  So we need the
            # _com_shutting_down flag.
            #
            if not type(self)._com_shutting_down:
                _debug("Release %s", self)
                self.Release()

    def __cmp__(self, other):
        """Compare pointers to COM interfaces."""
        # COM identity rule
        #
        # XXX To compare COM interface pointers, should we
        # automatically QueryInterface for IUnknown on both items, and
        # compare the pointer values?
        if not isinstance(other, _compointer_base):
            return 1

        # get the value property of the c_void_p baseclass, this is the pointer value
        return cmp(
            super(_compointer_base, self).value, super(_compointer_base, other).value
        )

    def __eq__(self, other):
        if not isinstance(other, _compointer_base):
            return False
        # get the value property of the c_void_p baseclass, this is the pointer value
        return (
            super(_compointer_base, self).value == super(_compointer_base, other).value
        )

    def __hash__(self):
        """Return the hash value of the pointer."""
        # hash the pointer values
        return hash(super(_compointer_base, self).value)

    # redefine the .value property; return the object itself.
    def __get_value(self):
        return self

    value = property(__get_value, doc="""Return self.""")

    def __repr__(self):
        ptr = super(_compointer_base, self).value
        return "<%s ptr=0x%x at %x>" % (self.__class__.__name__, ptr or 0, id(self))

    # This fixes the problem when there are multiple python interface types
    # wrapping the same COM interface.  This could happen because some interfaces
    # are contained in multiple typelibs.
    #
    # It also allows to pass a CoClass instance to an api
    # expecting a COM interface.
    @classmethod
    def from_param(cls, value):
        """Convert 'value' into a COM pointer to the interface.

        This method accepts a COM pointer, or a CoClass instance
        which is QueryInterface()d."""
        if value is None:
            return None
        # CLF: 2013-01-18
        # A default value of 0, meaning null, can pass through to here.
        if value == 0:
            return None
        if isinstance(value, cls):
            return value
        # multiple python interface types for the same COM interface.
        # Do we need more checks here?
        if cls._iid_ == getattr(value, "_iid_", None):
            return value
        # Accept an CoClass instance which exposes the interface required.
        try:
            table = value._com_pointers_
        except AttributeError:
            pass
        else:
            try:
                # a kind of QueryInterface
                return table[cls._iid_]
            except KeyError:
                raise TypeError("Interface %s not supported" % cls._iid_)
        return value.QueryInterface(cls.__com_interface__)


################################################################
# IUnknown, the root of all evil...

_T_IUnknown = TypeVar("_T_IUnknown", bound="IUnknown")

if TYPE_CHECKING:

    class _IUnknown_Base(c_void_p, metaclass=_cominterface_meta):  # type: ignore
        """This is workaround to avoid false-positive of static type checking.

        `IUnknown` behaves as a ctypes type, and `POINTER` can take it.
        This behavior is defined by some metaclasses in runtime.

        In runtime, this symbol in the namespace is just alias for
        `builtins.object`.
        """

        ...

else:
    _IUnknown_Base = object


class IUnknown(_IUnknown_Base, metaclass=_cominterface_meta):
    """The most basic COM interface.

    Each subclasses of IUnknown must define these class attributes:

    _iid_ - a GUID instance defining the identifier of this interface

    _methods_ - a list of methods for this interface.

    The _methods_ list must in VTable order.  Methods are specified
    with STDMETHOD or COMMETHOD calls.
    """

    _case_insensitive_: ClassVar[bool] = False
    _iid_: ClassVar[GUID] = GUID("{00000000-0000-0000-C000-000000000046}")
    _methods_: ClassVar[List[_ComMemberSpec]] = [
        STDMETHOD(HRESULT, "QueryInterface", [POINTER(GUID), POINTER(c_void_p)]),
        STDMETHOD(c_ulong, "AddRef"),
        STDMETHOD(c_ulong, "Release"),
    ]

    # NOTE: Why not `QueryInterface(T) -> _Pointer[T]`?
    # Any static type checkers is not able to provide members of `T` from `_Pointer[T]`,
    # regardless of the pointer is able to access members of contents in runtime.
    # And if `isinstance(p, POINTER(T))` is `True`, then `isinstance(p, T)` is also `True`.
    # So returning `T` is not a lie, and good way to know what members the class has.
    def QueryInterface(
        self, interface: Type[_T_IUnknown], iid: Optional[GUID] = None
    ) -> _T_IUnknown:
        """QueryInterface(interface) -> instance"""
        p = POINTER(interface)()
        if iid is None:
            iid = interface._iid_
        self.__com_QueryInterface(byref(iid), byref(p))  # type: ignore
        clsid = self.__dict__.get("__clsid")
        if clsid is not None:
            p.__dict__["__clsid"] = clsid
        return p  # type: ignore

    # these are only so that they get a docstring.
    # XXX There should be other ways to install a docstring.
    def AddRef(self) -> int:
        """Increase the internal refcount by one and return it."""
        return self.__com_AddRef()  # type: ignore

    def Release(self) -> int:
        """Decrease the internal refcount by one and return it."""
        return self.__com_Release()  # type: ignore


################################################################
