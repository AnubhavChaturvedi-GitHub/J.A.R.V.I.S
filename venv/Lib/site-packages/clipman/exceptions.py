# -*- coding: utf-8 -*-
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
 Module that contain exceptions.

- = - =
 * Usage:
 If you want to catch specific error, use name of error, as example:
 - except exceptions.NoEnginesFoundError:

 If you want to catch all errors, use ClipmanBaseException.
 - except exceptions.ClipmanBaseException:
"""

class ClipmanBaseException(Exception):
	""" Used for catch all exceptions in module """

class NoInitializationError(ClipmanBaseException):
	""" Called if dev don't called clipman.init() """
	# - = - = - = - = - = - = - ↓ Set default error message ↓
	def __init__(self, message="Initialization was not been performed or it failed! Call initialization first: clipman.init()"):
		super().__init__(message)

class UnsupportedError(ClipmanBaseException):
	""" Called if OS or graphical backend is unsupported """

class TextNotSpecified(ClipmanBaseException):
	""" Called if call("copy") not specified text to paste """

# - = - = -
class NoEnginesFoundError(ClipmanBaseException):
	""" If usable clipboard engines not found on target OS """
class AdditionalDependenciesRequired(ClipmanBaseException):
    """ If additional dependencies are required for target OS """
# - = - = -

class EngineError(ClipmanBaseException):
	""" If there is an error raised by clipboard engine """

class EngineTimeoutExpired(ClipmanBaseException):
	""" Called if clipboard engine calling times out. Mostly made for termux-clipboard-get """

class UnknownError(ClipmanBaseException):
	""" Unknown Error """
