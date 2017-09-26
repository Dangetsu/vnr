# coding: utf8
# msvcrt.py
# 1/4/2013 jichi
# Windows only

import skos
if skos.WIN:
  from ctypes import *

  dll = CDLL('msvcrt')

  malloc = dll.malloc
  malloc.argtype = c_size_t
  malloc.restype = c_void_p

  free = dll.free
  free.argtype = c_void_p
  free.restype = None

  memset = dll.memset
  memset.argtypes = c_void_p, c_int, c_size_t
  memset.restype = c_void_p

  memcpy = dll.memcpy
  memcpy.argtypes = c_void_p, c_void_p, c_size_t
  memcpy.restype = c_void_p

  strcpy = dll.strcpy
  strcpy.argtypes = c_char_p, c_char_p
  strcpy.restype = c_char_p

# EOF
