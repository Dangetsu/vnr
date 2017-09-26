# coding: utf8
# 1/10/2014 jichi
# EOF

#import json
from PySide.QtCore import QUrl
#from sakurakit.skdebug import dwarn
import osutil

def evalurl(url, x=None, y=None): # TODO: move ot other file
  """
  @param  url  QUrl
  @param* x  int or None
  @param* y  int or None
  @return  bool or None
  """
  origurl = url
  if isinstance(url, QUrl):
    url = url.toString()
  JSON_PREFIX = 'json://'
  if url.startswith(JSON_PREFIX):
    url = url[len(JSON_PREFIX):]
    if url:
      evaljson(url, x=None, y=None)
      return True
  elif url:
    osutil.open_url(origurl)
    return True

def evaljson(data, x=None, y=None):
  """
  @param  data  unicode  json
  @param* x  int or None
  @param* y  int or None
  """
  import shiori
  if x is None or y is None:
    shiori.showjson(data)
  else:
    shiori.showjsonat(data, x, y)
  #try:
  #  data = json.loads(data)
  #  if data.get('type') == 'term':
  #    id = data['id']
  #    if id:
  #      main.manager().showTerm(id=id)
  #      return True
  #  else:
  #    dwarn("unrecognized json type")
  #except Exception, e:
  #  dwarn(e)

# EOF
