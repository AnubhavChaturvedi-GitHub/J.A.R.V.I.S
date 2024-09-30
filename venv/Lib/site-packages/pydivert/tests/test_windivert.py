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
import time

import pytest
from pydivert.consts import Param
from pydivert.windivert import WinDivert

from .fixtures import scenario, windivert_handle as w

assert scenario, w  # keep fixtures


def test_open():
    w = WinDivert("false")
    w.open()
    assert w.is_open
    w.close()
    assert not w.is_open

    with w:
        # open a second one.
        with WinDivert("false") as w2:
            assert w2.is_open

        assert w.is_open
        assert "open" in repr(w)

        with pytest.raises(RuntimeError):
            w.open()

    assert not w.is_open
    assert "closed" in repr(w)

    with pytest.raises(RuntimeError):
        w.recv()
    with pytest.raises(RuntimeError):
        w.close()


def test_register():
    if WinDivert.is_registered():
        WinDivert.unregister()
    while WinDivert.is_registered():
        time.sleep(0.01)  # pragma: no cover
    assert not WinDivert.is_registered()
    WinDivert.register()
    assert WinDivert.is_registered()


def test_unregister():
    w = WinDivert("false")
    w.open()
    WinDivert.unregister()
    time.sleep(0.1)
    assert WinDivert.is_registered()
    w.close()
    # may not trigger immediately.
    while WinDivert.is_registered():
        time.sleep(0.01)  # pragma: no cover


class TestParams(object):
    def test_queue_time_range(self, w):
        """
        Tests setting the minimum value for queue time.
        From docs: 128 < default 512 < 2048
        """
        def_range = (128, 512, 2048)
        for value in def_range:
            w.set_param(Param.QUEUE_TIME, value)
            assert value == w.get_param(Param.QUEUE_TIME)

    def test_queue_len_range(self, w):
        """
        Tests setting the minimum value for queue length.
        From docs: 1< default 512 <8192
        """
        for value in (1, 512, 8192):
            w.set_param(Param.QUEUE_LEN, value)
            assert value == w.get_param(Param.QUEUE_LEN)

    def test_invalid_set(self, w):
        with pytest.raises(Exception):
            w.set_param(42, 43)

    def test_invalid_get(self, w):
        with pytest.raises(Exception):
            w.get_param(42)


def test_echo(scenario):
    client_addr, server_addr, w, send = scenario
    w = w  # type: WinDivert
    reply = send(server_addr, b"echo")

    for p in w:
        assert p.is_loopback
        assert p.is_outbound
        w.send(p)
        done = (
            p.udp and p.dst_port == client_addr[1]
            or
            p.tcp and p.tcp.fin
        )
        if done:
            break

    assert reply.get() == b"ECHO"


def test_divert(scenario):
    client_addr, server_addr, w, send = scenario
    w = w  # type: WinDivert
    target = (server_addr[0], 80)
    reply = send(target, b"echo")
    for p in w:
        if p.src_port == client_addr[1]:
            p.dst_port = server_addr[1]
        if p.src_port == server_addr[1]:
            p.src_port = target[1]
        w.send(p)

        done = (
            p.udp and p.dst_port == client_addr[1]
            or
            p.tcp and p.tcp.fin
        )
        if done:
            break

    assert reply.get() == b"ECHO"


def test_modify_payload(scenario):
    client_addr, server_addr, w, send = scenario
    w = w  # type: WinDivert
    reply = send(server_addr, b"echo")

    for p in w:
        p.payload = p.payload.replace(b"echo", b"test").replace(b"TEST", b"ECHO")
        w.send(p)

        done = (
            p.udp and p.dst_port == client_addr[1]
            or
            p.tcp and p.tcp.fin
        )
        if done:
            break
    assert reply.get() == b"ECHO"


def test_packet_cutoff(scenario):
    client_addr, server_addr, w, send = scenario
    w = w  # type: WinDivert
    reply = send(server_addr, b"a" * 1000)

    cutoff = None
    while True:
        p = w.recv(500)
        if p.ip.packet_len != len(p.raw):
            assert cutoff is None
            cutoff = p.ip.packet_len - len(p.raw)
            p.ip.packet_len = len(p.raw)  # fix length
            if p.udp:
                p.udp.payload_len = len(p.payload)
        w.send(p)
        done = (
            p.udp and p.dst_port == client_addr[1]
            or
            p.tcp and p.tcp.fin
        )
        if done:
            break
    assert cutoff
    assert reply.get() == b"A" * (1000 - cutoff)

def test_check_filter():

    res, pos, msg = WinDivert.check_filter('true')
    assert res
    assert pos == 0
    assert msg is not None
    res, pos, msg = WinDivert.check_filter('something wrong here')
    assert not res
    assert pos == 0
    assert msg is not None
    res, pos, msg = WinDivert.check_filter('outbound and something wrong here')
    assert not res
    assert pos == 13
