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
from pydivert.packet.header import Header, PayloadMixin
from pydivert.util import indexbyte as i, raw_property


class ICMPHeader(Header, PayloadMixin):
    header_len = 4

    @property
    def type(self):
        """
        The ICMP message type.
        """
        return i(self.raw[0])

    @type.setter
    def type(self, val):
        self.raw[0] = i(val)

    @property
    def code(self):
        """
        The ICMP message code.
        """
        return i(self.raw[1])

    @code.setter
    def code(self, val):
        self.raw[1] = i(val)

    cksum = raw_property('!H', 2, docs='The ICMP header checksum field.')


class ICMPv4Header(ICMPHeader):
    pass


class ICMPv6Header(ICMPHeader):
    pass
