#pragma once

// textunion.h
// 8/29/2015 jichi
// No idea why these structures appear a lot.

#include "engine/engineutil.h"

struct TextUnionA
{
  enum { ShortTextCapacity = 0x10 }; // including \0

  union {
    const char *text;
    char chars[ShortTextCapacity];
  };
  int size,
      capacity; // excluding \0

  bool isValid() const
  {
    if (size <= 0 || size > capacity)
      return false;
    const char *t = getText();
    return Engine::isAddressWritable(t, size) && ::strlen(t) == size;
  }

  const char *getText() const
  { return size < ShortTextCapacity ? chars : text; }

  void setText(const char *_text, int _size)
  {
    if (_size < ShortTextCapacity)
      ::memcpy(chars, _text, _size + 1);
    else
      text = _text;
    capacity = size = _size;
  }

  void setLongText(const char *_text, int _size)
  {
    text = _text;
    size = _size;
    capacity = qMax<size_t>(ShortTextCapacity, _size);
  }

  void setText(const QByteArray &text)
  { setText(text.constData(), text.size()); }
  void setLongText(const QByteArray &text)
  { setLongText(text.constData(), text.size()); }
};

struct TextUnionW
{
  enum { ShortTextCapacity = 8 };

  union {
    const wchar_t *text; // 0x0
    wchar_t chars[ShortTextCapacity];
  };
  int size, // 0x10
      capacity;

  bool isValid() const
  {
    if (size <= 0 || size > capacity)
      return false;
    const wchar_t *t = getText();
    return Engine::isAddressWritable(t, size) && ::wcslen(t) == size;
  }

  const wchar_t *getText() const
  { return size < ShortTextCapacity ? chars : text; }

  void setText(const wchar_t *_text, int _size)
  {
    if (_size < ShortTextCapacity)
      ::memcpy(chars, _text, (_size + 1) * sizeof(wchar_t));
    else
      text = _text;
    capacity = size = _size;
  }

  void setLongText(const wchar_t *_text, int _size)
  {
    text = _text;
    size = _size;
    capacity = qMax<size_t>(ShortTextCapacity, _size);
  }

  void setText(const QString &text)
  { setText((const wchar_t *)text.utf16(), text.size()); }
  void setLongText(const QString &text)
  { setLongText((const wchar_t *)text.utf16(), text.size()); }
};

// EOF
