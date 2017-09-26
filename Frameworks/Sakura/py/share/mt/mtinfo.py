# coding: utf8
# 2/10/2015

MT_INFO = {
  'bing':       {'online':True,  'align':True,   'script':True,  },
  'google':     {'online':True,  'align':True,   'script':True,  },
  'babylon':    {'online':True,  'align':False,  'script':True,  },
  'lecol':      {'online':True,  'align':False,  'script':True,  },
  'infoseek':   {'online':True,  'align':True,   'script':True,  },
  'excite':     {'online':True,  'align':False,  'script':True,  },
  'nifty':      {'online':True,  'align':False,  'script':True,  },
  'systran':    {'online':True,  'align':False,  'script':True,  },
  'transru':    {'online':True,  'align':False,  'script':True,  },
  'naver':      {'online':True,  'align':True,   'script':False, },
  'baidu':      {'online':True,  'align':True,   'script':False, },
  'youdao':     {'online':True,  'align':True,   'script':False, },
  'jbeijing':   {'online':False, 'align':False,  'script':False, },
  'fastait':    {'online':False, 'align':False,  'script':False, },
  'dreye':      {'online':False, 'align':False,  'script':False, },
  'eztrans':    {'online':False, 'align':False,  'script':False, },
  'transcat':   {'online':False, 'align':False,  'script':False, },
  'atlas':      {'online':False, 'align':False,  'script':True,  },
  'lec':        {'online':False, 'align':False,  'script':True,  },
  'hanviet':    {'online':False, 'align':True,   'script':False, },
  'vtrans':     {'online':True,  'align':False,  'script':False, },
}

def test_online(key):
  """
  @param  key  str
  @return  bool
  """
  try: return MT_INFO[key]['online']
  except KeyError: return False

def test_align(key):
  """
  @param  key  str
  @return  bool
  """
  try: return MT_INFO[key]['align']
  except KeyError: return False

def test_script(key):
  """
  @param  key  str
  @return  bool
  """
  try: return MT_INFO[key]['script']
  except KeyError: return False

def test_lang(key, to=None, fr=None):
  """
  @param  key  str
  @param* to  str  language
  @param* fr  str  language
  @return  bool
  """
  if key in ('google', 'bing'):
    return True
  f = get_mod_def(key)
  if f:
    online = test_online(key)
    return f.mt_test_lang(to=to, fr=fr, online=online)
  return False

def get_s_langs(key):
  """
  @param  key  str
  @return  [str] or None
  """
  if key not in ('google', 'bing', 'systran'):
    f = get_mod_def(key)
    if f:
      online = test_online(key)
      return f.mt_s_langs(online=online)

def get_t_langs(key):
  """
  @param  key  str
  @return  [str] or None
  """
  if key not in ('google', 'bing', 'systran'):
    f = get_mod_def(key)
    if f:
      online = test_online(key)
      return f.mt_t_langs(online=online)

def get_mod_def(key):
  """
  @param  key  str
  @return  module
  """
  if key == 'atlas':
    from atlas import atlasdef
    return atlasdef
  if key in ('lec', 'lecol'):
    from lec import lecdef
    return lecdef
  if key == 'eztrans':
    from eztrans import ezdef
    return ezdef
  if key == 'transcat':
    from transcat import transcatdef
    return transcatdef
  if key == 'jbeijing':
    from jbeijing import jbdef
    return jbdef
  if key == 'dreye':
    from dreye import dreyedef
    return dreyedef
  if key in ('fastait', 'iciba'):
    from kingsoft import icibadef
    return icibadef
  if key == 'baidu':
    from baidu import baidudef
    return baidudef
  if key == 'youdao':
    from youdao import youdaodef
    return youdaodef
  if key == 'naver':
    from naver import naverdef
    return naverdef
  if key == 'infoseek':
    from transer import infoseekdef
    return infoseekdef
  if key == 'excite':
    from excite import excitedef
    return excitedef
  if key == 'babylon':
    from babylon import babylondef
    return babylondef
  if key == 'systran':
    from systran import systrandef
    return systrandef
  if key == 'nifty':
    from nifty import niftydef
    return niftydef
  if key == 'transru':
    from promt import transdef
    return transdef
  if key == 'google':
    from google import googledef
    return googledef
  if key == 'bing':
    from bing import bingdef
    return bingdef
  if key == 'hanviet':
    from hanviet import hanvietdef
    return hanvietdef
  if key == 'vtrans':
    from vtrans import vdef
    return vdef
  return None

# EOF
