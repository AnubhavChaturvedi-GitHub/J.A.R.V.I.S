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
from enum import IntEnum


# Divert layers.
class Layer(IntEnum):
    """
    See https://reqrypt.org/windivert-doc.html#divert_open
    """
    NETWORK = 0
    NETWORK_FORWARD = 1


# Divert Flag.
class Flag(IntEnum):
    """
    See https://reqrypt.org/windivert-doc.html#divert_open
    """
    DEFAULT = 0
    SNIFF = 1
    DROP = 2
    NO_CHECKSUM = 1024  # Deprecated since Windivert 1.2


# Divert parameters.
class Param(IntEnum):
    """
    See https://reqrypt.org/windivert-doc.html#divert_set_param
    """
    QUEUE_LEN = 0  # Packet queue length 1 < default 512 (actually 1024) < 8192
    QUEUE_TIME = 1  # Packet queue time 128 < default 512 < 2048
    QUEUE_SIZE = 2  # Packet queue size (bytes)  4096 (4KB) < default 4194304 (4MB) < 33554432 (32MB)


# Direction outbound/inbound
class Direction(IntEnum):
    """
    See https://reqrypt.org/windivert-doc.html#divert_address
    """
    OUTBOUND = 0
    INBOUND = 1


# Checksums
class CalcChecksumsOption(IntEnum):
    """
    See https://reqrypt.org/windivert-doc.html#divert_helper_calc_checksums
    """
    NO_IP_CHECKSUM = 1
    NO_ICMP_CHECKSUM = 2
    NO_ICMPV6_CHECKSUM = 4
    NO_TCP_CHECKSUM = 8
    NO_UDP_CHECKSUM = 16
    NO_REPLACE = 2048


class Protocol(IntEnum):
    """
    Transport protocol values define the layout of the header that will immediately follow the IPv4 or IPv6 header.
    See http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
    """
    HOPOPT = 0
    ICMP = 1
    TCP = 6
    UDP = 17
    ROUTING = 43
    FRAGMENT = 44
    AH = 51
    ICMPV6 = 58
    NONE = 59
    DSTOPTS = 60


IPV6_EXT_HEADERS = {
    Protocol.HOPOPT,
    Protocol.ROUTING,
    Protocol.FRAGMENT,
    Protocol.DSTOPTS,
    Protocol.AH,
}
