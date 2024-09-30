from comtypes._memberspec import _ComMemberSpec, _DispMemberSpec, _resolve_argspec


class helpstring(str):
    "Specifies the helpstring for a COM method or property."


class defaultvalue(object):
    "Specifies the default value for parameters marked optional."

    def __init__(self, value):
        self.value = value


class dispid(int):
    "Specifies the DISPID of a method or property."


# XXX STDMETHOD, COMMETHOD, DISPMETHOD, and DISPPROPERTY should return
# instances with more methods or properties, and should not behave as an unpackable.


def STDMETHOD(restype, name, argtypes=()) -> _ComMemberSpec:
    "Specifies a COM method slot without idlflags"
    return _ComMemberSpec(restype, name, argtypes, None, (), None)


def DISPMETHOD(idlflags, restype, name, *argspec) -> _DispMemberSpec:
    "Specifies a method of a dispinterface"
    return _DispMemberSpec("DISPMETHOD", name, tuple(idlflags), restype, argspec)


def DISPPROPERTY(idlflags, proptype, name) -> _DispMemberSpec:
    "Specifies a property of a dispinterface"
    return _DispMemberSpec("DISPPROPERTY", name, tuple(idlflags), proptype, ())


# tuple(idlflags) is for the method itself: (dispid, 'readonly')

# sample generated code:
#     DISPPROPERTY([5, 'readonly'], OLE_YSIZE_HIMETRIC, 'Height'),
#     DISPMETHOD(
#         [6], None, 'Render', ([], c_int, 'hdc'), ([], c_int, 'x'), ([], c_int, 'y')
#     )


def COMMETHOD(idlflags, restype, methodname, *argspec) -> _ComMemberSpec:
    """Specifies a COM method slot with idlflags.

    XXX should explain the sematics of the arguments.
    """
    # collect all helpstring instances
    # We should suppress docstrings when Python is started with -OO
    # join them together(does this make sense?) and replace by None if empty.
    helptext = "".join(t for t in idlflags if isinstance(t, helpstring)) or None
    paramflags, argtypes = _resolve_argspec(argspec)
    if "propget" in idlflags:
        name = "_get_%s" % methodname
    elif "propput" in idlflags:
        name = "_set_%s" % methodname
    elif "propputref" in idlflags:
        name = "_setref_%s" % methodname
    else:
        name = methodname
    return _ComMemberSpec(
        restype, name, argtypes, paramflags, tuple(idlflags), helptext
    )
