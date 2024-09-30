import array
import datetime
import unittest
from ctypes import POINTER, PyDLL, byref, c_long, py_object
from ctypes.wintypes import BOOL
from decimal import Decimal

from comtypes import BSTR, IUnknown
from comtypes._safearray import SafeArrayGetVartype
from comtypes.automation import (
    VARIANT,
    VARIANT_BOOL,
    VT_ARRAY,
    VT_BSTR,
    VT_I4,
    VT_R4,
    VT_R8,
    VT_VARIANT,
    _midlSAFEARRAY,
)
from comtypes.safearray import safearray_as_ndarray
from comtypes.test import is_resource_enabled
from comtypes.test.find_memleak import find_memleak


def get_array(sa):
    """Get an array from a safe array type"""
    with safearray_as_ndarray:
        return sa[0]


def com_refcnt(o):
    """Return the COM refcount of an interface pointer"""
    import gc

    gc.collect()
    gc.collect()
    o.AddRef()
    return o.Release()


class VariantTestCase(unittest.TestCase):
    @unittest.skip("This fails with a memory leak.  Figure out if false positive.")
    def test_VARIANT_array(self):
        v = VARIANT()
        v.value = ((1, 2, 3), ("foo", "bar", None))
        self.assertEqual(v.vt, VT_ARRAY | VT_VARIANT)
        self.assertEqual(v.value, ((1, 2, 3), ("foo", "bar", None)))

        def func():
            VARIANT((1, 2, 3), ("foo", "bar", None))

        bytes = find_memleak(func)
        self.assertFalse(bytes, "Leaks %d bytes" % bytes)

    @unittest.skip("This fails with a memory leak.  Figure out if false positive.")
    def test_double_array(self):
        a = array.array("d", (3.14, 2.78))
        v = VARIANT(a)
        self.assertEqual(v.vt, VT_ARRAY | VT_R8)
        self.assertEqual(tuple(a.tolist()), v.value)

        def func():
            VARIANT(array.array("d", (3.14, 2.78)))

        bytes = find_memleak(func)
        self.assertFalse(bytes, "Leaks %d bytes" % bytes)

    def test_float_array(self):
        a = array.array("f", (3.14, 2.78))
        v = VARIANT(a)
        self.assertEqual(v.vt, VT_ARRAY | VT_R4)
        self.assertEqual(tuple(a.tolist()), v.value)

    def test_2dim_array(self):
        data = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12))
        v = VARIANT(data)
        self.assertEqual(v.value, data)


class SafeArrayTestCase(unittest.TestCase):
    def test_equality(self):
        a = _midlSAFEARRAY(c_long)
        b = _midlSAFEARRAY(c_long)
        self.assertTrue(a is b)

        c = _midlSAFEARRAY(BSTR)
        d = _midlSAFEARRAY(BSTR)
        self.assertTrue(c is d)

        self.assertNotEqual(a, c)

        # XXX remove:
        self.assertEqual((a._itemtype_, a._vartype_), (c_long, VT_I4))
        self.assertEqual((c._itemtype_, c._vartype_), (BSTR, VT_BSTR))

    def test_VT_BSTR(self):
        t = _midlSAFEARRAY(BSTR)

        sa = t.from_param(["a", "b", "c"])
        self.assertEqual(sa[0], ("a", "b", "c"))
        self.assertEqual(SafeArrayGetVartype(sa), VT_BSTR)

    @unittest.skip("This fails with a memory leak.  Figure out if false positive.")
    def test_VT_BSTR_leaks(self):
        sb = _midlSAFEARRAY(BSTR)

        def doit():
            sb.from_param(["foo", "bar"])

        bytes = find_memleak(doit)
        self.assertFalse(bytes, "Leaks %d bytes" % bytes)

    @unittest.skip("This fails with a memory leak.  Figure out if false positive.")
    def test_VT_I4_leaks(self):
        sa = _midlSAFEARRAY(c_long)

        def doit():
            sa.from_param([1, 2, 3, 4, 5, 6])

        bytes = find_memleak(doit)
        self.assertFalse(bytes, "Leaks %d bytes" % bytes)

    def test_VT_I4(self):
        t = _midlSAFEARRAY(c_long)

        sa = t.from_param([11, 22, 33])

        self.assertEqual(sa[0], (11, 22, 33))

        self.assertEqual(SafeArrayGetVartype(sa), VT_I4)

        # TypeError: len() of unsized object
        self.assertRaises(TypeError, lambda: t.from_param(object()))

    def test_VT_VARIANT(self):
        t = _midlSAFEARRAY(VARIANT)

        now = datetime.datetime.now()
        sa = t.from_param([11, "22", None, True, now, Decimal("3.14")])
        self.assertEqual(sa[0], (11, "22", None, True, now, Decimal("3.14")))

        self.assertEqual(SafeArrayGetVartype(sa), VT_VARIANT)

    def test_VT_BOOL(self):
        t = _midlSAFEARRAY(VARIANT_BOOL)

        sa = t.from_param([True, False, True, False])
        self.assertEqual(sa[0], (True, False, True, False))

    def test_VT_UNKNOWN_1(self):
        a = _midlSAFEARRAY(POINTER(IUnknown))
        t = _midlSAFEARRAY(POINTER(IUnknown))
        self.assertTrue(a is t)

        from comtypes.typeinfo import CreateTypeLib

        # will never be saved to disk
        punk = CreateTypeLib("spam").QueryInterface(IUnknown)

        # initial refcount
        initial = com_refcnt(punk)

        # This should increase the refcount by 1
        sa = t.from_param([punk])
        self.assertEqual(initial + 1, com_refcnt(punk))

        # Unpacking the array must not change the refcount, and must
        # return an equal object.
        self.assertEqual((punk,), sa[0])
        self.assertEqual(initial + 1, com_refcnt(punk))

        del sa
        self.assertEqual(initial, com_refcnt(punk))

        sa = t.from_param([None])
        self.assertEqual((POINTER(IUnknown)(),), sa[0])

    def test_VT_UNKNOWN_multi(self):
        a = _midlSAFEARRAY(POINTER(IUnknown))
        t = _midlSAFEARRAY(POINTER(IUnknown))
        self.assertTrue(a is t)

        from comtypes.typeinfo import CreateTypeLib

        # will never be saved to disk
        punk = CreateTypeLib("spam").QueryInterface(IUnknown)

        # initial refcount
        initial = com_refcnt(punk)

        # This should increase the refcount by 4
        sa = t.from_param((punk,) * 4)
        self.assertEqual(initial + 4, com_refcnt(punk))

        # Unpacking the array must not change the refcount, and must
        # return an equal object.
        self.assertEqual((punk,) * 4, sa[0])
        self.assertEqual(initial + 4, com_refcnt(punk))

        del sa
        self.assertEqual(initial, com_refcnt(punk))

        # This should increase the refcount by 2
        sa = t.from_param((punk, None, punk, None))
        self.assertEqual(initial + 2, com_refcnt(punk))

        null = POINTER(IUnknown)()
        self.assertEqual((punk, null, punk, null), sa[0])

        del sa
        self.assertEqual(initial, com_refcnt(punk))

        # repeat same test, with 2 different com pointers

        plib = CreateTypeLib("foo")
        a, b = com_refcnt(plib), com_refcnt(punk)
        sa = t.from_param([plib, punk, plib])

        ####        self.failUnlessEqual((plib, punk, plib), sa[0])
        self.assertEqual((a + 2, b + 1), (com_refcnt(plib), com_refcnt(punk)))

        del sa
        self.assertEqual((a, b), (com_refcnt(plib), com_refcnt(punk)))

    @unittest.skip(
        "This fails with a 'library not registered' error.  Need to figure out how to "
        "register TestComServerLib (without admin if possible)."
    )
    def test_UDT(self):
        from comtypes.gen.TestComServerLib import MYCOLOR

        t = _midlSAFEARRAY(MYCOLOR)
        self.assertTrue(t is _midlSAFEARRAY(MYCOLOR))

        sa = t.from_param([MYCOLOR(0, 0, 0), MYCOLOR(1, 2, 3)])

        self.assertEqual(
            [(x.red, x.green, x.blue) for x in sa[0]],
            [(0.0, 0.0, 0.0), (1.0, 2.0, 3.0)],
        )

        def doit():
            t.from_param([MYCOLOR(0, 0, 0), MYCOLOR(1, 2, 3)])

        bytes = find_memleak(doit)
        self.assertFalse(bytes, "Leaks %d bytes" % bytes)


if is_resource_enabled("pythoncom"):
    try:
        import pythoncom
    except ImportError:
        # pywin32 not installed...
        pass
    else:
        # pywin32 is available.  The pythoncom dll contains two handy
        # exported functions that allow to create a VARIANT from a Python
        # object, also a function that unpacks a VARIANT into a Python
        # object.
        #
        # This allows us to create und unpack SAFEARRAY instances
        # contained in VARIANTs, and check for consistency with the
        # comtypes code.

        _dll = PyDLL(pythoncom.__file__)

        # c:/sf/pywin32/com/win32com/src/oleargs.cpp 213
        # PyObject *PyCom_PyObjectFromVariant(const VARIANT *var)
        unpack = _dll.PyCom_PyObjectFromVariant
        unpack.restype = py_object
        unpack.argtypes = (POINTER(VARIANT),)

        # c:/sf/pywin32/com/win32com/src/oleargs.cpp 54
        # BOOL PyCom_VariantFromPyObject(PyObject *obj, VARIANT *var)
        _pack = _dll.PyCom_VariantFromPyObject
        _pack.argtypes = py_object, POINTER(VARIANT)
        _pack.restype = BOOL

        def pack(obj):
            var = VARIANT()
            _pack(obj, byref(var))
            return var

        class PyWinTest(unittest.TestCase):
            def test_1dim(self):
                data = (1, 2, 3)
                variant = pack(data)
                self.assertEqual(variant.value, data)
                self.assertEqual(unpack(variant), data)

            def test_2dim(self):
                data = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
                variant = pack(data)
                self.assertEqual(variant.value, data)
                self.assertEqual(unpack(variant), data)

            def test_3dim(self):
                data = (((1, 2), (3, 4), (5, 6)), ((7, 8), (9, 10), (11, 12)))
                variant = pack(data)
                self.assertEqual(variant.value, data)
                self.assertEqual(unpack(variant), data)

            def test_4dim(self):
                data = (
                    (((1, 2), (3, 4)), ((5, 6), (7, 8))),
                    (((9, 10), (11, 12)), ((13, 14), (15, 16))),
                )
                variant = pack(data)
                self.assertEqual(variant.value, data)
                self.assertEqual(unpack(variant), data)


if __name__ == "__main__":
    unittest.main()
