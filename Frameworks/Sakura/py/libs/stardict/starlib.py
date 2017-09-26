# coding: utf8
# 4/25/2015 jichi
# See: https://github.com/pysuxing/python-stardict
from struct import unpack

class IfoFileException(Exception):
  """Exception while parsing the .ifo file.
  Now version error in .ifo file is the only case raising this exception.
  """

  def __init__(self, description = "IfoFileException raised"):
    """Constructor from a description string.

    Arguments:
    - `description`: a string describing the exception condition.
    """
    self._description = description
  def __str__(self):
    """__str__ method, return the description of exception occured.

    """
    return self._description

class IfoFileReader(object):
  """Read infomation from .ifo file and parse the infomation a dictionary.
  The structure of the dictionary is shown below:
  {key, value}
  """

  def __init__(self, filename):
    """Constructor from filename.

    Arguments:
    - `filename`: the filename of .ifo file of stardict.
    May raise IfoFileException during initialization.
    """
    self._ifo = {}
    with open(filename, "r") as ifo_file:
      self._ifo["dict_title"] = ifo_file.readline() # dictionary title
      line = ifo_file.readline() # version info
      key, equal, value = line.partition("=")
      key = key.strip()
      value = value.strip()
      # check version info, raise an IfoFileException if error encounted
      if key != "version":
        raise IfoFileException("Version info expected in the second line of {!r:s}!".format(filename))
      if value != "2.4.2" and value != "3.0.0":
        raise IfoFileException("Version expected to be either 2.4.2 or 3.0.0, but {!r:s} read!".format(value))
      self._ifo[key] = value
      # read in other infomation in the file
      for line in ifo_file:
        key, equal, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        self._ifo[key] = value
      # check if idxoffsetbits should be discarded due to version info
      if self._ifo["version"] == "3.0.0" and "idxoffsetbits" in self._ifo:
        del self._ifo["version"]

  def get_ifo(self, key):
    """Get configuration value.

    Arguments:
    - `key`: configuration option name
    Return:
    - configuration value corresponding to the specified key if exists, otherwise False.
    """
    if key not in self._ifo:
      return False
    return self._ifo[key]

class IdxFileReader(object):
  """Read dictionary indexes from the .idx file and store the indexes in a list and a dictionary.
  The list contains each entry in the .idx file, with subscript indicating the entry's origin index in .idx file.
  The dictionary is indexed by word name, and the value is an integer or a list of integers pointing to
  the entry in the list.
  """

  encoding = 'utf8'

  def __init__(self, filename, compressed=False, index_offset_bits=32):
    """

    Arguments:
    - `filename`: the filename of .idx file of stardict.
    - `compressed`: indicate whether the .idx file is compressed.
    - `index_offset_bits`: the offset field length in bits.
    """
    if compressed:
      import gzip
      with gzip.open(filename, 'rb') as index_file:
        self._content = index_file.read()
    else:
      with open(filename, 'rb') as index_file: # always read as byte since data is binary
        self._content = index_file.read()
    self._offset = 0
    self._index = 0
    self._index_offset_bits = index_offset_bits
    self._word_idx = {}
    self._index_idx = []
    for word_str, word_data_offset, word_data_size, index in self:
      self._index_idx.append((word_str, word_data_offset, word_data_size))
      if word_str in self._word_idx:
        if isinstance(self._word_idx[word_str], list):
          self._word_idx[word_str].append(len(self._index_idx)-1)
        else:
          self._word_idx[word_str] = [self._word_idx[word_str], len(self._index_idx)-1]
      else:
        self._word_idx[word_str] = len(self._index_idx)-1

    # Switch to tuple to save memory
    # Disabled since few indices are list
    #for k,v in self._word_idx.iteritems():
    #  if isinstance(v, list):
    #    self._word_idx[k] = tuple(v)

    del self._content
    del self._index_offset_bits
    del self._index

  def __iter__(self):
    """Define the iterator interface.

    """
    return self

  def next(self):
    """Define the iterator interface.

    """
    if self._offset == len(self._content):
      raise StopIteration
    word_data_offset = 0
    word_data_size = 0
    end = self._content.find('\0', self._offset)
    word_str = self._content[self._offset: end]
    word_str = word_str.decode(self.encoding) # jichi: force using utf8
    self._offset = end+1
    if self._index_offset_bits == 64:
      word_data_offset, = unpack('!I', self._content[self._offset:self._offset+8])
      self._offset += 8
    elif self._index_offset_bits == 32:
      word_data_offset, = unpack('!I', self._content[self._offset:self._offset+4])
      self._offset += 4
    else:
      raise ValueError
    word_data_size, = unpack('!I', self._content[self._offset:self._offset+4])
    self._offset += 4
    self._index += 1
    return (word_str, word_data_offset, word_data_size, self._index)

  def get_index_by_num(self, number):
    """Get index infomation of a specified entry in .idx file by origin index.
    May raise IndexError if number is out of range.

    Arguments:
    - `number`: the origin index of the entry in .idx file
    Return:
    A tuple in form of (word_str, word_data_offset, word_data_size)
    """
    if number >= len(self._index_idx):
      raise IndexError("Index out of range! Acessing the {:d} index but totally {:d}".format(number, len(self._index_idx)))
    return self._index_idx[number]

  def get_index_by_word(self, word_str):
    """Get index infomation of a specified word entry.

    Arguments:
    - `word_str`: name of word entry.
    Return:
    Index infomation corresponding to the specified word if exists, otherwise False.
    The index infomation returned is a list of tuples, in form of [(word_data_offset, word_data_size) ...]
    """
    if word_str not in self._word_idx:
      return False
    number =  self._word_idx[word_str]
    index = []
    if isinstance(number, list):
      for n in number:
        index.append(self._index_idx[n][1:])
    else:
      index.append(self._index_idx[number][1:])
    return index

class SynFileReader(object):
  """Read infomation from .syn file and form a dictionary as below:
  {synonym_word: original_word_index}, in which 'original_word_index' could be a integer or
  a list of integers.
  """

  def __init__(self, filename):
    """Constructor.

    Arguments:
    - `filename`: The filename of .syn file of stardict.
    """
    self._syn = {}
    with open(filename, "r") as syn_file:
      content = syn_file.read()
    offset = 0
    while offset < len(content):
      end = content.find('\0', offset)
      synonym_word = content[offset:end]
      offset = end
      original_word_index = unpack('!I', content[offset, offset+4])
      offset += 4
      if synonym_word in self._syn:
        if isinstance(self._syn[synonym_word], list):
          self._syn[synonym_word].append(original_word_index)
        else:
          self._syn[synonym_word] = [self._syn[synonym_word], original_word_index]
      else:
        self._syn[synonym_word] = original_word_index

  def get_syn(self, synonym_word):
    """

    Arguments:
    - `synonym_word`: synonym word.
    Return:
    If synonym_word exists in the .syn file, return the corresponding indexes, otherwise False.
    """
    if synonym_word not in self._syn:
      return False
    return self._syn[synonym_word]

class DictFileReader(object):
  """Read the .dict file, store the data in memory for querying.
  """

  encoding = 'utf8'

  def __init__(self, filename, dict_ifo, dict_index, caching=False, compressed=None):
    """
    @param  filename  unicode None
    @param  dict_ifo  IfoFileReader
    @param  dict_index  IdxFileReader
    @param* caching  bool  whether read all data into memory
    """
    if compressed is None:
      compressed = filename.endswith('.dz')
    self._dict_ifo = dict_ifo
    self._dict_index = dict_index
    self._compressed = compressed
    self._offset = 0
    self._dict_file = None
    self._dict_file_content = None # string

    if compressed:
      import gzip
      f = gzip.open(filename, "rb")
    else:
      f = open(filename, "rb")
    if caching:
      self._dict_file_content = f.read()
      f.close()
    else:
      self._dict_file = f

  def __del__(self):
    if self._dict_file:
      self._dict_file.close()

  def get_dict_by_word(self, word):
    """Get the word's dictionary data by it's name.
    @return  [unicode] or None

    Arguments:
    - `word`: word name.
    Return:
    The specified word's dictionary data, in form of dict as below:
    {type_identifier: infomation, ...}
    in which type_identifier can be any character in "mlgtxykwhnrWP".
    """
    result = []
    indexes = self._dict_index.get_index_by_word(word)
    if indexes == False:
      return
    sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
    for index in indexes:
      self._offset = index[0]
      size = index[1]
      if sametypesequence:
        result.append(self._get_entry_sametypesequence(size))
      else:
        result.append(self._get_entry(size))
    return result

  def get_dict_by_index(self, index):
    """Get the word's dictionary data by it's index infomation.

    Arguments:
    - `index`: index of a word entrt in .idx file.'
    Return:
    The specified word's dictionary data, in form of dict as below:
    {type_identifier: infomation, ...}
    in which type_identifier can be any character in "mlgtxykwhnrWP".
    """
    word, offset, size = self._dict_index.get_index_by_num(index)
    self._offset = offset
    sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
    if sametypesequence:
      return self._get_entry_sametypesequence(size)
    else:
      return self._get_entry(size)

  def _get_entry(self, size):
    result = {}
    read_size = 0
    start_offset = self._offset
    while read_size < size:
      type_identifier = unpack("!c")
      if type_identifier in "mlgtxykwhnr":
        result[type_identifier] = self._get_entry_field_null_trail()
      else:
        result[type_identifier] = self._get_entry_field_size()
      read_size = self._offset - start_offset
    return result

  def _get_entry_sametypesequence(self, size):
    start_offset = self._offset
    result = {}
    sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
    for k in range(0, len(sametypesequence)):
      if sametypesequence[k] in "mlgtxykwhnr":
        if k == len(sametypesequence)-1:
          result[sametypesequence[k]] = self._get_entry_field_size(size - (self._offset - start_offset))
        else:
          result[sametypesequence[k]] = self._get_entry_field_null_trail()
      elif sametypesequence[k] in "WP":
        if k == len(sametypesequence)-1:
          result[sametypesequence[k]] = self._get_entry_field_size(size - (self._offset - start_offset))
        else:
          result[sametypesequence[k]] = self._get_entry_field_size()
    return result

  def _get_entry_field_null_trail(self):
    """
    @return  unicode
    """
    if self._dict_file_content:
      return self._get_entry_field_null_trail_in_memory(size)
    else:
      return self._get_entry_field_null_trail_in_disk(size)

  def _get_entry_field_size(self, size=None):
    """
    @param  size  int or None
    @return  unicode
    """
    if self._dict_file_content:
      return self._get_entry_field_size_in_memory(size)
    else:
      return self._get_entry_field_size_in_disk(size)

  def _get_entry_field_size_in_memory(self, size=None):
    """
    @param  size  int or None
    @return  unicode
    """
    if size == None:
      size = unpack('!I', self._dict_file_content[self._offset:self._offset+4])
      self._offset += 4
    result = self._dict_file_content[self._offset:self._offset+size]
    self._offset += size
    return result.decode(self.encoding)

  def _get_entry_field_null_trail_in_memory(self):
    """
    @return  unicode
    """
    end = self._dict_file.find('\0', self._offset)
    result = self._dict_file[self._offset:end]
    self._offset = end+1
    return result.decode(self.encoding)

  def _get_entry_field_size_in_disk(self, size=None):
    """
    @param  size  int or None
    @return  unicode
    """
    if size == None:
      size = unpack('!I', self._read_file_at(self._offset, 4))
      self._offset += 4
    result = self._read_file_at(self._offset, size)
    self._offset += size
    return result.decode(self.encoding)

  def _get_entry_field_null_trail_in_disk(self):
    """
    @return  unicode
    """
    result = self._read_file_until(self._offset, '\0')
    self._offset += len(result)
    return result.decode(self.encoding)

  # I/O

  def _read_file_at(self, start, size):
    """
    @param  start  int
    @param  stop  int
    @return  str
    """
    self._dict_file.seek(start)
    return self._dict_file.read(size)

  def _read_file_until(self, start, stop=0, chunk_size=500):
    """
    @param  start  int
    @param* stop  int or char ord of the stop character
    @param* chunk_size == 500
    @return  str
    """
    if isinstance(stop, int):
      stop = chr(stop)
    self._dict_file.seek(start)
    ret = data = self._dict_file.read(chunk_size)
    while data:
      end = data.find(stop)
      if end != -1:
        ret += data[:end]
        break
      else:
        ret += data
      data = self._dict_file.read(chunk_size)
    return ret

def read_idx_file(filename):
  """

  Arguments:
  - `filename`:
  """
  index_file = IdxFileReader(filename)
  for word_str in index_file._word_idx:
    print word_str, ": ", index_file.get_index_by_word(word_str)
  for index in range(0, len(index_file._index_idx)):
    print index, ": ", index_file.get_index_by_num(index)[0]

def read_ifo_file(filename):
  """

  Arguments:
  - `filename`:
  """
  ifo_file = IfoFileReader(filename)
  for key in ifo_file._ifo:
    print key, ":", ifo_file._ifo[key]

if __name__ == '__main__':

  import json, os, sys, time

  sys.path.append('..')

  from sakurakit.skprof import SkProfiler

  def sleep():
    print "sleep: enter"
    #time.sleep(5)
    print "sleep: leave"

  #dictdir = '../../../../../../Caches/Dictionaries/OVDP/NhatViet/'
  dictdir = '../../../../../../Caches/Dictionaries/StarDict'
  dictdir += '/hanja/'
  #dictdir += '/hangul/'

  if os.name == 'nt':
    dictdir = 'z:' + dictdir

  sleep()

  with SkProfiler("init"):

    #ifo_file = dictdir + 'star_nhatviet.ifo'
    #idx_file = dictdir + 'star_nhatviet.idx'
    #dict_file = dictdir + 'star_nhatviet.dict'

    ifo_file = dictdir + 'Hanja_KoreanHanzi_Dic.ifo'
    idx_file = dictdir + 'Hanja_KoreanHanzi_Dic.idx'
    dict_file = dictdir + 'Hanja_KoreanHanzi_Dic.dict.dz'

    #sleep()
    ifo_reader = IfoFileReader(ifo_file)
    #sleep()
    idx_reader = IdxFileReader(idx_file)
    #sleep()
    dict_reader = DictFileReader(dict_file, ifo_reader, idx_reader)

  sleep()

  with SkProfiler("query"):
    index = 10
    r = dict_reader.get_dict_by_index(index)
  print json.dumps(r, indent=2, ensure_ascii=False)

  #t = u"勝つ"
  #t = u"かわゆい"
  #t = u"可愛い"
  #t = u"万歳"
  #t = u'冗談'
  t = u'愛'
  r = dict_reader.get_dict_by_word(t)
  print len(r)
  print type(r[0]['m'])
  print r[0]['m']

  sleep()

# EOF
