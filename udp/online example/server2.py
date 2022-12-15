import pyaudio
import socket
import queue
from threading import Thread

# frames = []

if __name__ == "__main__":
    FORMAT = pyaudio.paInt16
    CHUNK = 1024
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()
    frames = queue.Queue()

    stream = p.open(format=FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    output = True,
                    frames_per_buffer = CHUNK,
                    )

                    
    def udpStream():

        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("127.0.0.1", 12345))

        while True:
            soundData, _ = udp.recvfrom(CHUNK * CHANNELS * 2)
            frames.put(soundData)

        udp.close()

    def play():
        while True:
            stream.write(frames.get())

    Ts = Thread(target = udpStream)
    Tp = Thread(target = play)
    Ts.setDaemon(True)
    Tp.setDaemon(True)
    Ts.start()
    Tp.start()
    Ts.join()
    Tp.join()