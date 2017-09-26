# coding: utf8
# jsonutil.py
# 7/4/2014 jichi

from datetime import datetime
import i18n

# http://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable-in-python
def default_datetime(obj):
  """
  @param  obj  any
  @return  any
  """
  if isinstance(obj, datetime):
    return i18n.unparsedatetime(obj)

if __name__ == '__main__':
  import json
  print json.dumps(datetime.now(), default=default_datetime)

# EOF
