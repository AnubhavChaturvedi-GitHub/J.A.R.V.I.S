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
from pydivert.util import indexbyte as i, flag_property, raw_property


class TCPHeader(Header, PayloadMixin, PortMixin):
    ns = flag_property("ns", 12, 0b00000001)

    cwr = flag_property("cwr", 13, 0b10000000)
    ece = flag_property("ece", 13, 0b01000000)

    urg = flag_property("syn", 13, 0b00100000)
    ack = flag_property("ack", 13, 0b00010000)
    psh = flag_property("psh", 13, 0b00001000)
    rst = flag_property("rst", 13, 0b00000100)
    syn = flag_property("syn", 13, 0b00000010)
    fin = flag_property("fin", 13, 0b00000001)

    @property
    def header_len(self):
        """
        The TCP header length.
        """
        return self.data_offset * 4

    seq_num = raw_property('!I', 4, docs='The sequence number field.')
    ack_num = raw_property('!I', 8, docs='The acknowledgement number field.')

    window_size = raw_property('!H', 14, docs='The size of the receive window in bytes.')
    cksum = raw_property('!H', 16, docs='The TCP header checksum field.')
    urg_ptr = raw_property('!H', 18, docs='The Urgent Pointer field.')

    @property
    def data_offset(self):
        """
        The size of TCP header in 32bit words.
        """
        return i(self.raw[12]) >> 4

    @data_offset.setter
    def data_offset(self, val):
        if val < 5 or val > 15:
            raise ValueError("TCP data offset must be greater or equal than 5 and less than 15.")
        struct.pack_into('!B', self.raw, 12, (val << 4) | (self.reserved << 1) | self.ns)

    @property
    def reserved(self):
        """
        The reserved field.
        """
        return (i(self.raw[12]) >> 1) & 0x07

    @reserved.setter
    def reserved(self, val):
        struct.pack_into('!B', self.raw, 12, (self.data_offset << 4) | (val << 1) | self.ns)

    @property
    def control_bits(self):
        """
        The Control Bits field.
        """
        return struct.unpack_from('!H', self.raw, 12)[0] & 0x01FF

    @control_bits.setter
    def control_bits(self, val):
        struct.pack_into('!H', self.raw, 12, (self.data_offset << 12) | (self.reserved << 9) | (val & 0x01FF))
