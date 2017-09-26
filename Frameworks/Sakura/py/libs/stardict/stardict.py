# coding: utf8
# stardict.py
# 4/26/2015  jichi
import os
from glob import glob
from sakurakit.skdebug import dwarn

class StarDict(object):
  #ifo_compressed = False
  #idx_compressed = False
  #dict_compressed = False

  # TODO: Automatically gess here
  def __init__(self, path='', ifo_file='', idx_file='', dict_file=''):
    """
    @param  path  unicode  base name
    @param* ifo_file  unicode
    @param* idx_file  unicode
    @param* dict_file  unicode
    """
    self.ifo_file = ifo_file or self.getDictionaryFile(path, 'ifo') # unicode
    self.idx_file = idx_file or self.getDictionaryFile(path, 'idx') # unicode
    self.dict_file = dict_file or self.getDictionaryFile(path, 'dict') # unicode
    self.reader = None

  def getDictionaryFile(self, path, suffix):
    """
    @param  path  unicode
    @param  path  suffix
    @return  unicode
    """
    ret = "%s.%s" % (path, suffix)
    if os.path.exists(ret):
      return ret
    if os.path.isdir(path):
      l = glob(os.path.join(path, '*.%s.dz' % suffix))
      if l and len(l) == 1:
        ret = l[0]
      else:
        l = glob(os.path.join(path, '*.%s' % suffix))
        if l and len(l) == 1:
          ret = l[0]
    return ret

  def valid(self): return bool(self.reader)

  def init(self):
    """
    @return  bool
    """
    import starlib
    try:
      ifo_reader = starlib.IfoFileReader(self.ifo_file) #, compressed=self.ifo_compressed)
      idx_reader = starlib.IdxFileReader(self.idx_file) #, compressed=self.idx_compressed)
      dict_reader = starlib.DictFileReader(self.dict_file, ifo_reader, idx_reader) #, compressed=self.dict_compressed)

      self.reader = dict_reader
      return True
    except Exception, e:
      dwarn(e)
      return False

  def query(self, text):
    """
    @param  text  unicode
    @return  [unicode] or None
    """
    try:
      m = self.reader.get_dict_by_word(text)
      if m:
        ret = []
        for it in m:
          ret.extend(it.itervalues())
        return ret
    except Exception, e: dwarn(e)

# EOF
