# coding: utf8
# growl.py
# 10/28/2012 jichi

from sakurakit.skdebug import dprint, dwarn, derror

def show(async=False): pass
def msg(text, async=False): dprint(text)
def warn(text, async=False): dwarn(text)
def error(text, async=False): derror(text)
def notify(text, async=False): dprint(text)

# EOF
