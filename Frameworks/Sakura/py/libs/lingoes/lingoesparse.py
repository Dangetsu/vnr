# coding: utf8
# lingoesparse.py
# 1/15/2013 jichi
#
# LD2 and LDX
# http://code.google.com/p/lingoes-extractor/source/browse/trunk/src/cn/kk/extractor/lingoes/LingoesLd2Extractor.java
# https://code.google.com/p/dict4cn/source/browse/trunk/importer/src/LingoesLd2Reader.java
# http://devchina.wordpress.com/2012/03/01/lingoes%E7%81%B5%E6%A0%BC%E6%96%AF%E7%94%B5%E5%AD%90%E8%AF%8D%E5%85%B8ld2ldf%E6%96%87%E4%BB%B6%E8%A7%A3%E6%9E%90java/
# http://www.cnblogs.com/SuperBrothers/archive/2012/11/24/2785971.html
#
# StarDict
# https://code.google.com/p/dict4cn/source/browse/trunk/importer/src/LingoesLd2Reader.java
#
# LD2
# - 0:3: string '?LD2'
# - 0x18: short version (2)
# - 0x1c: long id
#
# - 0x5c: int offset - 0x60

__all__ = 'parse', 'parsefile'

if __name__ == '__main__':
  import sys
  sys.path.append("..")

import zlib
from sakurakit.skdebug import dprint, dwarn
import byteutil

def parsefile(path, *args, **kwargs):
  try:
    with open(path, 'rb') as f:
      return parse(f.read(), *args, **kwargs)
  except Exception, e:
    dwarn(e)

def parse(data, *args, **kwargs):
  """
  @param  data  string
  @param  inenc  string
  @param  outenc  string
  @param* callback  function(unicode word, [unicode] xmls)
  @return  None or [(unicode word, [unicode] xmls]
  """
  if data:
    try:
      filetype = data[:4] # string
      assert filetype == '?LD2'
      version = byteutil.toshort(data, 0x18)
      assert version == 2

      #fileId = byteutil.tolong(data, 0x1c) # not used

      # Intro
      dataOffset = byteutil.toint(data, 0x5c) + 0x60
      introType = byteutil.toint(data, dataOffset)
      introOffset = byteutil.toint(data, dataOffset + 4) + dataOffset + 12
      if introType == 3: # without additional information
        return _parsedict(data, dataOffset, *args, **kwargs)
      elif len(data) > introOffset - 0x1c:
        return _parsedict(data, introOffset, *args, **kwargs) # skip the intro
      else:
        dwarn("invalid or corrupted file")
    except Exception, e:
      dwarn(e)

def _parsedict(data, offset, *args, **kwargs): # str, int; may raise out-of-bound exception
  # Dictionary type
  dictType = byteutil.toint(data, offset) # int
  assert dictType == 3
  #System.out.println("词典类型：0x" + Integer.toHexString(data.getInt(offset)))
  limit = byteutil.toint(data, offset + 4) + offset + 8 # int
  offsetIndex = offset + 0x1c
  offsetCompressedDataHeader = byteutil.toint(data, offset + 8) + offsetIndex
  inflatedWordsIndexLength = byteutil.toint(data, offset + 12)
  inflatedWordsLength = byteutil.toint(data, offset + 16)
  inflatedXmlLength = byteutil.toint(data, offset + 20)

  definitions = (offsetCompressedDataHeader - offsetIndex) / 4 # for debugging only
  dprint("number of definitions = %i" % definitions)

  #data.position(offsetCompressedDataHeader + 8)
  pos = offsetCompressedDataHeader + 8
  it = byteutil.toint(data, pos)
  pos += 4 # skip the index offset

  #deflateStreams = byteutil.iterint32(data, indexOffset, limit) # [int]
  deflateStreams = [] #[ int]
  while (it + pos) < limit:
    it = byteutil.toint(data, pos)
    pos += 4
    deflateStreams.append(it)

  inflatedBytes = _inflate(data, deflateStreams, pos) # [byte]
  if inflatedBytes:
    return _extract(inflatedBytes, inflatedWordsIndexLength, inflatedWordsIndexLength + inflatedWordsLength, *args, **kwargs)

  #final int offsetCompressedData = data.position()
  #System.out.println("索引词组数目：" + definitions)
  #System.out.println("索引地址/大小：0x" + Integer.toHexString(offsetIndex) + " / " + (offsetCompressedDataHeader - offsetIndex) + " B")
  #System.out.println("压缩数据地址/大小：0x" + Integer.toHexString(offsetCompressedData) + " / " + (limit - offsetCompressedData) + " B")
  #System.out.println("词组索引地址/大小（解压缩后）：0x0 / " + inflatedWordsIndexLength + " B")
  #System.out.println("词组地址/大小（解压缩后）：0x" + Integer.toHexString(inflatedWordsIndexLength) + " / " + inflatedWordsLength + " B")
  #System.out.println("XML地址/大小（解压缩后）：0x" + Integer.toHexString(inflatedWordsIndexLength + inflatedWordsLength) + " / " + inflatedXmlLength + " B")
  #System.out.println("文件大小（解压缩后）：" + ((inflatedWordsIndexLength + inflatedWordsLength + inflatedXmlLength) / 1024) + " KB")

def _inflate(data, deflateStreams, dataOffset): # str, [int], int -> str; may raise
  offset = -1
  lastOffset = dataOffset
  ret = ''
  for relativeOffset in deflateStreams:
    offset = dataOffset + relativeOffset
    ret += zlib.decompress(data[lastOffset:offset]) # Could raise gzip error
    lastOffset = offset
  return ret

def _extract(inflatedBytes, offsetDefs, offsetXml, *args, **kwargs): # str, int, int
  dataLen = 10
  defTotal = (offsetDefs / dataLen) - 1

  callback = kwargs.get('callback') # function

  pos = 8
  failCounter = 0
  ret = []
  for i in xrange(defTotal):
    t = _parseentry(inflatedBytes, offsetDefs, offsetXml, dataLen, i, *args, **kwargs)
    if t:
      if callback:
        callback(*t)
      else:
        ret.append(t)
  return ret

def _getIdxData(dataRawBytes, position):  # str, int -> [int]
  return [
    byteutil.toint(dataRawBytes, position),
    byteutil.toint(dataRawBytes, position + 4),
    byteutil.tobyte(dataRawBytes, position + 8),
    byteutil.tobyte(dataRawBytes, position + 9),
    byteutil.toint(dataRawBytes, position + 10),
    byteutil.toint(dataRawBytes, position + 14),
  ]

def _parseentry(inflatedBytes, offsetWords, offsetXml, dataLen, idx, inenc, outenc, **kwargs): # str, int, int, int, int;  may raise encoding error
  wordIdxData = _getIdxData(inflatedBytes, dataLen * idx)
  lastWordPos = wordIdxData[0]
  lastXmlPos = wordIdxData[1]
  refs = wordIdxData[3]
  currentWordOffset = wordIdxData[4]
  currentXmlOffset = wordIdxData[5]

  #print currentXmlOffset - lastXmlPos >  offsetXml + lastXmlPos
  xmls = []
  if currentXmlOffset > lastXmlPos:
    t = inflatedBytes[offsetXml + lastXmlPos : offsetXml+ currentXmlOffset]
    t = t.decode(outenc)
    xmls.append(t)
  for i in range(refs): # use range since refs is usually within 2
    ref = byteutil.toint(inflatedBytes, offsetWords + lastWordPos)
    wordIdxData = _getIdxData(inflatedBytes, dataLen * ref)
    lastXmlPos = wordIdxData[1]
    currentXmlOffset = wordIdxData[5]
    if currentXmlOffset > lastXmlPos:
      t = inflatedBytes[offsetXml + lastXmlPos: currentXmlOffset + offsetXml]
      t = t.decode(outenc)
      xmls.append(t)
    lastWordPos += 4
  if xmls:
    #word = inflatedBytes[offsetWords + lastWordPos + 4: currentWordOffset + offsetWords]
    word = inflatedBytes[offsetWords + lastWordPos: currentWordOffset + offsetWords]
    word = word.decode(inenc)
    return word, xmls

# EOF
