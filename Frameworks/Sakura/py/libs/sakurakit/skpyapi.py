# coding: utf8
# skpyapi.py
# 10/21/2012 jichi

from ctypes import pythonapi, c_void_p, py_object, ArgumentError

# See: http://docs.python.org/2/c-api/cobject.html
pythonapi.PyCObject_AsVoidPtr.restype = c_void_p
pythonapi.PyCObject_AsVoidPtr.argtypes = [py_object]

pythonapi.PyCObject_FromVoidPtr.restype = py_object
pythonapi.PyCObject_FromVoidPtr.argtypes = [c_void_p, c_void_p]

def lp_from_pycobj(pycobj):
  """
  @param  pyobject  PyObject
  @return  ctypes.voidp

  Equivalent to reinterpret_cast<void *>(obj)
  See: http://www.expobrain.net/2011/02/22/handling-win32-windows-handler-in-pyside/
  """
  try:
    return pythonapi.PyCObject_AsVoidPtr(pycobj)
  except ArgumentError:
    return pycobj

def pycobj_from_lp(lp):
  """
  @param  ctypes.voidp
  @return  pyobject  PyObject
  """
  try:
    return pythonapi.PyCObject_FromVoidPtr(lp, 0)
  except ArgumentError:
    return lp

def is_not_method(f):
  return not f or not hasattr(f, '__self__')

# EOF
