# -*- coding: utf-8 -*-
# pylint: disable-all
"""
 * Copyright (C) 2023-2024 Nikita Beloglazov <nnikita.beloglazov@gmail.com>
 *
 * This file is part of github.com/NikitaBeloglazov/clipman.
 *
 * NikitaBeloglazov/clipman is free software; you can redistribute it and/or
 * modify it under the terms of the Mozilla Public License 2.0
 * published by the Mozilla Foundation.
 *
 * NikitaBeloglazov/clipman is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY.
 *
 * You should have received a copy of the Mozilla Public License 2.0
 * along with NikitaBeloglazov/clipman
 * If not, see https://mozilla.org/en-US/MPL/2.0.
- = - =

 * Module Decsription:
 Module that is responsible for supporting OS Windows

- = - =

Mostly, this code was assembled and rewriten from pieces of other code,
that was taken from StackOverflow and INSPIRED from some pypeclip code.

Some REFERENCE links
- https://stackoverflow.com/questions/42320125/python-get-file-from-clipboard-with-winapi-through-dragqueryfile-returns-nothing
- https://stackoverflow.com/questions/46132401/read-text-from-clipboard-in-windows-using-ctypes
- https://gist.github.com/MAGANER/c80d1a026aa141df1dd57c8aafe55ebc
- https://learn.microsoft.com/ru-ru/windows/win32/dataxchg/clipboard-functions
- https://github.com/asweigart/pyperclip/blob/master/src/pyperclip/__init__.py#L350 (terrible order of things)

- = -

[!!] I AM (@NikitaBeloglazov) NOT RESPONSIBLE FOR THIS PIECE OF CODE.

This functionality is provided as-is. 
If problems arise, for example, with encoding, God and your own hands will help.
Pull requests are always open. Amen. xD

- = - =

 * Raw usage (not recommended)

 - from clipman import windows
 - win = windows.WindowsClipboard() # initialize it

 - win.paste() # returns text in clipboard
 - win.copy("test text") # puts text in clipboard

"""
import contextlib
import ctypes
import time
from ctypes import c_size_t, sizeof, c_wchar_p, get_errno, c_wchar
from ctypes.wintypes import (HGLOBAL, LPVOID, DWORD, LPCSTR, INT, HWND, HINSTANCE, HMENU, BOOL, UINT, HANDLE)
from . import exceptions

class CheckedCall(object):
	def __init__(self, f):
		super(CheckedCall, self).__setattr__("f", f)

	def __call__(self, *args):
		ret = self.f(*args)
		if not ret and get_errno():
			raise exceptions.EngineError("WindowsError: Error calling " + self.f.__name__)
		return ret

	def __setattr__(self, key, value):
		setattr(self.f, key, value)


class WindowsClipboard():
	def __init__(self):
		windll = ctypes.windll
		msvcrt = ctypes.CDLL('msvcrt')

		self.safeCreateWindowExA = CheckedCall(windll.user32.CreateWindowExA)
		self.safeCreateWindowExA.argtypes = [DWORD, LPCSTR, LPCSTR, DWORD, INT, INT,
										INT, INT, HWND, HMENU, HINSTANCE, LPVOID]
		self.safeCreateWindowExA.restype = HWND

		self.safeDestroyWindow = CheckedCall(windll.user32.DestroyWindow)
		self.safeDestroyWindow.argtypes = [HWND]
		self.safeDestroyWindow.restype = BOOL

		self.OpenClipboard = windll.user32.OpenClipboard
		self.OpenClipboard.argtypes = [HWND]
		self.OpenClipboard.restype = BOOL

		self.safeCloseClipboard = CheckedCall(windll.user32.CloseClipboard)
		self.safeCloseClipboard.argtypes = []
		self.safeCloseClipboard.restype = BOOL

		self.safeEmptyClipboard = CheckedCall(windll.user32.EmptyClipboard)
		self.safeEmptyClipboard.argtypes = []
		self.safeEmptyClipboard.restype = BOOL

		self.safeGetClipboardData = CheckedCall(windll.user32.GetClipboardData)
		self.safeGetClipboardData.argtypes = [UINT]
		self.safeGetClipboardData.restype = HANDLE

		self.safeSetClipboardData = CheckedCall(windll.user32.SetClipboardData)
		self.safeSetClipboardData.argtypes = [UINT, HANDLE]
		self.safeSetClipboardData.restype = HANDLE

		self.safeGlobalAlloc = CheckedCall(windll.kernel32.GlobalAlloc)
		self.safeGlobalAlloc.argtypes = [UINT, c_size_t]
		self.safeGlobalAlloc.restype = HGLOBAL

		self.safeGlobalLock = CheckedCall(windll.kernel32.GlobalLock)
		self.safeGlobalLock.argtypes = [HGLOBAL]
		self.safeGlobalLock.restype = LPVOID

		self.safeGlobalUnlock = CheckedCall(windll.kernel32.GlobalUnlock)
		self.safeGlobalUnlock.argtypes = [HGLOBAL]
		self.safeGlobalUnlock.restype = BOOL

		self.wcslen = CheckedCall(msvcrt.wcslen)
		self.wcslen.argtypes = [c_wchar_p]
		self.wcslen.restype = UINT

		self.GMEM_MOVEABLE = 0x0002
		self.CF_UNICODETEXT = 13

	@contextlib.contextmanager
	def window(self):
		"""
		Context that provides a valid Windows hwnd.
		We really just need the hwnd, so setting "STATIC"
		as predefined lpClass is just fine.
		"""
		hwnd = self.safeCreateWindowExA(0, b"STATIC", None, 0, 0, 0, 0, 0,
								   None, None, None, None)
		try:
			yield hwnd
		finally:
			self.safeDestroyWindow(hwnd)

	@contextlib.contextmanager
	def clipboard(self, hwnd):
		"""
		Context manager that opens the clipboard and prevents
		other applications from modifying the clipboard content.
		We may not get the clipboard handle immediately because
		some other application is accessing it (?)
		We try for at least 500ms to get the clipboard.
		"""
		t = time.time() + 0.5
		success = False
		while time.time() < t:
			success = self.OpenClipboard(hwnd)
			if success:
				break
			time.sleep(0.01)
		if not success:
			raise exceptions.EngineError("WindowsError: Error calling OpenClipboard")

		try:
			yield
		finally:
			self.safeCloseClipboard()

	def copy(self, text):
		"""
		Reference: http://msdn.com/ms649016#_win32_Copying_Information_to_the_Clipboard
		"""

		text = str(text)
		#text = _stringifyText(text) # Converts non-str values to str.

		with self.window() as hwnd:
			# http://msdn.com/ms649048
			# If an application calls OpenClipboard with hwnd set to NULL,
			# EmptyClipboard sets the clipboard owner to NULL;
			# this causes SetClipboardData to fail.
			# => We need a valid hwnd to copy something.
			with self.clipboard(hwnd):
				self.safeEmptyClipboard()

				if text:
					# http://msdn.com/ms649051
					# If the hMem parameter identifies a memory object,
					# the object must have been allocated using the
					# function with the GMEM_MOVEABLE flag.
					count = self.wcslen(text) + 1
					handle = self.safeGlobalAlloc(self.GMEM_MOVEABLE,
											 count * sizeof(c_wchar))
					locked_handle = self.safeGlobalLock(handle)

					ctypes.memmove(c_wchar_p(locked_handle), c_wchar_p(text), count * sizeof(c_wchar))

					self.safeGlobalUnlock(handle)
					self.safeSetClipboardData(self.CF_UNICODETEXT, handle)

	def paste(self):
		with self.clipboard(None):
			handle = self.safeGetClipboardData(self.CF_UNICODETEXT)
			if not handle:
				# GetClipboardData may return NULL with errno == NO_ERROR
				# if the clipboard is empty.
				# (Also, it may return a handle to an empty buffer,
				# but technically that's not empty)
				return ""
			return c_wchar_p(handle).value
