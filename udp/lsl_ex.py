"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream
import pyaudio
import numpy as np


def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")

    # type is case-sensitive
    streams = resolve_stream('type', 'Audio')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    p = pyaudio.PyAudio()

    # BUFFER_LEN / 1000
    # FRAMES_PER_BUFFER / RATE
    # BLOCKS_PER_SECOND
    # FRAMES_PER_BUFFER = BUFFER_LEN * RATE / 1000 = RATE / BLOCKS_PER_SECOND

    BUFFER_LEN = 10
    CHUNK = BUFFER_LEN*1024
    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    output=True,
                    frames_per_buffer=int(BUFFER_LEN * 44100 / 1000))

    # BUFFER_LEN = CHUNK / 1024 = RATE / (50 * 1024) = RATE / (BLOCKS_PER_SECOND * 1024)
    while True:
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        chunk, _ = inlet.pull_chunk()
        # print(len(chunk))
        
        # stream.write(chunk)
        stream.write(np.array(chunk).astype(np.int16).tobytes())
        # stream.write(np.array(chunk).tostring())
        # if len(chunk) != 0:
        #     print(type(chunk[0][0]))


if __name__ == '__main__':
    main()