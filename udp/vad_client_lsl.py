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

def main():
    
	BUFF_SIZE = 65536
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
	sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

	sock.sendto("DUMMY".encode(), ("127.0.0.1", 12346))

	while True:
		trncpt_data, _ = sock.recvfrom(BUFF_SIZE)
		print("Got ASR response: %s" % str(trncpt_data.decode()))


	sock.close()

if __name__ == '__main__':
    main()
