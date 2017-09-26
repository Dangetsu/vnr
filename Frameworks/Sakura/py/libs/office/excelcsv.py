# coding: utf8
# excelcsv.py
# 8/7/2013 jichi

import codecs, csv

def writer(fp, errors='ignore'):
  """
  @param  fp  file object
  @return  csv.writer
  """
  #fp.write(codecs.BOM_UTF16_LE) # BOM at the beginning
  fp = codecs.getwriter('utf16')(fp, errors=errors)
  fp = csv.writer(fp,
      dialect='excel',
      #delimiter=',', # utf16 ',' cannot be recognized by excel
      delimiter='\t', # excei
      quotechar='"',
      lineterminator='\r', # On windows
      quoting=csv.QUOTE_MINIMAL) # minimize quotes
  return fp

# EOF
