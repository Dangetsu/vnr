# coding: utf8
# 6/25/2013
# See: pip compressinja

__all__ = 'XmlCompressor',

import re
from jinja2.ext import Extension
from jinja2.lexer import Token, describe_token
from jinja2 import TemplateSyntaxError

_re_tag = re.compile(r'(?:<(/?)([a-zA-Z0-9_-]+)\s*|(>\s*))(?s)')
#_ws_normalize_re = re.compile(r'[ \t\r\n]+')
_re_space = re.compile(r'\s+')
_re_word = re.compile(r'\w+')

class StreamProcessContext(object):

  def __init__(self, stream):
    self.stream = stream
    self.token = None
    self.stack = []

  def fail(self, message):
    raise TemplateSyntaxError(message, self.token.lineno,
                  self.stream.name, self.stream.filename)

class XmlCompressor(Extension):

  def enter_tag(self, tag, ctx):
    ctx.stack.append(tag)

  def leave_tag(self, tag, ctx):
    if not ctx.stack:
      ctx.fail('Tried to leave "%s" but something closed '
           'it already' % tag)
    if tag == ctx.stack[-1]:
      ctx.stack.pop()
      return
    for idx, other_tag in enumerate(reversed(ctx.stack)):
      if other_tag == tag:
        for num in xrange(idx + 1):
          ctx.stack.pop()
      else: break

  def normalize(self, ctx):
    pos = 0
    buf = []
    def write_data(value):
      if not _re_word.search(value):
        value = _re_space.sub('', value)
      buf.append(value)

    for match in _re_tag.finditer(ctx.token.value):
      closes, tag, sole = match.groups()
      preamble = ctx.token.value[pos:match.start()]
      write_data(preamble)
      if sole:
        write_data(sole)
      else:
        buf.append(match.group())
        (closes and self.leave_tag or self.enter_tag)(tag, ctx)
      pos = match.end()

    write_data(ctx.token.value[pos:])
    return ''.join(buf)

  def filter_stream(self, stream):
    ctx = StreamProcessContext(stream)
    for token in stream:
      if token.type != 'data':
        yield token
        continue
      ctx.token = token
      value = self.normalize(ctx)
      yield Token(token.lineno, 'data', value)

# EOF
