import unittest as ut

from ctypes import POINTER, byref, c_bool, c_ubyte
import comtypes
import comtypes.client

comtypes.client.GetModule("portabledeviceapi.dll")
from comtypes.gen.PortableDeviceApiLib import IStream


def _create_stream() -> IStream:
    # Create an IStream
    stream = POINTER(IStream)()  # type: ignore
    comtypes._ole32.CreateStreamOnHGlobal(None, c_bool(True), byref(stream))
    return stream  # type: ignore


class Test_RemoteWrite(ut.TestCase):
    def test_RemoteWrite(self):
        stream = _create_stream()
        test_data = "Some data".encode("utf-8")
        pv = (c_ubyte * len(test_data)).from_buffer(bytearray(test_data))

        written = stream.RemoteWrite(pv, len(test_data))

        # Verification
        self.assertEqual(written, len(test_data))


class Test_RemoteRead(ut.TestCase):
    def test_RemoteRead(self):
        stream = _create_stream()
        test_data = "Some data".encode("utf-8")
        pv = (c_ubyte * len(test_data)).from_buffer(bytearray(test_data))
        stream.RemoteWrite(pv, len(test_data))

        # Make sure the data actually gets written before trying to read back
        stream.Commit(0)
        # Move the stream back to the beginning
        STREAM_SEEK_SET = 0
        stream.RemoteSeek(0, STREAM_SEEK_SET)

        buffer_size = 1024

        read_buffer, data_read = stream.RemoteRead(buffer_size)

        # Verification
        self.assertEqual(data_read, len(test_data))
        self.assertEqual(bytearray(read_buffer)[0:data_read], test_data)


if __name__ == "__main__":
    ut.main()
