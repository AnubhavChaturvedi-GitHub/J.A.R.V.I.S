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
import socket
import struct

from pydivert.packet.header import Header
from pydivert.util import PY2, PY34, flag_property, indexbyte as i, raw_property


class IPHeader(Header):
    _src_addr = slice(0, 0)
    _dst_addr = slice(0, 0)
    _af = None

    @property
    def src_addr(self):
        """
        The packet source address.
        """
        try:
            return socket.inet_ntop(self._af, self.raw[self._src_addr].tobytes())
        except (ValueError, socket.error):
            pass

    @src_addr.setter
    def src_addr(self, val):
        self.raw[self._src_addr] = socket.inet_pton(self._af, val)

    @property
    def dst_addr(self):
        """
        The packet destination address.
        """
        try:
            return socket.inet_ntop(self._af, self.raw[self._dst_addr].tobytes())
        except (ValueError, socket.error):
            pass

    @dst_addr.setter
    def dst_addr(self, val):
        self.raw[self._dst_addr] = socket.inet_pton(self._af, val)

    @property
    def packet_len(self):
        """
        The total packet length, including *all* headers, as reported by the IP header.
        """
        raise NotImplementedError()  # pragma: no cover

    @packet_len.setter
    def packet_len(self, val):
        raise NotImplementedError()  # pragma: no cover


class IPv4Header(IPHeader):
    _src_addr = slice(12, 16)
    _dst_addr = slice(16, 20)
    _af = socket.AF_INET

    @property
    def header_len(self):
        """
        The IP header length in bytes.
        """
        return self.hdr_len * 4

    @property
    def hdr_len(self):
        """
        The header length in words of 32bit.
        """
        return i(self.raw[0]) & 0x0F

    @hdr_len.setter
    def hdr_len(self, val):
        if val < 5:
            raise ValueError("IP header length must be greater or equal than 5.")
        struct.pack_into('!B', self.raw, 0, 0x40 | val)

    packet_len = raw_property('!H', 2, docs=IPHeader.packet_len.__doc__)
    tos = raw_property('!B', 1, docs='The Type Of Service field (six-bit DiffServ field and a two-bit ECN field).')
    ident = raw_property('!H', 4, docs='The Identification field.')

    reserved = flag_property('reserved', 6, 0b10000000)
    evil = flag_property('evil', 6, 0b10000000, docs='Just an april\'s fool joke for the RESERVED flag.')
    df = flag_property('df', 6, 0b01000000)
    mf = flag_property('mf', 6, 0b00100000)

    ttl = raw_property('!B', 8, docs='The Time To Live field.')
    protocol = raw_property('!B', 9, docs='The Protocol field.')
    cksum = raw_property('!H', 10, docs='The IP header Checksum field.')

    @property
    def flags(self):
        """
        The flags field: RESERVED (the evil bit), DF (don't fragment), MF (more fragments).
        """
        return i(self.raw[6]) >> 5

    @flags.setter
    def flags(self, val):
        struct.pack_into('!B', self.raw, 6, (val << 5) | (self.frag_offset & 0xFF00))

    @property
    def frag_offset(self):
        """
        The Fragment Offset field in blocks of 8 bytes.
        """
        return struct.unpack_from("!H", self.raw, 6)[0] & 0x1FFF

    @frag_offset.setter
    def frag_offset(self, val):
        self.raw[6:8] = struct.pack("!H", (self.flags << 13) | (val & 0x1FFF))

    @property
    def dscp(self):
        """
        The Differentiated Services Code Point field (originally defined as Type of Service) also known as DiffServ.
        """
        return (i(self.raw[1]) >> 2) & 0x3F

    @dscp.setter
    def dscp(self, val):
        struct.pack_into('!B', self.raw, 1, (val << 2) | self.ecn)

    diff_serv = dscp

    @property
    def ecn(self):
        """
        The Explicit Congestion Notification field.
        """
        return i(self.raw[1]) & 0x03

    @ecn.setter
    def ecn(self, val):
        struct.pack_into('!B', self.raw, 1, (self.dscp << 2) | (val & 0x03))


class IPv6Header(IPHeader):
    _src_addr = slice(8, 24)
    _dst_addr = slice(24, 40)
    _af = socket.AF_INET6
    header_len = 40

    payload_len = raw_property('!H', 4, docs='The Payload Length field.')
    next_hdr = raw_property('!B', 6, docs='The Next Header field. Replaces the Protocol field in IPv4.')
    hop_limit = raw_property('!B', 7, docs='The Hop Limit field. Replaces the TTL field in IPv4.')

    @property
    def packet_len(self):
        return self.payload_len + self.header_len

    @packet_len.setter
    def packet_len(self, val):
        self.payload_len = val - self.header_len

    @property
    def traffic_class(self):
        """
        The Traffic Class field (six-bit DiffServ field and a two-bit ECN field).
        """
        return (struct.unpack_from('!H', self.raw, 0)[0] >> 4) & 0x00FF

    @traffic_class.setter
    def traffic_class(self, val):
        struct.pack_into('!H', self.raw, 0, 0x6000 | (val << 4) | (self.flow_label & 0x000F0000))

    @property
    def flow_label(self):
        """
        The Flow Label field.
        """
        return struct.unpack_from('!I', self.raw, 0)[0] & 0x000FFFFF

    @flow_label.setter
    def flow_label(self, val):
        struct.pack_into('!I', self.raw, 0, 0x60000000 | (self.traffic_class << 20) | (val & 0x000FFFFF))

    @property
    def diff_serv(self):
        """
        The DiffServ field.
        """
        return (self.traffic_class & 0xFC) >> 2

    @diff_serv.setter
    def diff_serv(self, val):
        self.traffic_class = self.ecn | (val << 2)

    @property
    def ecn(self):
        """
        The Explicit Congestion Notification field.
        """
        return self.traffic_class & 0x03

    @ecn.setter
    def ecn(self, val):
        self.traffic_class = (self.diff_serv << 2) | val

    if not PY2 and not PY34:
        packet_len.__doc__ = IPHeader.packet_len.__doc__
