# coding: utf8
# unilang.py
# 4/30/2015 jichi
import cyrilchars, kochars

def guess_language(text):
  """
  @param  text  unicodoe
  @return  str or None
  """
  if kochars.anyhangul(text):
    return 'ko'
  if cyrilchars.anycyril(text):
    return 'ru'

# EOF
