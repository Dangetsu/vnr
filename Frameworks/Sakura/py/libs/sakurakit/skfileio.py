# coding: utf8
# skfileio.py
# 11/10/2012 jichi
import os, re
import skstr
from skdebug import dprint, dwarn

## Parsing file names ##

_repl_escape = skstr.multireplacer({
  #"'": '', # remove
  '"': '', # remove
  '?': u'？',
  '*': u'＊',
  ':': u'：',
  '<': u'＜',
  '>': u'＞',
  '/': u'／',
  '|': '-',
  '\\': '-',
  '\t': ' ',
}) #, escape=True
def escape(name):
  """
  @param  name  unicode
  @return  unicode
  """
  return _repl_escape(name).strip() if name else ''

# http://stackoverflow.com/questions/7287996/python-get-relative-path-from-comparing-two-absolute-paths
def relpaths(paths): # [unicode] -> [unicode]
  path = map(os.path.abspath, paths)
  prefix = os.path.commonprefix(paths)
  return [os.path.relpath(path, prefix) for path in paths]

def realpath(path, prefix): # unicode, unicode -> unicode
  return os.path.relpath(os.path.abspath(path), os.path.abspath(prefix))

# Escape brackets in glob
# http://edgylogic.com/blog/escaping-square-brackets-pythons-glob/
def escapeglob(path): # unicode -> unicode
  if '[' not in path:
    return path
  path = re.sub(r'\[', '[[]', path)
  path = re.sub(r'(?<!\[)\]', '[]]', path)
  return path

## Read and write ##

def readfile(path, mode='r'):
  """
  @param  path  str
  @param  mode  str  'r' or 'rb'
  @return  unicode or ""
  """
  try:
    with open(path, mode) as f:
      return f.read()
  except IOError: pass
  except UnicodeDecodeError, e: dwarn(e)
  except Exception, e: dwarn(e)
  return ""

def readdata(path): return readfile(path, mode='rb')

def writefile(path, data, mode='w'):
  """
  @param  path  str
  @param  data  str
  @param  mode  str  'w' or 'wb'
  @return  bool
  """
  try:
    with open(path, mode) as f:
      f.write(data)
    return True
  except IOError: pass
  except UnicodeEncodeError, e: dwarn(e)
  except Exception, e: dwarn(e)
  return False

def iterwritefile(path, iterdata, mode='w', flush=True):
  """
  @param  path  str
  @param  iterdata [str]
  @param  mode  str  'w' or 'wb'
  @return  bool
  """
  try:
    with open(path, mode) as f:
      for it in iterdata:
        f.write(it)
        if flush:
          f.flush()
    return True
  except IOError: pass
  except UnicodeEncodeError, e: dwarn(e)
  except Exception, e: dwarn(e)
  return False

def writedata(path, data, **kwargs): return writefile(path, data, mode='wb', **kwargs)
def iterwritedata(path, iterdata, **kwargs): return iterwritefile(path, terdata, mode='wb', **kwargs)

def copyfile(src, dst):
  """
  @param  src  str  path
  @param  dst  str  path
  @return  bool
  """
  try:
    import shutil
    shutil.copyfile(src, dst)
    return True
  except: return False

def removefile(path):
  """
  @param  path  str
  @return  bool
  """
  dprint(path)
  try: os.remove(path); return True
  except: return False

def makedirs(path):
  try:
    if not os.path.exists(path):
      os.makedirs(path)
    return True
  #except OSError:
  except Exception:
    dwarn("failed to create directory: %s" % path)
    return False

def removetree(path): # remove the whole directory recursively
  """
  @param  path  str
  @return  bool
  """
  try:
    if os.path.exists(path):
      dprint(path)
      import shutil
      shutil.rmtree(path)
    return True
  except: return False

def emptydir(path):
  """
  @param  path  str
  @return  bool

  FIXME: This implementation is very slow.
  """
  try: return bool(os.listdir(work_path))
  except: return False

def listdirs(path):
  """Return directories in path
  @param  path
  @return  [unicode]
  """
  try: return [os.path.join(path, it) for it in os.listdir(path) if os.path.isdir(path)]
  except: return []

def listfiles(path):
  """Return files in path
  @param  path
  @return  [unicode]
  """
  try: return [os.path.join(path, it) for it in os.listdir(path) if os.path.isfile(path)]
  except: return []

def trashfile(path):
  """
  @param  path  str or unicode
  @return  bool  if succeed
  """
  import skos
  if skos.WIN:
    import skwin
    # The send2trash is broken for windows. Use my own version instead
    return skwin.trash_file(path)
  else:
    from send2trash import send2trash
    try:
      send2trash(path)
      return True
    except OSError, e:
      dwarn("failed to delete file %s, exception:" % path, e)
      return False

def touchfile(path):
  """
  @param  path
  @return  bool
  """
  try:
    if not os.path.exists(path):
      open(path, 'w+').close()
    return True
  except: return False

def rename(src, dst):
  """
  @param  src  str
  @param  dst  str
  @return  bool
  """
  try: os.rename(src, dst); return True
  except: return False

def filecreatetime(path):
  """
  @return  long
  """
  try: return os.path.getctime(path)
  except: return 0

def fileupdatetime(path):
  """
  @return  long
  """
  try: return os.path.getmtime(path)
  except: return 0

def filesize(path):
  """
  @return  int
  """
  try: return os.stat(path).st_size
  except: return 0

def fileempty(path):
  """
  @return  bool
  """
  return filesize(path) == 0

# Directory navigation

# http://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
def getfirstchildfile(path): # unicode -> unicode or None
  try:
    parent, dirs, files = os.walk(path).next()
    return os.path.join(parent, files[0])
  except Exception, e:
    dwarn(e)

# http://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
def getfirstchilddir(path): # unicode -> unicode or None
  try:
    parent, dirs, files = os.walk(path).next()
    return os.path.join(parent, dirs[0])
  except Exception, e:
    dwarn(e)

# Compression

def extractarchive(path, location, type, *args, **kwargs):
  """
  @param  path  unicode
  @param  location  unicode
  @param  type  str
  @return  bool
  """
  if type == 'tar':
    x = extracttar
  elif type == 'zip':
    x = extractzip
  elif type == 'xz':
    x = extractxz
  elif type == '7z':
    x = extract7z
  else:
    dwarn("unknown archive type = %s" % type)
    return False
  return x(path, location, *args, **kwargs)

# http://docs.python.org/2/library/tarfile.html
# mode: r, r:, r:gz, r:bz2
# http://stackoverflow.com/questions/740820/python-write-string-directly-to-tarfile
def extracttar(path, location, mode='r'): # unicode, unicode -> bool
  """
  @param  path  unicode
  @param  location  unicode
  @param* mode  str
  @return  bool
  """
  import tarfile
  try:
    #with tarfile.TarFile(path) as z: # without extraction
    with tarfile.open(path, mode) as z:
      z.extractall(location)
      return True
  except Exception, e:
    dwarn(e)
  return False

def extracttargz(path, location): return extracttar(path, location, 'r:gz')
def extracttarbz2(path, location): return extracttar(path, location, 'r:bz2')
extracttgz = extracttargz
extracttbz2 = extracttarbz2

# http://stackoverflow.com/questions/9431918/extracting-zip-file-contents-to-specific-directory-in-python-2-7
def extractzip(path, location): # unicode, unicode -> bool
  """
  @param  path  unicode
  @param  location  unicode
  @return  bool
  """
  import zipfile
  try:
    with zipfile.ZipFile(path, 'r') as z:
      z.extractall(location)
      return True
  except Exception, e:
    dwarn(e)
  return False

# Python 3 is different
# github.com/fancycode/pylzma/blob/master/doc/usage.txt
# http://stackoverflow.com/questions/10701528/example-of-how-to-use-pylzma
def extractxz(infile, outfile): # unicode, unicode -> bool
  """
  @param  infile  unicode
  @param  outfile  unicode
  @return  bool
  """
  import pylzma
  try:
    with open(infile, 'rb') as i:
      with open(outfile, 'wb') as o:
        z = pylzma.decompressobj()
        while True:
          data = i.read(1)
          if not data: break
          o.write(z.decompress(data))
        o.write(z.flush())
  except Exception, e:
    dwarn(e)
  return False

# Only needed by Python2. tar.xz is supported by Python3 by default.
# http://stackoverflow.com/questions/10701528/example-of-how-to-use-pylzma
# http://stackoverflow.com/questions/17217073/how-to-decompress-a-xz-file-which-has-multiple-folders-files-inside-in-a-singl
def extracttarxz(path, location): # unicode, unicode -> bool
  """
  @param  path  unicode
  @param  location  unicode
  @return  bool
  """
  try:
    import pylzma
    with open(path, 'rb') as fp:
      z = pylzma.decompressobj()
      data = ''
      while True:
        trunk = fp.read(1)
        if not trunk: break
        data += z.decompress(trunk)
      data += z.flush()
    import tarfile
    from cStringIO import StringIO
    with tarfile.open(mode= "r:", fileobj=StringIO(data)) as t:
      t.extractall(location)
      return True
  except Exception, e:
    dwarn(e)
  return False

  #import contextlib, tarfile, lzma
  #try:
  #  with contextlib.closing(lzma.LZMAFile(path)) as xz:
  #    with tarfile.open(fileobj=xz) as f:
  #      f.extractall(location)
  #      return True
  #except Exception, e:
  #  dwarn(e)
  #return False

# http://stackoverflow.com/questions/10701528/example-of-how-to-use-pylzma
# http://www.dreamincode.net/forums/topic/296783-how-to-cope-with-the-occasional-administrator-privledge-requirement/
# Only needed by Python2. 7zip is supported by Python3 by default.
# Note: This require pylzma to be installed first
# FIXME: py7zlib does not support latest 7zip

def extract7zarchive(z, location): # py7zlib.Archive7z, unicode ->, throws
  """
  @param  z  file object
  @param  location  unicode
  @return  bool
  """
  for name in z.getnames():
    outfile = os.path.join(location, name)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    with open(outfile, 'wb') as f:
      f.write(z.getmember(name).read())

# Warning: This only support 7z version 0.3 and does not support 7z 0.4
# Warning: This could cause out of memory error
def extract7z(path, location): # unicode, unicode -> bool
  """
  @param  path  unicode
  @param  location  unicode
  @return  bool
  """
  import py7zlib # could be found in pylzma from pip
  try:
    with open(path, 'rb') as fp:
      z = py7zlib.Archive7z(fp)
      extract7zarchive(z, location)
      return True
  except Exception, e:
    dwarn(e)
  return False

if __name__ == '__main__':
  #f = '/Users/jichi/tmp/unidic-2.1.2.7z'
  f = r'S:\Stream\Caches\tmp\unidic-mlj.7z'
  extract7z(f, 'tmp')

# EOF
