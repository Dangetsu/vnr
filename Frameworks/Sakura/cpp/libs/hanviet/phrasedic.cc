// phrasedic.cc
// 2/2/2015 jichi

#include "hanviet/phrasedic.h"
#include "cpputil/cpplocale.h"
#include "unistr/unichar.h"
#include "trrender/trescape.h" // cross module include is bad
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
#include <fstream>
#include <iterator>
#include <list>
#include <stack>
#include <utility>
//#include <iostream>
//#include <QDebug>

/** Helpers */

namespace { // unnamed

enum : char {
  CH_COMMENT = L'#'  // beginning of a comment
  , CH_HAN_DELIM = L'='
  , CH_VIET_DELIM = L'/'
};

const std::locale UTF8_LOCALE = ::cpp_utf8_locale<wchar_t>();

struct HanVietPhraseEntry
{
  std::wstring han,     // source
               viet;    // target

  void reset(const std::wstring &first, const std::wstring &second)
  {
    han = first;
    viet = second;
  }

  std::wstring first_viet() const
  {
    size_t i = viet.find(CH_VIET_DELIM);
    return i == std::string::npos ? viet : viet.substr(0, i);
  }

  std::wstring render() const
  {
    size_t i = viet.find(CH_VIET_DELIM);
    if (i == std::string::npos)
      return viet;
    std::wstring first = viet.substr(0, i);

    std::wstring ret = L"{\"type\":\"tip\"";

    std::string t = ::trescape(han);
    ret.append(L",\"source\":\"")
       .append(t.cbegin(), t.cend())
       .push_back('"');

    t = ::trescape(viet);
    ret.append(L",\"target\":\"")
       .append(t.cbegin(), t.cend())
       .push_back('"');

    ret.push_back('}');

    ret.insert(0, L"<a href='json://");
    ret.push_back('\'');

    ret.push_back('>');
    ret.append(first)
       .append(L"</a>");
    return ret;
  }
};

// Needed by analysis

struct Segment
{
  std::wstring source, target;
  const HanVietPhraseEntry *phrase;

  Segment() : phrase(nullptr) {}
  explicit Segment(const HanVietPhraseEntry *phrase) : phrase(phrase) {}
  explicit Segment(const std::wstring &source, const std::wstring &target = std::wstring())
    : source(source), target(target), phrase(nullptr) {}
};

typedef std::list<Segment> SegmentList;
struct SegmentIndex
{
  size_t start, length;
  SegmentList::iterator it;

  explicit SegmentIndex(size_t start = 0, size_t length = 0, SegmentList::iterator it = SegmentList::iterator())
    : start(start), length(length), it(it) {}
};

} // unnamed namespace

/** Private class */

class HanVietPhraseDictionaryPrivate
{
public:
  typedef HanVietPhraseEntry entry_type;

  entry_type *entries;
  size_t entry_count;

  HanVietPhraseDictionaryPrivate() : entries(nullptr), entry_count(0) {}
  ~HanVietPhraseDictionaryPrivate() { if (entries) delete[] entries; }

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
      entries = new entry_type[size];
      entry_count = size;
    }
  }
};

/** Public class */

// Construction

HanVietPhraseDictionary::HanVietPhraseDictionary() : d_(new D) {}
HanVietPhraseDictionary::~HanVietPhraseDictionary() { delete d_; }

int HanVietPhraseDictionary::size() const { return d_->entry_count; }
bool HanVietPhraseDictionary::isEmpty() const { return !d_->entry_count; }

void HanVietPhraseDictionary::clear() { d_->clear(); }

// Initialization
bool HanVietPhraseDictionary::addFile(const std::wstring &path)
{
#ifdef _MSC_VER
  std::wifstream fin(path);
#else
  std::string spath(path.begin(), path.end());
  std::wifstream fin(spath.c_str());
#endif // _MSC_VER
  if (!fin.is_open())
    return false;
  fin.imbue(UTF8_LOCALE);

  std::list<std::pair<std::wstring, std::wstring> > lines; // han, viet

  for (std::wstring line; std::getline(fin, line);)
    if (line.size() >= 3 && line[0] != CH_COMMENT) {
      size_t pos = line.find(CH_HAN_DELIM);
      if (pos != std::string::npos && 1 <= pos && pos < line.size() - 1)
        lines.push_back(std::make_pair(
            line.substr(0, pos),
            line.substr(pos + 1)));
    }

  fin.close();

  if (lines.empty()) {
    d_->clear();
    return false;
  }

  //QWriteLocker locker(&d_->lock);
  d_->resize(lines.size());

  size_t i = 0;
  BOOST_FOREACH (const auto &it, lines)
    d_->entries[i++].reset(it.first, it.second);

  return true;
}

// Conversion

std::wstring HanVietPhraseDictionary::lookup(const std::wstring &text) const
{
  if (text.empty() || !d_->entries) // at least two elements
    return std::wstring();
  for (size_t i = 0; i < d_->entry_count; i++) {
    const auto &e = d_->entries[i];
    if (e.han == text)
      return e.viet;
  }
  return std::wstring();
}

std::wstring HanVietPhraseDictionary::translate(const std::wstring &text, bool mark) const
{
  if (text.empty() || !d_->entries) // at least two elements
    return text;

  enum : wchar_t { delim = L' ' };

  std::wstring ret = text;

  size_t free_size = text.size();
  for (size_t i = 0; i < d_->entry_count && free_size; i++) {
    const auto &e = d_->entries[i];
    if (e.han.size() <= free_size && boost::contains(ret, e.han)) {
      std::wstring repl = mark ? e.render() : e.first_viet();
      repl.push_back(delim);
      boost::replace_all(ret, e.han, repl);
      free_size -= e.han.size(); // should subtract number of matches, which I don't know how ot get
    }
  }

  return ret;
}

std::wstring HanVietPhraseDictionary::analyze(const std::wstring &text, bool mark,
                                              const align_fun_t &align, const transform_fun_t &fallback) const
{
  if (text.empty() || !d_->entries) // at least two elements
    return text;

  enum : wchar_t { delim = L' ' };

  SegmentList segs;
  std::stack<SegmentIndex> indices;

  indices.push(SegmentIndex(
       0, text.size(),  segs.end()));

  while (!indices.empty()) {
    auto top = indices.top();
    indices.pop();
    std::wstring source = text.substr(top.start, top.length);

    bool found = false;
    for (size_t i = 0; i < d_->entry_count; i++) {
      const auto &e = d_->entries[i];
      if (e.han.size() <= source.size()) {
        auto pos = source.find(e.han);
        if (pos != std::string::npos) {
          segs.insert(top.it, Segment(&e));
          if (pos > 0)
            indices.push(SegmentIndex(
                top.start, pos, std::prev(top.it)));
          size_t offset = pos + e.han.size();
          if (offset < source.size())
            indices.push(SegmentIndex(
                top.start + offset, top.length - offset, top.it));
          found = true;
          break;
        }
      }
    }
    if (!found) {
      if (fallback)
        segs.insert(top.it, Segment(source, fallback(source)));
      else
        segs.insert(top.it, Segment(source));
    }
  }

  std::wstring ret;
  BOOST_FOREACH (const auto &seg, segs)
    if (auto p = seg.phrase) {
      if (align)
        align(p->han, p->first_viet());
      ret.append(mark ? p->render() : p->first_viet())
         .push_back(delim);
    } else if (seg.target.empty() || seg.target == seg.source)
      ret.append(seg.source);
    else {
      if (align)
        align(seg.source, seg.target);
      ret.append(seg.target);
    }
  return ret;
}

// EOF
