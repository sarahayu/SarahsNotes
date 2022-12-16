from pylsl import StreamInfo, StreamOutlet, resolve_stream
import pyaudio
import numpy as np


def main():
    BUFFER_LEN = 10
    CHUNK = BUFFER_LEN*1024
    RATE = 44100
    CHANNELS = 1
    info = StreamInfo("MyMic", "Audio", CHANNELS, RATE, 'int16', 'myuid34234')

    # next make an outlet
    outlet = StreamOutlet(info)

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(2),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    while True:
        frame = stream.read(CHUNK)
        outlet.push_chunk(np.frombuffer(frame, dtype=np.int16))


if __name__ == '__main__':
    main()