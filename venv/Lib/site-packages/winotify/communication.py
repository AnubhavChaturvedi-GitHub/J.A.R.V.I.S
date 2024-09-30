import os
import atexit
import threading
import time
import typing

__all__ = ['Listener', 'Sender']


class Listener:
    def __init__(self, file):
        self.file = file
        print(self.file)
        self.thread = threading.Thread(name=self.__repr__(), target=self._loop, daemon=True)
        self.callbacks = {}
        if not os.path.exists(self.file):
            open(self.file, 'w').close()

        atexit.register(self._cleanup)

    def _loop(self):
        while True:
            data = open(self.file).read()
            if data:
                print(data)
                self.run_callback(self.callbacks.get(data, lambda: print(f"No callback named {data}")))
                with open(self.file, 'w') as pipe:  # clear
                    pipe.write('')
            else:
                time.sleep(.1)

    def run_callback(self, func: typing.Callable):
        """
        call function callback, this method can be overridden
        :param func: callback's function object
        :return:
        """
        return func()

    def start(self):
        self.thread.start()

    def _cleanup(self):
        os.remove(self.file)


class Sender:
    def __init__(self, file):
        self.file = file

    def send(self, data):
        with open(self.file, 'r+') as pipe:
            if len(pipe.read()) > 0:
                return
            pipe.write(data)

