#ifndef HANGUL2HANJA_P_H
#define HANGUL2HANJA_P_H

// hangul2hanja_p.h
// 1/6/2015 jichi

#include "hanjaconv/hangul2hanja.h"
#include <boost/foreach.hpp>

/** Private class */

class HangulHanjaConverterPrivate
{
  typedef HangulHanjaConverter Q;
  struct Entry
  {
    std::wstring hangul,  // source
                 hanja;   // target

    void reset(const std::wstring &first, const std::wstring &second)
    {
      hangul = first;
      hanja = second;
    }
  };

public:
  typedef Entry entry_type;

  entry_type *entries;
  size_t entry_count;

  HangulHanjaConverterPrivate() : entries(nullptr), entry_count(0) {}
  ~HangulHanjaConverterPrivate() { if (entries) delete[] entries; }

  void clear()
  {
    entry_count = 0;
    if (entries) {
      delete[] entries;
      entries = nullptr;
    }
  }

  void resize(size_t size)
  {
    //Q_ASSERT(size > 0);
    if (entry_count != size) {
      clear(); // clear first for thread-safety
      if (size) {
        entries = new entry_type[size];
        entry_count = size;
      }
    }
  }

  void reset(const std::list<std::pair<std::wstring, std::wstring> > &lines) // hanja, hangul
  {
    if (lines.empty())
      clear();
    else {
      resize(lines.size());

      size_t i = 0;
      BOOST_FOREACH (const auto &it, lines)
        entries[i++].reset(it.first, it.second);
    }
  }

  // Replace hangul with hanja in text
  void replace(std::wstring &text) const;
  // Detect (hangul, hanja) pairs and pass to fun
  void collect(const wchar_t *text, size_t size, const Q::collect_fun_t &fun) const;

  // Helpers
private:
  /** Replace only at text[start].
   *  @param  text  target text to replace
   *  @param  start  offset of the text to look at
   */
  size_t replace_first(std::wstring &text, size_t start) const;

  /** Collect only at text[start].
   *  @param  text  target text to parse
   *  @param  size  target text size
   *  @param  start  offset of the text to look at
   *  @param  last  where last collect happens
   *  @param  fun
   */
  size_t collect_first(const wchar_t *text, size_t size,
                       size_t start, size_t last,
                       const Q::collect_fun_t &fun) const;
};

#endif // HANGUL2HANJA_P_H
