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
    frames = queue.Queue()

    # Stream from microphone to STT using VAD
    spinner = None
    if not ARGS.nospinner:
        spinner = Halo(spinner='line')
    stream_context = model.createStream()
    wav_data = bytearray()
    has_data = False

    def udpStream():

        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("127.0.0.1", 12345))

        while True:
            soundData, _ = udp.recvfrom(ARGS.rate)
            frames.put(soundData)
    
    Ts = threading.Thread(target = udpStream)
    Ts.setDaemon(True)
    Ts.start()
    
    while True:
        try:
            # still have frames to add
            logging.debug("streaming frame")
            frame = frames.get(timeout=3)
            if spinner: spinner.start()
            has_data = True
            stream_context.feedAudioContent(np.frombuffer(frame, np.int16))
        except queue.Empty:
            # no more frames, possible pause (...or network lag)
            if spinner: spinner.stop()
            logging.debug("end utterence")
            if has_data:
                has_data = False
                text = stream_context.finishStream()
                print("Recognized: %s" % text)
                if ARGS.keyboard:
                    from pyautogui import typewrite
                    typewrite(text)
                stream_context = model.createStream()

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
