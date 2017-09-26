// hanja2hangulword.cc
// 7/11/2015 jichi

#include "hanjaconv/hanja2hangulword.h"
#include "hanjaconv/hanjadef_p.h"
#include <boost/foreach.hpp>
#include <fstream>
#include <list>
#include <utility> // for pair
#include <vector>

/** Private class */

class HanjaHangulWordConverterPrivate
{
  struct Entry
  {
    std::wstring hanja,     // source
                 hangul;    // target

    void reset(const std::wstring &first, const std::wstring &second)
    {
      hanja = first;
      hangul = second;
    }
  };

  struct Dictionary
  {
    Entry *entries;
    size_t entry_count;

    Dictionary() : entries(nullptr), entry_count(0) {}
    ~Dictionary() { if (entries) delete[] entries; }

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
        if (entries)
          delete[] entries;
        entries = new Entry[size];
        entry_count = size;
      }
    }
  };

public:
  typedef Dictionary dict_type;
  std::vector<dict_type *> dicts;

  ~HanjaHangulWordConverterPrivate()
  {
    for (size_t i = 0; i < dicts.size(); i++)
      delete dicts[i];
  }

  size_t size() const
  {
    size_t ret = 0;
    for (size_t i = 0; i < dicts.size(); i++)
      ret += dicts[i]->entry_count;
    return ret;
  }

  void clear()
  {
    if (!dicts.empty()) {
      for (size_t i = 0; i < dicts.size(); i++)
        delete dicts[i];
      dicts.clear();
    }
  }
};

/** Public class */

// Construction

HanjaHangulWordConverter::HanjaHangulWordConverter() : d_(new D) {}
HanjaHangulWordConverter::~HanjaHangulWordConverter() { delete d_; }

bool HanjaHangulWordConverter::isEmpty() const { return d_->dicts.empty(); }

int HanjaHangulWordConverter::size() const { return d_->size(); }

void HanjaHangulWordConverter::clear() { d_->clear(); }

// Initialization
bool HanjaHangulWordConverter::addDictionary(const wchar_t *path)
{
#ifdef _MSC_VER
  std::wifstream fin(path);
#else
  std::string spath(path, path + ::wcslen(path));
  std::wifstream fin(spath.c_str());
#endif // _MSC_VER
  if (!fin.is_open())
    return false;
  fin.imbue(HANJA_UTF8_LOCALE);

  std::list<std::pair<std::wstring, std::wstring> > lines; // hanja, hangul

  for (std::wstring line; std::getline(fin, line);)
    if (line.size() >= 3 && line[0] != CH_COMMENT) {
      size_t pos = line.find(CH_DELIM);
      if (pos != std::string::npos && 1 <= pos && pos < line.size() - 1)
        lines.push_back(std::make_pair(
            line.substr(0, pos),
            line.substr(pos + 1)));
    }

  fin.close();

  if (lines.empty())
    return false;

  auto dict = new D::dict_type;
  dict->resize(lines.size());

  size_t i = 0;
  BOOST_FOREACH (const auto &it, lines)
    dict->entries[i++].reset(it.first, it.second);

  d_->dicts.push_back(dict);

  return true;
}

// Conversion
void HanjaHangulWordConverter::replace(wchar_t *text) const
{
  if (!text || d_->dicts.empty())
    return;
  size_t size = ::wcslen(text);
  for (size_t di = 0; di < d_->dicts.size(); di++) {
    const auto d = d_->dicts[di];
    for (size_t ei = 0; ei < d->entry_count; ei++) {
      const auto &e = d->entries[ei];
      if (size >= e.hanja.size())
        for (auto p = ::wcsstr(text, e.hanja.c_str());
             p;
             p = ::wcsstr(p + e.hanja.size(), e.hanja.c_str()))
          ::memcpy(p, e.hangul.c_str(), e.hangul.size() * sizeof(wchar_t));
    }
  }
}

std::wstring HanjaHangulWordConverter::lookup(const wchar_t *text) const
{
  if (!text || d_->dicts.empty())
    return std::wstring();
  size_t size = ::wcslen(text);
  for (size_t di = 0; di < d_->dicts.size(); di++) {
    const auto d = d_->dicts[di];
    for (size_t ei = 0; ei < d->entry_count; ei++) {
      const auto &e = d->entries[ei];
      if (size == e.hanja.size() && text == e.hanja)
        return e.hangul;
    }
  }
  return std::wstring();
}

// EOF
