# coding: utf8
# googlesr.py 11/1/2014
# See: https://www.google.com/intl/ja/chrome/demos/speech.html
# See: http://qiita.com/ysk_1031/items/8b8990a65bc586f33a20
# See: https://github.com/gillesdemey/google-speech-v2
# See: https://pypi.python.org/pypi/SpeechRecognition/
#
# Alternative: AT&T recognition: http://www.wilsonmar.com/speech_to_text.htm

__all__ = 'Microphone', 'Recognizer'

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import audioop, collections, io, json, math, wave
#try: from urllib2 import Request, urlopen # try to use python2 module
#except ImportError: from urllib.request import Request, urlopen # otherwise, use python3 module
from urllib2 import Request, urlopen
import pyaudio
from sakurakit.skdebug import dprint

#def defaultapi(): return 'http://translate.google.com/m' # this will redirect to https
def defaultapi(): return "http://www.google.com/speech-api/v2/recognize"
def setapi(url):
  """
  @param  url  str
  """
  global GOOGLE_SR_API
  GOOGLE_SR_API = url

# Example: "http://www.google.com/speech-api/v2/recognize?client=chromium&lang=%s&key=%s" % (self.language, self.key)
GOOGLE_SR_API = defaultapi()
#GOOGLE_SR_API = "http://sakuradite.org/proxy/gg/speech/v2/recognize"
GOOGLE_API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw" # See: https://pypi.python.org/pypi/SpeechRecognition/

MIMETYPE_WAV = 'audio/l16' # See: http://qiita.com/ysk_1031/items/8b8990a65bc586f33a20
MIMETYPE_FLAC = 'audio/x-flac'

#wip: filter out clicks and other too short parts

class AudioSource(object): # abstract

  def __enter__(self): self.open(); return self
  def __exit__(self, *err): self.close()

  def open(self): pass
  def close(self): pass

class Microphone(AudioSource):

  MIMETYPE = MIMETYPE_WAV # str

  #RATE = 44100 # lower sample rate to make the sound smaller
  RATE = 16000 # int  sampling rate in Hertz

  CHANNELS = 1 # int  mono audio
  CHUNK = 1024 # int  number of frames stored in each buffer

  FORMAT = pyaudio.paInt16 # 16-bit int sampling
  SAMPLE_WIDTH = pyaudio.get_sample_size(FORMAT)

  def __init__(self, device_index=None):
    """
    @param  device_index  int or None  device index of pyaudio.PyAudio
    """
    self.device_index = device_index # int or None
    self.audio = None # pyaudio.PyAudio
    self.stream = None # pyaudio stream

  def open(self):
    """@reimp"""
    self.audio = pyaudio.PyAudio()
    self.stream = self.audio.open(
        input_device_index=self.device_index,
        format=self.FORMAT,
        rate=self.RATE,
        channels=self.CHANNELS,
        frames_per_buffer=self.CHUNK,
        input=True) # stream is an input stream

  def close(self):
    """@reimp"""
    self.stream.stop_stream()
    self.stream.close()
    self.stream = None
    self.audio.terminate()
    self.audio = None

class WavFile(AudioSource):
  def __init__(self, filename_or_fileobject):
    """
    @param  filename_or_fileobject  unicode or file
    """
    if isinstance(filename_or_fileobject, str):
      self.filename = filename_or_fileobject
    else:
      self.filename = None
      self.wav_file = filename_or_fileobject
    self.stream = None

  def open(self):
    """@reimp"""
    if self.filename: self.wav_file = open(self.filename, "rb")
    self.wav_reader = wave.open(self.wav_file, "rb")
    self.SAMPLE_WIDTH = self.wav_reader.getsampwidth()
    self.RATE = self.wav_reader.getframerate()
    self.CHANNELS = self.wav_reader.getnchannels()
    assert self.CHANNELS == 1 # audio must be mono
    self.CHUNK = 4096
    self.stream = WavFile.WavStream(self.wav_reader)

  def close(self):
    """@reimp"""
    if self.filename: self.wav_file.close()
    self.stream = None

  class WavStream(object):
    def __init__(self, wav_reader):
      self.wav_reader = wav_reader

    def read(self, size = -1):
      if size == -1:
        return self.wav_reader.readframes(self.wav_reader.getnframes())
      return self.wav_reader.readframes(size)

class AudioData(object):
  def __init__(self, type, rate, data):
    self.type = type # str
    self.rate = rate # int
    self.data = data # str

class Recognizer(object):

  key = GOOGLE_API_KEY # str

  energy_threshold = 100 # minimum audio energy to consider for recording
  #energy_threshold = 0 # 11/2/2014: Tuned for Soundflower

  pause_threshold = 0.8 # seconds of quiet time before a phrase is considered complete
  quiet_duration = 0.5 # amount of quiet time to keep on both sides of the recording

  def __init__(self, language="en-US"):
    self.language = language # str  such as en-US, ja-JP
    self.aborted = False
    self.stopped = False
    self.detects_quiet = True

  def open_file(self):
    """
    @return  file
    """
    return io.BytesIO()

  def encode(self, source, frame_data):
    """Save wav file.
    @param  source  AudioSource
    @param  frame_data  str
    @return  str
    """
    with self.open_file() as wav_file:
      wav_writer = wave.open(wav_file, 'wb')
      try:
        wav_writer.setsampwidth(source.SAMPLE_WIDTH)
        wav_writer.setnchannels(source.CHANNELS)
        wav_writer.setframerate(source.RATE)
        wav_writer.writeframes(frame_data)
      finally:  # make sure resources are cleaned up
        wav_writer.close()
      if isinstance(wav_file, file):
        wav_file.seek(0)
        wav_data = wav_file.read()
      else:
        wav_data = wav_file.getvalue()
      return wav_data

    #import platform, os
    ## determine which converter executable to use
    #system = platform.system()
    #path = os.path.dirname(os.path.abspath(__file__)) # directory of the current module file, where all the FLAC bundled binaries are stored
    #flac_converter = shutil_which("flac") # check for installed version first
    #if flac_converter is None: # flac utility is not installed
    #  if system == "Windows" and platform.machine() in {"i386", "x86", "x86_64", "AMD64"}: # Windows NT, use the bundled FLAC conversion utility
    #    flac_converter = os.path.join(path, "flac-win32.exe")
    #  elif system == "Linux" and platform.machine() in {"i386", "x86", "x86_64", "AMD64"}:
    #    flac_converter = os.path.join(path, "flac-linux-i386")
    #  else:
    #    raise ChildProcessError("FLAC conversion utility not available - consider installing the FLAC command line application")
    #process = subprocess.Popen("\"%s\" --stdout --totally-silent --best -" % flac_converter, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    #flac_data, stderr = process.communicate(wav_data)
    #return flac_data

  # Not implemented
  #def record(self, source, duration=0):
  #  """
  #  @param  source  AudioSource
  #  @param* duration  float
  #  """
  #  assert isinstance(source, AudioSource) and source.stream

  #  frames = io.BytesIO()
  #  seconds_per_buffer = (source.CHUNK + 0.0) / source.RATE
  #  elapsed_time = 0
  #  while True: # loop for the total number of chunks needed
  #    elapsed_time += seconds_per_buffer
  #    if duration and elapsed_time > duration: break

  #    buffer = source.stream.read(source.CHUNK)
  #    if len(buffer) == 0: break
  #    frames.write(buffer)

  #  frame_data = frames.getvalue()
  #  frames.close()
  #  data = self.encode(source, frame_data)
  #  return AudioData(source.MIMETYPE, source.RATE, data)

  def listen(self, source, timeout=0):
    """
    @param  source  AudioSource
    @param* timeout  int
    @return AudioData or None
    """
    assert isinstance(source, AudioSource) and source.stream

    # record audio data as raw samples
    frames = collections.deque()
    assert self.pause_threshold >= self.quiet_duration >= 0
    seconds_per_buffer = source.CHUNK / float(source.RATE)
    pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer)) # number of buffers of quiet audio before the phrase is complete
    quiet_buffer_count = int(math.ceil(self.quiet_duration / seconds_per_buffer)) # maximum number of buffers of quiet audio to retain before and after
    elapsed_time = 0

    dprint("start")

    # store audio input until the phrase starts
    while not self.stopped:
      if self.aborted:
        return
      elapsed_time += seconds_per_buffer
      if timeout and elapsed_time > timeout: # handle timeout if specified
        #raise TimeoutError("listening timed out")
        break

      buffer = source.stream.read(source.CHUNK)
      if len(buffer) == 0:
        break # reached end of the stream
      frames.append(buffer)

      # Always detects quiet
      #if self.detects_quiet:
      # check if the audio input has stopped being quiet
      energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal, https://en.wikipedia.org/wiki/Root_mean_square
      if energy > self.energy_threshold:
        break

      if len(frames) > quiet_buffer_count: # ensure we only keep the needed amount of quiet buffers
        frames.popleft()

    dprint("recording")

    # read audio input until the phrase ends
    pause_count = 0
    while not self.stopped:
      if self.aborted:
        return
      buffer = source.stream.read(source.CHUNK)
      if len(buffer) == 0:
        break # reached end of the stream
      frames.append(buffer)

      if self.detects_quiet:
        # check if the audio input has gone quiet for longer than the pause threshold
        energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
        if energy > self.energy_threshold:
          pause_count = 0
        else:
          pause_count += 1
        if pause_count > pause_buffer_count: # end of the phrase
          pause_count = pause_buffer_count
          break

    dprint("stop")

    # remove extra quiet frames at the end
    if pause_count:
      for i in range(quiet_buffer_count, pause_count):
        if frames:
          frames.pop()

    if not frames:
      return

    # obtain frame data
    frame_data = b"".join(list(frames))

    if self.aborted:
      return
    return AudioData(source.MIMETYPE, source.RATE, self.encode(source, frame_data))

  def recognize(self, audio_data, show_all=False):
    """
    @param  audio_data  AudioData
    @param* show_all  bool
    @return  unicode or None
    """
    assert isinstance(audio_data, AudioData)

    url = "%s?client=chromium&lang=%s&key=%s" % (GOOGLE_SR_API, self.language, self.key)
    #self.request = Request(url, data = audio_data.data, headers = {"Content-Type": "audio/x-flac; rate=%s" % audio_data.rate})
    self.request = Request(url, data = audio_data.data, headers = {"Content-Type": "audio/l16; rate=%s" % audio_data.rate})
    # check for invalid key response from the server
    try: response = urlopen(self.request)
    except: raise KeyError("Server wouldn't respond (or invalid key or quota has been maxed out or network error)")
    response_text = response.read().decode("utf-8")

    # ignore any blank blocks
    actual_result = []
    for line in response_text.split("\n"):
      if not line: continue
      result = json.loads(line)["result"]
      if len(result) != 0:
        actual_result = result[0]

    # make sure we have a list of transcriptions
    if "alternative" not in actual_result:
      #raise LookupError("Speech is unintelligible")
      return None

    # return the best guess unless told to do otherwise
    if not show_all:
      for prediction in actual_result["alternative"]:
        if "confidence" in prediction:
          return prediction["transcript"]
      #raise LookupError("Speech is unintelligible")
      return None

    spoken_text = []

    # check to see if Google thinks it's 100% correct
    default_confidence = 0
    if len(actual_result["alternative"])==1: default_confidence = 1

    # return all the possibilities
    for prediction in actual_result["alternative"]:
      if "confidence" in prediction:
        spoken_text.append({"text":prediction["transcript"], "confidence":prediction["confidence"]})
      else:
        spoken_text.append({"text":prediction["transcript"], "confidence":default_confidence})
    return spoken_text

# helper functions

if __name__ == '__main__':

  class DebugRecognizer(Recognizer):
    def __init__(self, *args, **kwargs):
      super(DebugRecognizer, self).__init__(*args, **kwargs)
    def open_file(self):
      """@reimp"""
      path = "test.wav"
      return open(path, 'w+b')

  a = pyaudio.PyAudio()

  print '==== host info'
  for i in range(a.get_host_api_count()):
    info = a.get_host_api_info_by_index(i)
    print i, '------'
    print info

  print '==== device info'
  for i in range(a.get_device_count()):
    info = a.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
      print i, '------'
      print info

  #print devinfo['index']
  #print devinfo['maxInputChannels']
  #import sys
  #sys.exit(0)

  dev = None # Microphone
  #dev = 1 # Microphone
  #dev = 4 # Primary Sound Capture Driver
  #dev = 5 # Parallels Audio Controller

  r = DebugRecognizer(language='ja')

  import sys, signal
  def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    r.stopped = True
  signal.signal(signal.SIGINT, signal_handler)

  r.detects_quiet = False
  with Microphone(device_index=dev) as source:                # use the default microphone as the audio source
    print "listen start"
    audio = r.listen(source)                   # listen for the first phrase and extract it into audio data
    print "listen stop"

  t = r.recognize(audio)
  if t is None:
    print("Could not understand audio")
  else:
    print("You said " + t)    # recognize speech using Google Speech Recognition

# EOF

#def shutil_which(pgm):
#  """
#  python2 backport of python3's shutil.which()
#  """
#  path = os.getenv('PATH')
#  for p in path.split(os.path.pathsep):
#    p = os.path.join(p, pgm)
#    if os.path.exists(p) and os.access(p, os.X_OK):
#      return p
