# coding: utf8
# myss.py
# 5/28/2013 jichi

import rc

SS = 'body{background-image:url("%s")}' % rc.image_url('background').toString()
def render(html):
  """
  @param  html  unicode
  @return  unicode
  """
  return "<style>%s</style>" % SS + "<body>%s</body>" % html

# EOF
