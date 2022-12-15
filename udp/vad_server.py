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

def main(ARGS):
    # Load STT model
    if os.path.isdir(ARGS.model):
        model_dir = ARGS.model
        ARGS.model = os.path.join(model_dir, 'output_graph.pb')
        ARGS.scorer = os.path.join(model_dir, ARGS.scorer)

    print('Initializing model...')
    logging.info("ARGS.model: %s", ARGS.model)
    model = stt.Model(ARGS.model)
    if ARGS.scorer:
        logging.info("ARGS.scorer: %s", ARGS.scorer)
        model.enableExternalScorer(ARGS.scorer)

    print("Listening (ctrl-C to exit)...")
    audio_frames = queue.Queue()
    trncpt_frames = queue.Queue()
    END_FRAME = None

    # Stream from microphone to STT using VAD
    spinner = None
    if not ARGS.nospinner:
        spinner = Halo(spinner='line')
    stream_context = model.createStream()

    def audioRecvStream():

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 12345))
        has_data = False

        while True:
            try:
                sock.settimeout(1)
                soundData, _ = sock.recvfrom(ARGS.rate)
                has_data = True
                audio_frames.put(soundData)
            except:
                # did not receive data for 1 second... 
                if has_data:
                    has_data = False
                    audio_frames.put(END_FRAME)

        sock.close()
            
    def trncptSendStream():
        BUFF_SIZE = 65536

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
        sock.bind(("127.0.0.1", 12346))

        _, client_addr = sock.recvfrom(BUFF_SIZE)

        while True:
            sock.sendto(trncpt_frames.get().encode(), client_addr)

        sock.close()
    
    audio_thread = threading.Thread(target = audioRecvStream)
    trncpt_thread = threading.Thread(target = trncptSendStream)
    audio_thread.setDaemon(True)
    trncpt_thread.setDaemon(True)
    audio_thread.start()
    trncpt_thread.start()

    while True:
        # still have frames to add
        logging.debug("streaming frame")
        frame = audio_frames.get()

        if frame is END_FRAME:

            if spinner: spinner.stop()
            logging.debug("end utterence")

            text = stream_context.finishStream()
            print("Recognized: %s" % text)
            trncpt_frames.put(text)
            if ARGS.keyboard:
                from pyautogui import typewrite
                typewrite(text)
            stream_context = model.createStream()
        else:
            if spinner: spinner.start()
            stream_context.feedAudioContent(np.frombuffer(frame, np.int16))

if __name__ == '__main__':
    DEFAULT_SAMPLE_RATE = 16000

    import argparse
    parser = argparse.ArgumentParser(description="Stream from microphone to STT using VAD")

    # parser.add_argument('-v', '--vad_aggressiveness', type=int, default=3,
    #                     help="Set aggressiveness of VAD: an integer between 0 and 3, 0 being the least aggressive about filtering out non-speech, 3 the most aggressive. Default: 3")
    parser.add_argument('--nospinner', action='store_true',
                        help="Disable spinner")
    parser.add_argument('-w', '--savewav',
                        help="Save .wav files of utterences to given directory")
    parser.add_argument('-f', '--file',
                        help="Read from .wav file instead of microphone")

    parser.add_argument('-m', '--model', required=True,
                        help="Path to the model (protocol buffer binary file, or entire directory containing all standard-named files for model)")
    parser.add_argument('-s', '--scorer',
                        help="Path to the external scorer file.")
    # parser.add_argument('-d', '--device', type=int, default=None,
    #                     help="Device input index (Int) as listed by pyaudio.PyAudio.get_device_info_by_index(). If not provided, falls back to PyAudio.get_default_device().")
    parser.add_argument('-r', '--rate', type=int, default=DEFAULT_SAMPLE_RATE,
                        help=f"Input device sample rate. Default: {DEFAULT_SAMPLE_RATE}. Your device may require 44100.")
    parser.add_argument('-k', '--keyboard', action='store_true', 
                        help="Type output through system keyboard")
    ARGS = parser.parse_args()
    if ARGS.savewav: os.makedirs(ARGS.savewav, exist_ok=True)
    main(ARGS)
