// textutil.cc
// 5/7/2014 jichi
#include "util/textutil.h"
#include "unistr/unichar.h"
#include <QtCore/QString>

// Currently, only for Japanese text.
// Return if the text contains non-ascii characters.
//
// TODO: Skip "ＭＳ ゴシック"
bool Util::needsTranslation(const QString &text)
{
  return !text.isEmpty()
      && !allAscii(text)
      && !unistr::ishangul(text[0].unicode())
      && !(text.size() >= 2 && unistr::ishangul(text[1].unicode()));
}

bool Util::allHangul(const wchar_t *s)
{
  for (; *s; s++)
    if (*s > 127 && !unistr::isspace(*s) && !unistr::ishangul(*s) && !unistr::ispunct(*s))
      return false;
  return true;
}

QString Util::thin2wide(const QString &s)
{
  QString r;
  foreach (const QChar &it, s) {
    wchar_t ch = it.unicode();
    if (ch == ' ')
      ch = 0x3000;
    else
      ch = unistr::thin2wide(ch);
    r.push_back(ch);
  }
  return r;
}

QString Util::wide2thin(const QString &s)
{
  QString r;
  foreach (const QChar &it, s) {
    wchar_t ch = it.unicode();
    if (ch == 0x3000)
      ch = ' ';
    else
      ch = unistr::wide2thin(ch);
    r.push_back(ch);
  }
  return r;
}

// EOF

#if 0

bool Util::containsWidePunct(const char *text)
{
  static const char *puncts[] = {
    "\x81\x41" /* 、 */
    , "\x81\x43" /* ， */
    , "\x81\x42" /* 。 */
    , "\x81\x48" /* ？ */
    , "\x81\x49" /* ！ */
    , "\x81\x63" /* … */
    , "\x81\x64" /* ‥ */

    , "\x81\x79" /* 【 */
    , "\x81\x7a" /* 】 */
    , "\x81\x75" /* 「 */
    , "\x81\x76" /* 」 */
    , "\x81\x77" /* 『 */
    , "\x81\x78" /* 』 */
    , "\x81\x69" /* （ */
    , "\x81\x6a" /* ） */
    , "\x81\x6f" /* ｛ */
    , "\x81\x70" /* ｝ */
    , "\x81\x71" /* 〈 */
    , "\x81\x72" /* 〉 */
    , "\x81\x6d" /* ［ */
    , "\x81\x6e" /* ］ */
    , "\x81\x83" /* ＜ */
    , "\x81\x84" /* ＞ */
  };
  for (size_t i = 0; i < sizeof(puncts)/sizeof(*puncts); i++)
    if (::strstr(text, puncts[i]))
      return true;
  return false;
}

#endif // 0
