// qtdynsjis.cc
// 6/3/2015 jichi
// http://en.wikipedia.org/wiki/Shift_JIS
#include "qtdyncodec/qtdynsjis.h"
#include <QtCore/QTextCodec>

#ifdef __clang__
# pragma GCC diagnostic ignored "-Wlogical-op-parentheses"
#endif // __clang__

//#ifdef _MSC_VER
//# pragma warning(disable:4018) // C4018: signed/unsigned mismatch
//#endif // _MSC_VER

//#define SK_NO_QT
//#define DEBUG "dynsjis.cc"
//#include "sakurakit/skdebug.h"

/** Private class */

// See also LeadByte table for Windows:
//
// BYTE LeadByteTable[0x100] = {
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
//   2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
//   2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//   2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
//   2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1
// };
//
// -2: 0x00 and 0xff are skipped

class DynamicShiftJISCodecPrivate
{
public:
  QTextCodec *codec; // sjis codec
  std::wstring text; // already saved characters

  uint minimumSecondByte;

  explicit DynamicShiftJISCodecPrivate(QTextCodec *codec)
    : codec(codec ? codec : QTextCodec::codecForName("Shift_JIS"))
    , minimumSecondByte(0)
  {}

  size_t capacity() const
  {
    // See: http://en.wikipedia.org/wiki/Shift_JIS
    return // = 7739
      (3 * 16 - 1) * (4 * 16 + 4 - 1 - minimumSecondByte) // = 3149, 0x00 are skipped
      + (16 + 2) * (256 - 1 - minimumSecondByte) // = 4590, first/last byte unused
    ;
  }
  bool isFull() const { return text.size() >= capacity(); }

  QByteArray encode(const wchar_t *text, size_t length, bool *dynamic);
  QString decode(const char *data, size_t length, bool *dynamic) const;

private:
  QByteArray encodeChar(wchar_t ch);
  wchar_t decodeChar(quint8 ch1, quint8 ch2) const;
};

// Encode

QByteArray DynamicShiftJISCodecPrivate::encode(const wchar_t *text, size_t length, bool *dynamic)
{
  QByteArray ret;
  for (size_t i = 0; i < length; i++) {
    wchar_t ch = text[i];
    if (ch <= 127)
      ret. push_back(ch);
    else {
      QChar qch(ch);
      QByteArray data = codec->fromUnicode(&qch, 1);
      if (data.size() == 1 && (!data[0] || data[0] == '?')) { // failed to decode
        data = encodeChar(ch);
        if (!data.isEmpty() && dynamic)
          *dynamic = true;
      }
      ret.append(data);
    }
  }
  return ret;
}

QByteArray DynamicShiftJISCodecPrivate::encodeChar(wchar_t ch)
{
  QByteArray ret;
  size_t i = text.find(ch);
  if (i == std::wstring::npos) {
    if (isFull())
      return ret;
    i = text.size();
    text.push_back(ch);
  }
  if (i < 31 * (4 * 16 + 4 - 1 - minimumSecondByte)) {
    int v1 = i / (4 * 16 + 4 - 1 - minimumSecondByte) + 0x81,
        v2 = i % (4 * 16 + 4 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    if (v2 == 0x40)
      v2 = 0x7f;
    else if (v2 >= 0x41)
      v2 += 0xfd - 0x41;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 31 * (4 * 16 + 4 - 1 - minimumSecondByte);
  if (i < 16 * (4 * 16 + 4 - 1 - minimumSecondByte)) {
    int v1 = i / (4 * 16 + 4 - 1 - minimumSecondByte) + 0xe0,
        v2 = i % (4 * 16 + 4 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    if (v2 == 0x40)
      v2 = 0x7f;
    else if (v2 >= 0x41)
      v2 += 0xfd - 0x41;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 16 * (4 * 16 + 4 - 1 - minimumSecondByte);
  if (i < 256 - 1 - minimumSecondByte) {
    int v1 = 0x80,
        v2 = i % (256 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 256 - 1 - minimumSecondByte;
  if (i < 256 - 1 - minimumSecondByte) {
    int v1 = 0xa0,
        v2 = i % (256 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  i -= 256 - 1 - minimumSecondByte;
  if (i < 16 * (256 - 1 - minimumSecondByte)) {
    int v1 = i / (256 - 1 - minimumSecondByte) + 0xf0,
        v2 = i % (256 - 1 - minimumSecondByte) + 1 + minimumSecondByte;
    ret.push_back(v1);
    ret.push_back(v2);
    return ret;
  }
  // This return should be unreachable
  return ret;
}

// Decode

QString DynamicShiftJISCodecPrivate::decode(const char *data, size_t length, bool *dynamic) const
{
  QString ret;
  for (size_t i = 0; i < length; i++) {
    quint8 ch = (quint8)data[i];
    if (ch <= 127)
      ret.push_back(ch);
    else if (ch >= 0xa1 && ch <= 0xdf) // size == 1
      ret.append(codec->toUnicode(data + 1, 1));
    else {
      if (i + 1 == length) // no enough character
        return ret;
      quint8 ch2 = (quint8)data[++i];
      if ((ch >= 0x81 && ch <= 0x9f || ch >= 0xe0 && ch <= 0xef)
          && (ch2 != 0x7f && ch2 >= 0x40 && ch2 <= 0xfc))
        ret.append(codec->toUnicode(data + i - 1, 2));
      else if (wchar_t c = decodeChar(ch, ch2)) {
        ret.push_back(c);
        if (dynamic)
          *dynamic = true;
      } else
        ret.push_back(ch + (wchar_t(ch2) << 8)); // preserve the original character
    }
  }
  return ret;
}

wchar_t DynamicShiftJISCodecPrivate::decodeChar(quint8 ch1, quint8 ch2) const
{
  if (text.empty())
    return 0;
  if (minimumSecondByte && ch2 < minimumSecondByte)
    return 0;
  size_t i = std::wstring::npos;
  if (ch1 >= 0x81 && ch1 <= 0x9f) {
    if (ch2 == 0x7f)
      ch2 = 0x40;
    else if (ch2 >= 0xfd)
      ch2 += 0x41 - 0xfd;
    i = (ch1 - 0x81) * (4 * 16 + 4 - 1 - minimumSecondByte) + ch2 - 1 - minimumSecondByte;
  } else if (ch1 >= 0xe0 && ch1 <= 0xef) {
    if (ch2 == 0x7f)
      ch2 = 0x40;
    else if (ch2 >= 0xfd)
      ch2 += 0x41 - 0xfd;
    i = (ch1 - 0xe0) * (4 * 16 + 4 - 1 - minimumSecondByte) + ch2 - 1 - minimumSecondByte
      + 31 * (4 * 16 + 4 - 1 - minimumSecondByte);
  } else if (ch1 == 0x80)
    i = ch2 - 1 - minimumSecondByte
      + 47 * (4 * 16 + 4 - 1 - minimumSecondByte);
  else if (ch1 == 0xa0)
    i = ch2 - 1 - minimumSecondByte
      + 47 * (4 * 16 + 4 - 1 - minimumSecondByte)
      + (256 - 1 - minimumSecondByte);
  else if (ch1 >= 0xf0 && ch1 <= 0xff) // 0xff is skipped
    i = (ch1 - 0xf0) * (256 - 1 - minimumSecondByte) + ch2 - 1 - minimumSecondByte
      + 47 * (4 * 16 + 4 - 1 - minimumSecondByte)
      + (256 - 1 - minimumSecondByte) * 2;
  if (i != std::wstring::npos && i < text.size())
    return text[i];
  return 0;
}

/** Public class */

DynamicShiftJISCodec::DynamicShiftJISCodec(QTextCodec *codec) : d_(new D(codec)) {}

DynamicShiftJISCodec::~DynamicShiftJISCodec() { delete d_; }

int DynamicShiftJISCodec::capacity() const { return d_->capacity(); }

int DynamicShiftJISCodec::size() const { return d_->text.size(); }

bool DynamicShiftJISCodec::isEmpty() const { return d_->text.empty(); }

bool DynamicShiftJISCodec::isFull() const { return d_->isFull(); }

void DynamicShiftJISCodec::clear() { d_->text.clear(); }

int DynamicShiftJISCodec::minimumSecondByte() const { return d_->minimumSecondByte; }

void DynamicShiftJISCodec::setMinimumSecondByte(int v) { d_->minimumSecondByte = v; }

QByteArray DynamicShiftJISCodec::encode(const QString &text, bool *dynamic) const
{
  if (dynamic)
    *dynamic = false;
  if (!d_->codec)
    return text.toLocal8Bit();
  return d_->encode(reinterpret_cast<const wchar_t *>(text.utf16()), text.size(), dynamic);
}

QString DynamicShiftJISCodec::decode(const QByteArray &data, bool *dynamic) const
{
  if (dynamic)
    *dynamic = false;
  if (!d_->codec)
    return QString::fromLocal8Bit(data);
  if (d_->text.empty())
    return d_->codec->toUnicode(data);
  return d_->decode(data.constData(), data.size(), dynamic);
}

// EOF
