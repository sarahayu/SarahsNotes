# brew install portaudio
# pip install pyaudio

import pyaudio
import wave
import audioop
import math
from collections import deque

# Silence limit in seconds. The max ammount of seconds where
# only silence is recorded. When this time passes the
# recording finishes and the file is delivered.

# The silence threshold intensity that defines silence
# and noise signal (an int. lower than THRESHOLD is silence).

# Previous audio (in seconds) to prepend. When noise
# is detected, how much of previously recorded audio is
# prepended. This helps to prevent chopping the beggining
# of the phrase.

def record_on_detect(file_name, silence_limit=1, silence_threshold=2500, chunk=1024, rate=44100, prev_audio=1):
  CHANNELS = 2
  FORMAT = pyaudio.paInt16

  p = pyaudio.PyAudio()
  stream = p.open(format=p.get_format_from_width(2),
                  channels=CHANNELS,
                  rate=rate,
                  input=True,
                  output=False,
                  frames_per_buffer=chunk)

  listen = True
  started = False
  rel = rate/chunk
  frames = []

  prev_audio = deque(maxlen=int(prev_audio * rel))
  slid_window = deque(maxlen=int(silence_limit * rel))

  while listen:
    data = stream.read(chunk)
    slid_window.append(math.sqrt(abs(audioop.avg(data, 4))))

    if(sum([x > silence_threshold for x in slid_window]) > 0):
      if(not started):
        print("Starting record of phrase")
        started = True
    elif (started is True):
      started = False
      listen = False
      prev_audio = deque(maxlen=int(0.5 * rel))

    if (started is True):
      frames.append(data)
    else:
      prev_audio.append(data)

  stream.stop_stream()
  stream.close()

  p.terminate()


  wf = wave.open(f'{file_name}.wav', 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(p.get_sample_size(FORMAT))
  wf.setframerate(rate)

  wf.writeframes(b''.join(list(prev_audio)))
  wf.writeframes(b''.join(frames))
  wf.close()


record_on_detect('example')