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
import itertools
import socket
import threading

import pydivert
import pytest

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


@pytest.fixture
def windivert_handle():
    with pydivert.WinDivert("false") as w:
        yield w


@pytest.fixture(params=list(itertools.product(
    ("ipv4", "ipv6"),
    ("tcp", "udp"),
)), ids=lambda x: ",".join(x))
def scenario(request):
    ip_version, proto = request.param

    if ip_version == "ipv4":
        atype = socket.AF_INET
        host = "127.0.0.1"
    else:
        atype = socket.AF_INET6
        host = "::1"
    if proto == "tcp":
        stype = socket.SOCK_STREAM
    else:
        stype = socket.SOCK_DGRAM

    server = socket.socket(atype, stype)
    server.bind((host, 0))
    client = socket.socket(atype, stype)
    client.bind((host, 0))

    reply = Queue()

    if proto == "tcp":
        def server_echo():
            server.listen(1)
            conn, addr = server.accept()
            conn.sendall(conn.recv(4096).upper())
            conn.close()

        def send(addr, data):
            client.connect(addr)
            client.sendall(data)
            reply.put(client.recv(4096))
    else:
        def server_echo():
            data, addr = server.recvfrom(4096)
            server.sendto(data.upper(), addr)

        def send(addr, data):
            client.sendto(data, addr)
            data, recv_addr = client.recvfrom(4096)
            assert addr[:2] == recv_addr[:2]  # only accept responses from the same host
            reply.put(data)

    server_thread = threading.Thread(target=server_echo)
    server_thread.start()

    filt = "{proto}.SrcPort == {c_port} or {proto}.SrcPort == {s_port}".format(
        proto=proto,
        c_port=client.getsockname()[1],
        s_port=server.getsockname()[1]
    )

    def send_thread(*args, **kwargs):
        threading.Thread(target=send, args=args, kwargs=kwargs).start()
        return reply

    with pydivert.WinDivert(filt) as w:
        yield client.getsockname(), server.getsockname(), w, send_thread
    client.close()
    server.close()
