import atexit
import multiprocessing
import threading
import typing
from queue import Queue
from multiprocessing.connection import Listener as MPL, Client
__all__ = ['Listener', 'Sender']


class Listener:
    def __init__(self, key: str):
        pipe = r'\\.\pipe\{}'.format(key.replace("-", ""))
        print(pipe)
        self.server = MPL(pipe, family='AF_PIPE', authkey=key.encode())
        self.thread = threading.Thread(name=self.__repr__(), target=self._loop, daemon=True)
        self.callbacks = {}
        self.queue = Queue(1)
        atexit.register(self._cleanup)

    def _loop(self):
        while True:
            try:
                with self.server.accept() as con:
                    msg = con.recv()
            except multiprocessing.AuthenticationError:
                continue

            self.run_callback(self.callbacks.get(msg, lambda: print(f'no such callbacks: {msg}')))

    def run_callback(self, func: typing.Callable):
        """
        call function callback, or put it in queue
        :param func: callback's function object
        :return:
        """
        if hasattr(func, 'rimt'):  # put func to queue
            self.queue.put(func)
        else:
            func()

    def start(self):
        self.thread.start()
        print(f"Thread {self.thread.name}, {self.thread.is_alive()}")

    def _cleanup(self):
        self.server.close()


class Sender:
    def __init__(self, key: str):
        pipe = r"\\.\pipe\{}".format(key.replace("-", ""))
        connected = False
        while not connected:
            try:
                self.con = Client(pipe, family='AF_PIPE', authkey=key.encode())
                connected = True
            except multiprocessing.AuthenticationError:
                continue

    def send(self, data):
        self.con.send(data)
        self.con.close()

