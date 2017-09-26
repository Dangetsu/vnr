# coding: utf8
# sapiman.py
# 11/16/2013 jichi
# Windows only

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from sakurakit import skos
from sakurakit.skclass import memoized

VW_SHOW = 'VW Show'
VW_MISAKI = 'VW Misaki'
VW_MIYU = 'VW Miyu'

if skos.WIN:
  import sapi.registry

  class SapiVoice:
    def __init__(self, **kwargs):
      self.key = kwargs.get('key') or '' # str
      self.gender = kwargs.get('gender') or 'f' # str
      self.language = kwargs.get('language') or '' # str
      self.name = kwargs.get('name') or '' # unicode
      self.vendor = kwargs.get('vendor') or 'f' # unicode
      self.location = kwargs.get('location') or '' # unicode

  _VOICE_BLACKLIST = frozenset((
    'MS-Anna-1033-20-DSK', # C:\Program Files\Common Files\SpeechEngines\Microsoft\TTS20\en-US\enu-dsk
    'MSMary', # C:\Program Files\Common Files\SpeechEngines\Microsoft\TTS\1033\mary.spd
    'MSMike', # C:\Program Files\Common Files\SpeechEngines\Microsoft\TTS\1033\mike.spd
    'SampleTTSVoice', # C:\Program Files\Microsoft Speech SDK 5.1\Samples\CPP\Engines\TTS\samplevoice.vce
  ))

  def _voicesortkey(v):
    """
    @param  v  SapiVoice
    @return  (int priority, str language, str name)
    """
    if v.key == VW_SHOW:
      priority = 1
    elif v.key == VW_MISAKI:
      priority = 2
    elif v.key == VW_MIYU:
      priority = 3
    elif v.language == 'ja':
      priority = 10
    elif v.language == 'zh':
      priority = 11
    elif v.language == 'en':
      priority = 12
    else:
      priority = 99
    return priority, v.language, v.gender, v.name

  @memoized
  def voices():
    ret = []
    for it in sapi.registry.querylist():
      key = it['key']
      if key and key not in _VOICE_BLACKLIST:
        ret.append(SapiVoice(**it))
    # Reorder
    if ret:
      ret.sort(key=_voicesortkey)
    return ret

  def location(key):
    """
    @param  key  unicode
    @return  unicode
    """
    v = sapi.registry.query(key=key)
    return v['location'] if v else ''

else: # Mac
  def voices(): return []
  def location(key): return ''

if __name__ == '__main__':
  for it in  voices():
    print it.key
  #print location(VW_MISAKI)
  #print location(VW_SHOW)
  #print location(VW_MIYU)

# EOF
