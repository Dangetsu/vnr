# coding: utf8
# eb2db.py
# 2/18/2015 jichi

import sqlite3
import eb, eblib
from sakurakit.skdebug import dprint
from unitraits import jpchars
from dictdb import dictdb

## Gaiji ##

def narrow_gaiji(code):
  """
  @param  code  int
  @return  unicode
  """
  return 'h%04X' % code

def wide_gaiji(code):
  """
  @param  code  int
  @return  unicode
  """
  return 'z%04X' % code

def ebxac_gaiji(code):  # FIXME: caiji code is incorrect
  """
  @param  code  int
  @return  unicode
  """
  return 'c%04X' % code

## EB Renderer ##

class EBHtml(eblib.EB):
  def __init__(self, path, gaiji={}):
    """
    @param  path  unicode
    @param  gaiji  {str:unicode} not None
    """
    super(EBHtml, self).__init__(path)
    self.gaiji = gaiji

  # Overridden hooks

  def hook_newline(self, _):
    """@reimp"""
    self.write_text("<br/>")

  def hook_narrow_font(self, _, code):
    """@reimp"""
    self.write_gaiji(narrow_gaiji(code))
  def hook_wide_font(self, _, code):
    """@reimp"""
    self.write_gaiji(wide_gaiji(code))
  def hook_ebxac_gaiji(self, _, code):
    """@reimp"""
    # FIXME: not working
    #self.write_gaiji(ebxac_gaiji(code))
    pass

  # Helpers

  def write_gaiji(self, key):
    t = self.gaiji.get(key) or ' ' # space by default
    self.write_text(t)

class EBShiori(EBHtml):
  def __init__(self, path, gaiji={}):
    super(EBShiori, self).__init__(path, gaiji=gaiji)

  """Used in kagami/shiori.qml"""
  def hook_begin_reference(self, _):
    """@reimp"""
    self.write_text('<span class="sr">')
  def hook_end_reference(self, _, page, offset):
    """@reimp"""
    #self.write_text("</reference=%x:%x>" % (page, offset))
    self.write_text("</span>")
  def hook_begin_keyword(self, _):
    """@reimp"""
    self.write_text('<span class="sk">')
  def hook_end_keyword(self, _):
    """@reimp"""
    self.write_text("</span>")

def dump(path, gaiji={}, inenc='euc_jp', outenc='utf8', output='eb.db'):
  """
  @param  path  unicode
  @param* gaiji  {str:str}
  @param* inenc  str
  @param* outenc  str
  """
  dprint("enter")

  from sakurakit import skfileio
  skfileio.removefile(output)

  headings = set() # [unicode]
  dictdb.createdb(output)
  with sqlite3.connect(output) as conn:
    cur = conn.cursor()

    shiori = EBShiori(path, gaiji=gaiji)
    kana = jpchars.s_hira + jpchars.s_kata
    for i,ch in enumerate(kana):
      s = ch.encode(inenc)
      hits = shiori.search_word(s)
      dprint(ch, i, len(hits))
      for hit in hits:
        h = hit.heading().decode(outenc)
        if h not in headings:
          headings.add(h)
          t = hit.text().decode(outenc)
          dictdb.insertentry(cur, (h, t))

    conn.commit()

  dprint("leave")

# EOF
