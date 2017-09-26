# coding: utf8
# sknodebug.py
# 10/10/2012 jichi

DEBUG = False

# Functions
def dprint(msg, *args, **kwargs): pass
def dwarn(msg, *args, **kwargs): pass
def derror(msg, *args, **kwargs): pass

# Declorators
def debugfunc(f): return f
def debugmethod(f): return f

# EOF
