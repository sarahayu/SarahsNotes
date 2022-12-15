import pyaudio
import socket
import queue
from threading import Thread

if __name__ == "__main__":
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()
    frames = queue.Queue()

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = CHUNK,
                    )

                    
    def udpStream():
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

        while True:
            udp.sendto(frames.get(), ("127.0.0.1", 12345))

        udp.close()

    def record():    
        while True:
            frames.put(stream.read(CHUNK))

    Tr = Thread(target = record)
    Ts = Thread(target = udpStream)
    Tr.setDaemon(True)
    Ts.setDaemon(True)
    Tr.start()
    Ts.start()
    Tr.join()
    Ts.join()