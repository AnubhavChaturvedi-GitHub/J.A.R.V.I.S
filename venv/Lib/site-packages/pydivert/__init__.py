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
import sys as _sys

from .consts import Layer, Flag, Param, CalcChecksumsOption, Direction, Protocol
from .packet import Packet
from .windivert import WinDivert

__author__ = 'fabio'
__version__ = '2.1.0'

if _sys.version_info < (3, 4):
    # add socket.inet_pton on Python < 3.4
    import win_inet_pton as _win_inet_pton

    assert _win_inet_pton

__all__ = [
    "WinDivert",
    "Packet",
    "Layer", "Flag", "Param", "CalcChecksumsOption", "Direction", "Protocol",
]
