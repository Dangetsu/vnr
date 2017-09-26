# coding: utf8
# bbcode.py
# 3/20/2013 jichi
# See https://github.com/pydsigner/pybbcode

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from sakurakit.skclass import memoized

@memoized
def default_set():
  """
  @return  pybbcode.TagSet
  """
  import pybbcode
  ret = pybbcode.TagSet()
  ret.add_tag(r'\[b\](.*?)\[/b\]', '<b>%(0)s</b>')
  ret.add_tag(r'\[i\](.*?)\[/i\]', '<i>%(0)s</i>')
  ret.add_tag(r'\[u\](.*?)\[/u\]', '<u>%(0)s</u>')

  ret.add_tag(r'\[s\](.*?)\[/s\]',
      '<span style="text-decoration:line-through">%(0)s</span>')

  ret.add_tag(r'\[big\](.*?)\[/big\]',
      '<span style="font-size:130%">%(0)s</span>')
  ret.add_tag(r'\[small\](.*?)\[/small\]',
      '<small>%(0)s</small>')
  ret.add_tag(r'\[size=([7-9]|50|[1-4]\d)\](.*?)\[/size\]',
      '<span style="font-size:%(0)spx">%(1)s</span>')

  ret.add_tag(r'\[color=(.*?)\](.*?)\[/color\]',
      '<span style="color:%(0)s">%(1)s</span>')

  ret.add_tag(r'\[url\](.*?)\[/url\]',
      '<a href="%(0)s" style="color:snow">%(0)s</a>')
  ret.add_tag(r'\[url=(.*?)\](.*?)\[/url\]',
      '<a href="%(0)s" style="color:snow">%(1)s</a>')

  return ret

def parse(bb):
  """
  @param  bb  str or unicode
  """
  ret = default_set().parse_with_ignore(bb) if '[' in bb else bb
  return  ret.replace('\n', "<br/>")

if __name__ == '__main__':
  print parse('''
  [i][b][u]Hello?[/u][/b][/i]
  [css="[i][/i]"][/css]
  [ignore]
      [i]This would be italic.[/i]
      [/ignore]
      [url="http://www.google.com"]Google[/url]
      [big][url]http://www.python.org[/url][/bigg]
      [size=50][css="text-color:red"]CSS tag[/css][/size]
''')

# EOF
