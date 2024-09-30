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
import struct


class Header(object):
    def __init__(self, packet, start=0):
        self._packet = packet  # type: "pydivert.Packet"
        self._start = start

    @property
    def raw(self):
        """
        The raw header, possibly including payload.
        """
        return self._packet.raw[self._start:]

    @raw.setter
    def raw(self, val):
        if len(val) == len(self.raw):
            self.raw[:] = val
        else:
            self._packet.raw = memoryview(bytearray(
                self._packet.raw[:self._start].tobytes() + val
            ))
            self._packet.ip.packet_len = len(self._packet.raw)

    def __setattr__(self, key, value):
        if key in dir(self) or key in {"_packet", "_start"}:
            return super(Header, self).__setattr__(key, value)
        raise AttributeError("AttributeError: '{}' object has no attribute '{}'".format(
            type(self).__name__,
            key
        ))


class PayloadMixin(object):
    @property
    def header_len(self):
        raise NotImplementedError()  # pragma: no cover

    @property
    def payload(self):
        """
        The packet payload data.
        """
        return self.raw[self.header_len:].tobytes()

    @payload.setter
    def payload(self, val):
        if len(val) == len(self.raw) - self.header_len:
            self.raw[self.header_len:] = val
        else:
            self.raw = self.raw[:self.header_len].tobytes() + val


class PortMixin(object):
    @property
    def src_port(self):
        """
        The source port.
        """
        return struct.unpack_from("!H", self.raw, 0)[0]

    @property
    def dst_port(self):
        """
        The destination port.
        """
        return struct.unpack_from("!H", self.raw, 2)[0]

    @src_port.setter
    def src_port(self, val):
        self.raw[0:2] = struct.pack("!H", val)

    @dst_port.setter
    def dst_port(self, val):
        self.raw[2:4] = struct.pack("!H", val)
