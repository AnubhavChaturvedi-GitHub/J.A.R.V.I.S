# -*- coding: utf-8 -*-
# Copyright (C) 2016  Fabio Falcinelli, Maximilian Hils
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
pydivert bundles the WinDivert binaries from
https://reqrypt.org/download/WinDivert-1.3.0-WDDK.zip
"""
import functools
import os
import platform
import sys
from ctypes import (
    POINTER, GetLastError, WinError, c_uint, c_void_p, c_uint32, c_char_p, ARRAY, c_uint64, c_int16, c_int, WinDLL,
    c_uint8, windll)
from ctypes.wintypes import HANDLE

from .structs import WinDivertAddress

ERROR_IO_PENDING = 997

here = os.path.abspath(os.path.dirname(__file__))

if platform.architecture()[0] == "64bit":
    DLL_PATH = os.path.join(here, "WinDivert64.dll")
else:
    DLL_PATH = os.path.join(here, "WinDivert32.dll")


def raise_on_error(f):
    """
    This decorator throws a WinError whenever GetLastError() returns an error.
    As as special case, ERROR_IO_PENDING is ignored.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        retcode = GetLastError()
        if retcode and retcode != ERROR_IO_PENDING:
            err = WinError(code=retcode)
            windll.kernel32.SetLastError(0)  # clear error code so that we don't raise twice.
            raise err
        return result

    return wrapper


WINDIVERT_FUNCTIONS = {
    "WinDivertHelperParsePacket": [HANDLE, c_uint, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p,
                                   c_void_p, POINTER(c_uint)],
    "WinDivertHelperParseIPv4Address": [c_char_p, POINTER(c_uint32)],
    "WinDivertHelperParseIPv6Address": [c_char_p, POINTER(ARRAY(c_uint8, 16))],
    "WinDivertHelperCalcChecksums": [c_void_p, c_uint, c_uint64],
    "WinDivertHelperCheckFilter": [c_char_p, c_int, POINTER(c_char_p), POINTER(c_uint)],
    "WinDivertHelperEvalFilter": [c_char_p, c_int, c_void_p, c_uint, c_void_p],
    "WinDivertOpen": [c_char_p, c_int, c_int16, c_uint64],
    "WinDivertRecv": [HANDLE, c_void_p, c_uint, c_void_p, c_void_p],
    "WinDivertSend": [HANDLE, c_void_p, c_uint, c_void_p, c_void_p],
    "WinDivertRecvEx": [HANDLE, c_void_p, c_uint, c_uint64, c_void_p, c_void_p, c_void_p],
    "WinDivertSendEx": [HANDLE, c_void_p, c_uint, c_uint64, c_void_p, c_void_p, c_void_p],
    "WinDivertClose": [HANDLE],
    "WinDivertGetParam": [HANDLE, c_int, POINTER(c_uint64)],
    "WinDivertSetParam": [HANDLE, c_int, c_uint64],
}

_instance = None


def instance():
    global _instance
    if _instance is None:
        _instance = WinDLL(DLL_PATH)
        for funcname, argtypes in WINDIVERT_FUNCTIONS.items():
            func = getattr(_instance, funcname)
            func.argtypes = argtypes
    return _instance


# Dark magic happens below.
# On init, windivert_dll.WinDivertOpen is a proxy function that loads the DLL on the first invocation
# and then replaces all existing proxy function with direct handles to the DLL's functions.


_module = sys.modules[__name__]


def _init():
    """
    Lazy-load DLL, replace proxy functions with actual ones.
    """
    i = instance()
    for funcname in WINDIVERT_FUNCTIONS:
        func = getattr(i, funcname)
        func = raise_on_error(func)
        setattr(_module, funcname, func)


def _mkprox(funcname):
    """
    Make lazy-init proxy function.
    """

    def prox(*args, **kwargs):
        _init()
        return getattr(_module, funcname)(*args, **kwargs)

    return prox


for funcname in WINDIVERT_FUNCTIONS:
    setattr(_module, funcname, _mkprox(funcname))
