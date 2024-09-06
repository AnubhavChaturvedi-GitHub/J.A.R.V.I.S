import pyaudio
import struct
import math

INITIAL_TAP_THRESHOLD = 0.7222
FORMAT = pyaudio.paInt16
SHORT_NORMALIZE = (1.0 / 32768.0)
CHANNELS = 3
RATE = 44100
INPUT_BLOCK_TIME = 0.01
INPUT_FRAMES_PER_BLOCK = int(RATE * INPUT_BLOCK_TIME)
OVERSENSITIVE = 9.0 / INPUT_BLOCK_TIME
UNDERSENSITIVE = 10.0 / INPUT_BLOCK_TIME
MAX_TAP_BLOCKS = 0.15 / INPUT_BLOCK_TIME
REQUIRED_CLAPS = 2  # Adjust this value as needed


class TapTester(object):

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS + 1
        self.quietcount = 0
        self.errorcount = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None
        for i in range(self.pa.get_device_count()):
            devinfo = self.pa.get_device_info_by_index(i)
            for keyword in ["mic", "input"]:
                if keyword in devinfo["name"].lower():
                    device_index = i
                    return device_index

        if device_index is None:
            print("No preferred input found; using default input device.")

        return device_index

    def open_mic_stream(self):
        device_index = self.find_input_device()

        stream = self.pa.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              input_device_index=device_index,
                              frames_per_buffer=INPUT_FRAMES_PER_BLOCK)

        return stream

    @staticmethod
    def get_rms(block):
        count = len(block) / 2
        format = "%dh" % count
        shorts = struct.unpack(format, block)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n

        return math.sqrt(sum_squares / count)

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError as e:
            self.errorcount += 1
            print("(%d) Error recording: %s" % (self.errorcount, e))
            self.noisycount = 5
            return

        amplitude = self.get_rms(block)

        if amplitude > self.tap_threshold:
            self.quietcount = 2
            self.noisycount += 1
            if self.noisycount > OVERSENSITIVE:
                self.tap_threshold *= 1.5
        else:
            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                return True
            self.noisycount = 0
            self.quietcount += 1
            if self.quietcount > UNDERSENSITIVE:
                self.tap_threshold *= 1



def clap_detect():
    while True:
        tt = TapTester()
        clap_count = 0

        while True:
            if tt.listen():
                clap_count += 2

                if clap_count == REQUIRED_CLAPS:
                    print("clap dectected")
                    break