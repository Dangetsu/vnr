#, volume=SAPI_MAX_VOLUME coding: utf8
# engine.py
# 4/7/2013 jichi

__all__ = 'SapiEngine',

if __name__ == '__main__': # debug
  import os, sys
  os.environ["PATH"] = os.path.pathsep.join((
    "../../../bin",
    "../../../../Qt/PySide",
  ))
  map(sys.path.append, (
    "../../../../Qt/PySide",
    "../../../bin",
    "..",
  ))

from sakurakit import skstr
from sakurakit.skclass import memoizedproperty
import registry

SAPI_MAX_VOLUME = 100
SAPI_MIN_VOLUME = 0

SAPI_MAX_RATE = 10
SAPI_MIN_RATE = -10

SAPI_MAX_PITCH = 10
SAPI_MIN_PITCH = -10

# Examples:
# <pitch middle="0"><rate speed="-5">\n%s\n</rate></pitch>
# <rate speed="-5">\n%s\n</rate>
# <volume level="5">\n%s\n</volume>
# <rate speed="5">\nお花の匂い\n</rate>
def _toxmltext(text, speed=0, pitch=0, volume=SAPI_MAX_VOLUME):
  """
  @param  text  unicode  text to speak
  @param* speed  int
  @return  unicode  XML
  """
  # "\n" is critical to prevent unicode content from crashing
  # absspeed: absolute
  # speed: relative
  escaped = False
  if speed:
    if not escaped:
      text = skstr.escapehtml(text)
      escaped = True
    text = '<rate speed="%i">\n%s\n</rate>' % (speed, text)
  if pitch:
    if not escaped:
      text = skstr.escapehtml(text)
      escaped = True
    text = '<pitch middle="%i">\n%s\n</pitch>' % (pitch, text)
  if volume != SAPI_MAX_VOLUME:
    if not escaped:
      text = skstr.escapehtml(text)
      escaped = True
    text = '<volume level="%i">\n%s\n</volume>' % (volume, text)
  return text

def _tovoicekey(key):
  """
  @return  unicode
  """
  if key:
    for (hk,base) in (
        ('HKEY_LOCAL_MACHINE', registry.SAPI_HKLM_PATH),
        ('HKEY_CURRENT_USER', registry.SAPI_HKCU_PATH),
      ):
      path = base +  '\\' + key
      if registry.exists(path, hk):
        return hk + '\\' + path
  return ''

class SapiEngine(object):

  # Consistent with registry.py
  def __init__(self, key='',
      speed=0, pitch=0, volume=SAPI_MAX_VOLUME,
      name='', vendor='',
      language='ja', gender='f',
      **kw):
    self._sapi = None # pysapi.SapiPlayer

    self.key = key      # str registry key
    self.name = name    # str
    self.vendor = vendor  # str
    self.language = language # str
    self.gender = gender # str

    self.speed = speed # int
    self.pitch = pitch # int
    self.volume = volume # int

  @property
  def sapi(self):
    if not self._sapi:
      from  pysapi import SapiPlayer
      ret = SapiPlayer()
      ret.setVoice(_tovoicekey(self.key))
      self._sapi = ret
    return self._sapi

  def isValid(self):
    return bool(self.key) and self.sapi.isValid()

  def stop(self):
    if self._sapi:
      self._sapi.purge()

  def speak(self, text, async=True):
    """
    @param  text  unicode
    """
    #if stop:
    #  self.stop()
    if text:
      text = _toxmltext(text,
          speed=self.speed, pitch=self.pitch, volume=self.volume)
      self.sapi.speak(text, async)

if __name__ == '__main__': # debug
  import pythoncom
  #pythoncom.OleInitialize()
  #reg = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\VW Misaki"
  kw = registry.query(key='VW Misaki')
  tts = SapiEngine(**kw)
  print 1
  t = u"Hello"
  t = u"お花の匂い"
  t = _toxmltext(t, pitch=5, speed=-5)
  tts.speak(t, async=False)
  #tts.speak(t, async=False)
  #tts.speak(u'<pitch middle="0"><rate speed="-5">%s</rate></pitch>' % t, async=False)
  #tts.speak(u'<rate speed="-10">\n%s\n</rate>' % t, async=False)
  #tts.speak(u'<volume level="100">\n%s\n</volume>' % t, async=False)
  #tts.speak(u'<rate speed="5">お花の匂い</rate>', async=False)

  #sys.exit(0)

  #print 2
  #tts.stop()
  #tts.speak(u"お早う♪", async=False)
  #print 3
  import time
  time.sleep(3)
  print 4

# EOF

