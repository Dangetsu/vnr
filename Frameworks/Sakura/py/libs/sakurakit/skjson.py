# coding: utf8
# skjson.py
# 7/4/2014 jichi

from datetime import datetime

# http://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable-in-python
def default_datetime(obj):
  """
  @param  obj  any
  @return  any
  """
  if isinstance(obj, datetime):
    serial = obj.isoformat()
    return serial

if __name__ == '__main__':
  import json
  print json.dumps(datetime.now(), default=default_datetime)

# EOF
