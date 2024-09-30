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
 Module that is responsible for supporting KDE Plasma 5-6 natively through DBUS

- = - =

 * Raw usage (not recommended)

 - from clipman import kde

 - kde.get_clipboard() # returns text in clipboard
 - kde.set_clipboard("test text") # puts text in clipboard

"""

import asyncio

from . import exceptions

# - = INIT - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - =
try:
	from dbus_next.aio import MessageBus
	from dbus_next import Message, DBusError
except ImportError as e:
	error_message = "Please install dbus-next package.\n - Via your system package manager. Possible package name: \"python3-dbus_next\" or \"python3-dbus-next\"\n - Or via PIP: \"pip3 install dbus-next\""
	raise exceptions.AdditionalDependenciesRequired(error_message) from e
# - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - =

async def dbus_call(message, timeout=10):
	""" A function that makes a call with timeout to the dbus address passed as an argument. """
	# Connecting to SessionBus
	bus = await MessageBus().connect()

	try:
		# Send message with timeout
		reply = await asyncio.wait_for(bus.call(message), timeout=timeout)

		# Parse response
		return reply.body[0] if reply.body else None
	except asyncio.TimeoutError as e:
		raise exceptions.EngineTimeoutExpired(f"Dbus call try timed out after {timeout} seconds") from e
	except DBusError as e:
		raise exceptions.UnknownError("Some DBus error occurred! See details above") from e
	finally:
		bus.disconnect()

def set_clipboard(text):
	""" Sets text to clipboard """
	message = Message(
		destination="org.kde.klipper",
		path="/klipper",
		interface="org.kde.klipper.klipper",
		member="setClipboardContents",
		body=[text],
		signature='s'
	)
	return asyncio.run(dbus_call(message))

def get_clipboard():
	""" Get content in clipboard """
	message = Message(
		destination="org.kde.klipper",
		path="/klipper",
		interface="org.kde.klipper.klipper",
		member="getClipboardContents",
	)
	return asyncio.run(dbus_call(message))
