# coding: utf8
# res.py
# 11/25/2012 jichi

import os
from sakurakit import skfileio
from sakurakit.skclass import memoized, memoizedproperty
from sakurakit.sktr import tr_
from mytr import my
import growl, rc

class Resource(object):
  def __init__(self, path='', lockpath=''):
    self.path = path # unicode
    self.lockpath = lockpath # unicode

  def open(self):
    location = os.path.dirname(self.path)
    import osutil
    osutil.open_location(location)

  def get(self): return False # -> bool # abstract

  def exists(self): # -> bool
    return os.path.exists(self.path)
  def locked(self): # -> bool
    skfileio.removefile(self.lockpath)
    return os.path.exists(self.lockpath)
  def remove(self): # -> bool
    return skfileio.removefile(self.path)
  def valid(self): return self.exists()

  def removetree(self): # -> bool # utility
    return skfileio.removetree(self.path)

class AppLocale(Resource):
  URL = 'http://ntu.csie.org/~piaip'
  #URL = 'http://ntu.csie.org/~piaip/papploc.msi'
  #URL = "http://www.microsoft.com/en-us/download/details.aspx?id=13209"

  def __init__(self):
    from sakurakit import skpaths
    super(AppLocale, self).__init__(
      #path=os.path.join(rc.DIR_CACHE_INST, "AppLocale/papploc.msi"),
      path=os.path.join(skpaths.WINDIR, "AppPatch/AlLayer.dll"),
      lockpath=os.path.join(rc.DIR_TMP, "apploc.lock"),
    )

  def remove(self): # override
    from scripts import apploc
    return apploc.remove()

  def get(self): # override
    from scripts import apploc
    return apploc.get()

#class TahScript(Resource):
#  URL = 'http://sakuradite.com/wiki/en/VNR/Translation_Scripts'
#
#  def __init__(self):
#    super(TahScript, self).__init__(
#      path=os.path.join(rc.DIR_CACHE_DICT, "Scripts/tahscript.txt"),
#      lockpath=os.path.join(rc.DIR_TMP, "tahscript.lock"),
#    )
#
#  def get(self): # override
#    # TODO
#    # Fetch the online wiki at URL
#    return True

class Font(Resource):

  def __init__(self, family):
    import config
    self.family = family
    super(Font, self).__init__(
      path=config.FONT_LOCATIONS[family],
      lockpath=os.path.join(rc.DIR_TMP, "font.%s.lock" % family),
    )

  def get(self): # override
    from scripts import font
    return font.get(self.family)

  def remove(self): # override
    return self.removetree()

# Global objects

@memoized
def apploc(): return AppLocale()

FONTS = {} # {str lang:JMDictic}
def font(key):
  """
  @param  key  str  such as hanazono
  @return  Font
  """
  ret = FONTS.get(key)
  if not ret:
    FONTS[key] = ret = Font(key)
  return ret

#@memoized
#def tahscript(): return TahScript()

# EOF
