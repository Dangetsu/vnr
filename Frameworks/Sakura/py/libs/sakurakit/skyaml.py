# coding: utf8
# skyaml
# 12/16/2014 jichi
# See: http://stackoverflow.com/questions/20352794/pyyaml-is-producing-undesired-python-unicode-output

from sakurakit.skdebug import dwarn
import yaml

# default_flow_style: Disable default flow style to make it more readable
def dump(data, f, default_flow_style=False, encoding='utf-8', allow_unicode=True):
  try:
    yaml.safe_dump(data, f,
      default_flow_style=default_flow_style,
      encoding=encoding,
      allow_unicode=allow_unicode)
    return True
  except Exception, e:
    dwarn(e)
    return False

def writefile(data, path, **kwargs):
  try: return dump(data, file(path, 'w'), **kwargs)
  except Exception, e:
    dwarn(e)
    return False

# EOF
