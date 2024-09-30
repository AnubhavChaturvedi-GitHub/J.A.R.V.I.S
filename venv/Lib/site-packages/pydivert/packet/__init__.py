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
import ctypes
import pprint
import socket

from pydivert import windivert_dll
from pydivert.consts import Direction, IPV6_EXT_HEADERS, Protocol, Layer
from pydivert.packet.header import Header
from pydivert.packet.icmp import ICMPv4Header, ICMPv6Header
from pydivert.packet.ip import IPv4Header, IPv6Header
from pydivert.packet.tcp import TCPHeader
from pydivert.packet.udp import UDPHeader
from pydivert.util import cached_property, indexbyte as i, PY2


class Packet(object):
    """
    A single packet, possibly including an IP header, a TCP/UDP header and a payload.
    Creation of packets is cheap, parsing is done on first attribute access.
    """

    def __init__(self, raw, interface, direction):
        if isinstance(raw, bytes):
            raw = memoryview(bytearray(raw))
        self.raw = raw  # type: memoryview
        self.interface = interface
        self.direction = direction

    def __repr__(self):
        def dump(x):
            if isinstance(x, Header) or isinstance(x, Packet):
                d = {}
                for k in dir(x):
                    v = getattr(x, k)
                    if k.startswith("_") or callable(v):
                        continue
                    if k in {"address_family", "protocol", "ip", "icmp"}:
                        continue
                    if k == "payload" and v and len(v) > 20:
                        v = v[:20] + b"..."
                    d[k] = dump(v)
                if isinstance(x, Packet):
                    return pprint.pformat(d)
                return d
            return x

        return "Packet({})".format(dump(self))

    @property
    def is_outbound(self):
        """
        Indicates if the packet is outbound.
        Convenience method for ``.direction``.
        """
        return self.direction == Direction.OUTBOUND

    @property
    def is_inbound(self):
        """
        Indicates if the packet is inbound.
        Convenience method for ``.direction``.
        """
        return self.direction == Direction.INBOUND

    @property
    def is_loopback(self):
        """
        - True, if the packet is on the loopback interface.
        - False, otherwise.
        """
        return self.interface[0] == 1

    @cached_property
    def address_family(self):
        """
        The packet address family:
            - socket.AF_INET, if IPv4
            - socket.AF_INET6, if IPv6
            - None, otherwise.
        """
        if len(self.raw) >= 20:
            v = i(self.raw[0]) >> 4
            if v == 4:
                return socket.AF_INET
            if v == 6:
                return socket.AF_INET6

    @cached_property
    def protocol(self):
        """
        - | A (ipproto, proto_start) tuple.
          | ``ipproto`` is the IP protocol in use, e.g. Protocol.TCP or Protocol.UDP.
          | ``proto_start`` denotes the beginning of the protocol data.
          | If the packet does not match our expectations, both ipproto and proto_start are None.
        """
        if self.address_family == socket.AF_INET:
            proto = i(self.raw[9])
            start = (i(self.raw[0]) & 0b1111) * 4
        elif self.address_family == socket.AF_INET6:
            proto = i(self.raw[6])

            # skip over well-known ipv6 headers
            start = 40
            while proto in IPV6_EXT_HEADERS:
                if start >= len(self.raw):
                    # less than two bytes left
                    start = None
                    proto = None
                    break
                if proto == Protocol.FRAGMENT:
                    hdrlen = 8
                elif proto == Protocol.AH:
                    hdrlen = (i(self.raw[start + 1]) + 2) * 4
                else:
                    # Protocol.HOPOPT, Protocol.DSTOPTS, Protocol.ROUTING
                    hdrlen = (i(self.raw[start + 1]) + 1) * 8
                proto = i(self.raw[start])
                start += hdrlen
        else:
            start = None
            proto = None

        out_of_bounds = (
            (proto == Protocol.TCP and start + 20 > len(self.raw)) or
            (proto == Protocol.UDP and start + 8 > len(self.raw)) or
            (proto in {Protocol.ICMP, Protocol.ICMPV6} and start + 4 > len(self.raw))
        )
        if out_of_bounds:
            # special-case tcp/udp so that we can rely on .protocol for the port properties.
            start = None
            proto = None

        return proto, start

    @cached_property
    def ipv4(self):
        """
        - An IPv4Header instance, if the packet is valid IPv4.
        - None, otherwise.
        """
        if self.address_family == socket.AF_INET:
            return IPv4Header(self)

    @cached_property
    def ipv6(self):
        """
        - An IPv6Header instance, if the packet is valid IPv6.
        - None, otherwise.
        """
        if self.address_family == socket.AF_INET6:
            return IPv6Header(self)

    @cached_property
    def ip(self):
        """
        - An IPHeader instance, if the packet is valid IPv4 or IPv6.
        - None, otherwise.
        """
        return self.ipv4 or self.ipv6

    @cached_property
    def icmpv4(self):
        """
        - An ICMPv4Header instance, if the packet is valid ICMPv4.
        - None, otherwise.
        """
        ipproto, proto_start = self.protocol
        if ipproto == Protocol.ICMP:
            return ICMPv4Header(self, proto_start)

    @cached_property
    def icmpv6(self):
        """
        - An ICMPv6Header instance, if the packet is valid ICMPv6.
        - None, otherwise.
        """
        ipproto, proto_start = self.protocol
        if ipproto == Protocol.ICMPV6:
            return ICMPv6Header(self, proto_start)

    @cached_property
    def icmp(self):
        """
        - An ICMPHeader instance, if the packet is valid ICMPv4 or ICMPv6.
        - None, otherwise.
        """
        return self.icmpv4 or self.icmpv6

    @cached_property
    def tcp(self):
        """
        - An TCPHeader instance, if the packet is valid TCP.
        - None, otherwise.
        """
        ipproto, proto_start = self.protocol
        if ipproto == Protocol.TCP:
            return TCPHeader(self, proto_start)

    @cached_property
    def udp(self):
        """
        - An TCPHeader instance, if the packet is valid UDP.
        - None, otherwise.
        """
        ipproto, proto_start = self.protocol
        if ipproto == Protocol.UDP:
            return UDPHeader(self, proto_start)

    @cached_property
    def _port(self):
        """header that implements PortMixin"""
        return self.tcp or self.udp

    @cached_property
    def _payload(self):
        """header that implements PayloadMixin"""
        return self.tcp or self.udp or self.icmpv4 or self.icmpv6

    @property
    def src_addr(self):
        """
        - The source address, if the packet is valid IPv4 or IPv6.
        - None, otherwise.
        """
        if self.ip:
            return self.ip.src_addr

    @src_addr.setter
    def src_addr(self, val):
        self.ip.src_addr = val

    @property
    def dst_addr(self):
        """
        - The destination address, if the packet is valid IPv4 or IPv6.
        - None, otherwise.
        """
        if self.ip:
            return self.ip.dst_addr

    @dst_addr.setter
    def dst_addr(self, val):
        self.ip.dst_addr = val

    @property
    def src_port(self):
        """
        - The source port, if the packet is valid TCP or UDP.
        - None, otherwise.
        """
        if self._port:
            return self._port.src_port

    @src_port.setter
    def src_port(self, val):
        self._port.src_port = val

    @property
    def dst_port(self):
        """
        - The destination port, if the packet is valid TCP or UDP.
        - None, otherwise.
        """
        if self._port:
            return self._port.dst_port

    @dst_port.setter
    def dst_port(self, val):
        self._port.dst_port = val

    @property
    def payload(self):
        """
        - The payload, if the packet is valid TCP, UDP, ICMP or ICMPv6.
        - None, otherwise.
        """
        if self._payload:
            return self._payload.payload

    @payload.setter
    def payload(self, val):
        self._payload.payload = val

    def recalculate_checksums(self, flags=0):
        """
        (Re)calculates the checksum for any IPv4/ICMP/ICMPv6/TCP/UDP checksum present in the given packet.
        Individual checksum calculations may be disabled via the appropriate flag.
        Typically this function should be invoked on a modified packet before it is injected with WinDivert.send().
        Returns the number of checksums calculated.

        See: https://reqrypt.org/windivert-doc.html#divert_helper_calc_checksums
        """
        buff, buff_ = self.__to_buffers()
        num = windivert_dll.WinDivertHelperCalcChecksums(ctypes.byref(buff_), len(self.raw), flags)
        if PY2:
            self.raw = memoryview(buff)[:len(self.raw)]
        return num

    def __to_buffers(self):
        buff = bytearray(self.raw.tobytes()) if PY2 else self.raw.obj
        return buff, (ctypes.c_char * len(self.raw)).from_buffer(buff)

    @property
    def wd_addr(self):
        """
        Gets the interface and direction as a `WINDIVERT_ADDRESS` structure.
        :return: The `WINDIVERT_ADDRESS` structure.
        """
        address = windivert_dll.WinDivertAddress()
        address.IfIdx, address.SubIfIdx = self.interface
        address.Direction = self.direction
        return address

    def matches(self, filter, layer=Layer.NETWORK):
        """
        Evaluates the packet against the given packet filter string.

        The remapped function is::

            BOOL WinDivertHelperEvalFilter(
                __in const char *filter,
                __in WINDIVERT_LAYER layer,
                __in PVOID pPacket,
                __in UINT packetLen,
                __in PWINDIVERT_ADDRESS pAddr
            );

        See: https://reqrypt.org/windivert-doc.html#divert_helper_eval_filter

        :param filter: The filter string.
        :param layer: The network layer.
        :return: True if the packet matches, and False otherwise.
        """
        buff, buff_ = self.__to_buffers()
        return windivert_dll.WinDivertHelperEvalFilter(filter.encode(), layer, ctypes.byref(buff_), len(self.raw),
                                                       ctypes.byref(self.wd_addr))
