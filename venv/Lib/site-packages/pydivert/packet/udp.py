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

from pydivert.packet.header import Header, PayloadMixin, PortMixin
from pydivert.util import PY2, PY34, raw_property


class UDPHeader(Header, PayloadMixin, PortMixin):
    header_len = 8

    @property
    def payload(self):
        return PayloadMixin.payload.fget(self)

    @payload.setter
    def payload(self, val):
        PayloadMixin.payload.fset(self, val)
        self.payload_len = len(val)

    if not PY2 and not PY34:
        payload.__doc__ = PayloadMixin.payload.__doc__

    @property
    def payload_len(self):
        return struct.unpack_from("!H", self.raw, 4)[0] - 8

    @payload_len.setter
    def payload_len(self, val):
        self.raw[4:6] = struct.pack("!H", val + 8)

    cksum = raw_property('!H', 6, docs='The UDP header checksum field.')
