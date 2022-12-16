import time, logging
from datetime import datetime
import threading, collections, queue, os, os.path
import stt
import numpy as np
import pyaudio
import wave
import webrtcvad
import socket
from halo import Halo
from scipy import signal

logging.basicConfig(level=20)

lock = threading.Lock()

def main(ARGS):
    
    print("Listening (ctrl-C to exit)...")
    audio_frames = queue.Queue()
    
    def trncptRecvStream():
        BUFF_SIZE = 65536
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

        sock.sendto("DUMMY".encode(), ("127.0.0.1", 12346))

        while True:
            trncpt_data, _ = sock.recvfrom(BUFF_SIZE)
            with lock:
                print("Got ASR response: %s" % str(trncpt_data.decode()))


        sock.close()

        
    def audioSendStream():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    

        while True:
            sock.sendto(audio_frames.get(), ("127.0.0.1", 12345))

        sock.close()
        
    trncpt_thread = threading.Thread(target = trncptRecvStream)
    audio_thread = threading.Thread(target = audioSendStream)
    trncpt_thread.setDaemon(True)
    audio_thread.setDaemon(True)
    trncpt_thread.start()
    audio_thread.start()

    p = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = ARGS.rate
    CHUNK = int(RATE / float(50))

    stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

    while True:
        audio_frames.put(stream.read(CHUNK))

if __name__ == '__main__':
    DEFAULT_SAMPLE_RATE = 16000

    import argparse
    parser = argparse.ArgumentParser(description="Stream from microphone to STT using VAD")

    parser.add_argument('-r', '--rate', type=int, default=DEFAULT_SAMPLE_RATE,
                        help=f"Input device sample rate. Default: {DEFAULT_SAMPLE_RATE}. Your device may require 44100.")
    ARGS = parser.parse_args()
    if ARGS.savewav: os.makedirs(ARGS.savewav, exist_ok=True)
    main(ARGS)
