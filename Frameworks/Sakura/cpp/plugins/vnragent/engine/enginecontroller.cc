// enginecontroller.cc
// 4/20/2014 jichi

#include "config.h"
#include "engine/enginecontroller.h"
#include "engine/enginehash.h"
#include "engine/enginemodel.h"
#include "engine/engineutil.h"
//#include "engine/enginememory.h"
#include "engine/enginesettings.h"
#include "embed/embedmanager.h"
#include "hijack/hijackfuns.h"
#include "util/codepage.h"
#include "util/dyncodec.h"
#include "util/i18n.h"
#include "util/textutil.h"
//#include "windbg/util.h"
#include "qtrichruby/richrubyparser.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
//#include "mhook/mhook.h" // must after windows.h
#include <QtCore/QTimer>
#include <QtCore/QTextCodec>
#include <unordered_set>

#define DEBUG "enginecontroller"
#include "sakurakit/skdebug.h"

/** Private class */

class EngineControllerPrivate
{
  typedef EngineController Q;

  RichRubyParser rubyParser;

public:
  static Q *globalInstance;

  enum { ExchangeInterval = 10 };

  EngineSettings settings;

  EngineModel *model;

  uint codePage;
  //Q::RequiredAttributes attributes;

  QTextCodec *encoder,
             *decoder,
             *spaceCodec;

  bool dynamicEncodingEnabled;
  DynamicCodec *dynamicCodec;

  bool finalized;

  int scenarioLineCapacity, // current maximum number bytes in a line for scenario thread, always increase and never decrease
      otherLineCapacity;
  std::unordered_set<qint64> textHashes_; // hashes of rendered text

  EngineControllerPrivate(EngineModel *model)
    : model(model)
    , codePage(0)
    , encoder(nullptr), decoder(nullptr), spaceCodec(nullptr)
    , dynamicEncodingEnabled(true)
    , dynamicCodec(nullptr)
    , finalized(false)
    , scenarioLineCapacity(0)
    , otherLineCapacity(0)
  {}

  ~EngineControllerPrivate()
  {
    if (dynamicCodec)
      delete dynamicCodec;
  }

  void finalize()
  {
    if (!finalized) {
      finalizeCodecs();
      scenarioLineCapacity = model->scenarioLineCapacity;
      otherLineCapacity = model->otherLineCapacity;
      finalized = true;
    }
  }

  // Property helpers

  //bool testAttribute(Q::RequiredAttribute v) const { return attributes & v; }
  //bool testAttributes(Q::RequiredAttributes v) const { return attributes & v; }

  // Encoding

  bool isDecodable(const char *t) const
  { return decoder && Util::textDecodable(t, decoder); }

  QByteArray encode(const QString &text) const
  { return encoder ? encoder->fromUnicode(text) : text.toLocal8Bit(); }

  QByteArray encode(const QChar &c) const
  { return encoder ? encoder->fromUnicode(&c, 1) : QByteArray(); }

  QString decode(const QByteArray &data) const
  { return decoder ? decoder->toUnicode(data) : QString::fromLocal8Bit(data); }

  bool containsTextHash(qint64 hash) const
  { return textHashes_.find(hash) != textHashes_.end(); }

  void addTextHash(qint64 hash)
  { textHashes_.insert(hash); }

private:
  void finalizeCodecs()
  {
    const char *engineEncoding = Util::encodingForCodePage(codePage);
    decoder = engineEncoding ? Util::codecForName(engineEncoding) : nullptr;

    const char *systemEncoding = Util::encodingForCodePage(::GetACP());
    //systemEncoding = "gbk";
    //systemEncoding = ENC_KSC;
    encoder = Util::codecForName(systemEncoding ? systemEncoding : ENC_SJIS);

    if (model->enableDynamicEncoding && dynamicEncodingEnabled) {
      dynamicCodec = new DynamicCodec;
      dynamicCodec->setMinimumByte(model->dynamicEncodingMinimumByte);
    }

    DOUT("encoding =" << engineEncoding  << ", system =" << systemEncoding);
  }

  static QString alwaysInsertSpaces(const QString &text)
  {
    QString ret;
    foreach (QChar c, text) {
      ret.push_back(c);
      if (c.unicode() >= 32) // ignore non-printable characters
        ret.push_back(' '); // or insert \u3000 if needed
    }
    return ret;
  }

  static QString insertSpacesAfterUnencodable(const QString &text, const QTextCodec *codec)
  {
    QString ret;
    foreach (const QChar &c, text) {
      ret.push_back(c);
      if (!Util::charEncodable(c, codec))
        ret.push_back(' ');
    }
    return ret;
  }

  static size_t getLineCapacity(const wchar_t *s)
  {
    enum : wchar_t { br = '\n' };
    if (!::wcschr(s, br))
      return Util::measureTextSize(s);
    size_t ret = 0;
    for (auto p = s; *s; s++)
      if (*s == br) {
        ret = qMax<int>(ret, Util::measureTextSize(p, s));
        p = s + 1;
      }
    return ret;
  }

  // Get paintable text distance while skipping intermediate BBCode tags
  static int getTextDistance(const QString &text, int startPos, int stopPos, bool skipBBCode)
  {
    if (!skipBBCode)
      return stopPos - startPos;
    int ret = 0;
    for (int i = startPos; i <= stopPos; i++)
      if (text[i] == '[') {
        int closePos = text.indexOf(']', i + 1);
        if (closePos != -1)
          i = closePos;
      } else
        ret++;
    return ret;
  }

  //QString renderRuby(const QString &text) const
  //{
  //  if (text.isEmpty() || !rubyParser.containsRuby(text))
  //    return text;
  //  else if (model->rubyCreateFunction)
  //    return rubyParser.renderRuby(text, model->rubyCreateFunction);
  //  else
  //    return rubyParser.removeRuby(text);
  //}

  //QString removeRuby(const QString &text) const
  //{
  //  if (text.isEmpty() || !rubyParser.containsRuby(text))
  //    return text;
  //  return rubyParser.removeRuby(text);
  //}

public:
  static size_t getLineCapacity(const QString &text)
  { return getLineCapacity(static_cast<const wchar_t *>(text.utf16())); }

  static QString mergeLines(const QString &text)
  {
    const char br = '\n';
    if (!text.contains(br))
      return text;
    // Remove \n\s+
    bool br_found = false;
    QString ret;
    foreach (const QChar &ch, text)
      if (ch.unicode() == br)
        br_found = true;
      else if (!br_found || !ch.isSpace()) {
        br_found = false;
        ret.push_back(ch);
      }
    return ret;
  }

  /**
   *  @param  text
   *  @param  limit
   *  @param  wordWrap
   *  @param  skipBBCode  skip bbcode such as [ruby]
   */
  static QString limitTextWidth(const QString &text, int limit, bool wordWrap = true, bool skipBBCode = true)
  {
    if (limit <= 0 || text.size() <= limit / 2)
      return text;

    if (skipBBCode)
      skipBBCode = text.contains('[');

    const char br = '\n';
    int maximumWordSize = limit / 3 + 1;

    QString ret;
    int width = 0;
    int spacePos = -1,
        brPos = -1;
    for (int pos = 0; pos < text.size(); pos++) {
      const QChar &ch = text[pos];
      wchar_t w = ch.unicode();
      if (skipBBCode && w == '[') {
        int closePos = text.indexOf(']', pos + 1);
        if (closePos != -1) {
          ret.append(text.mid(pos, closePos - pos + 1));
          pos = closePos;
          continue;
        }
      }
      ret.push_back(ch);
      if (wordWrap && ch.isSpace()) {
        spacePos = pos;
        if (w == br)
          brPos = pos;
      }
      width += w <= 127 ? 1 : 2;
      if (width >= limit) {
        width = 0;
        if (w != br) {
          if (spacePos > brPos && getTextDistance(text, spacePos, pos, skipBBCode) < maximumWordSize) {
            ret[ret.size() - 1 - (pos - spacePos)] = br;
            brPos = spacePos;
          } else {
            ret.push_back(br);
            brPos = pos;
          }
        }
      }
      //else if (w == br)
      //  ret[ret.size() - 1] = ' '; // replace '\n' by ' '
    }
    return ret;
  }

  QString adjustSpaces(const QString &text) const
  {
    if (settings.alwaysInsertsSpaces)
      return alwaysInsertSpaces(text);
    if (settings.smartInsertsSpaces) {
      auto codec = spaceCodec ? spaceCodec : encoder;
      if (codec)
        return insertSpacesAfterUnencodable(text, codec);
    }
    return text;
  }

  static bool isCharTrimmable(const QChar &ch) { return ch.unicode() <= 32 || ch.isSpace(); }

  static QString trimText(const QString &text, QString *prefix = nullptr, QString *suffix = nullptr)
  {
    if (text.isEmpty() ||
        !isCharTrimmable(text[0]) && !isCharTrimmable(text[text.size() - 1]))
      return text;
    QString ret = text;
    if (isCharTrimmable(ret[0])) {
      int pos = 1;
      for (; pos < ret.size() && isCharTrimmable(ret[pos]); pos++);
      if (prefix)
        *prefix = ret.left(pos);
      ret = ret.mid(pos);
    }
    if (!ret.isEmpty() && isCharTrimmable(ret[ret.size() - 1])) {
      int pos = ret.size() - 2;
      for (; pos >= 0 && isCharTrimmable(ret[pos]); pos--);
      if (suffix)
        *suffix = ret.mid(pos + 1);
      ret = ret.left(pos + 1);
    }
    return ret;
  }

  QString filterText(const QString &text, int role) const
  {
    QString ret = text;
    if (model->newLineString && ::strcmp(model->newLineString, "\n"))
      ret.replace(model->newLineString, "\n");
    if (model->rubyRemoveFunction)
       ret = model->rubyRemoveFunction(ret);
    if (model->textFilterFunction)
      ret = model->textFilterFunction(ret, role);
    if (!model->textSeparators.isEmpty()) {
      char s[2] = {};
      for (int i = 0; i < model->textSeparators.size(); i++) {
        s[0] = i + 1;
        ret.replace(model->textSeparators[i], s);
      }
    }
    return ret;
  }

  QString filterTranslation(const QString &text, int role) const
  {
    if (text.isEmpty())
      return text;
    QString ret = text;

    if (rubyParser.containsRuby(ret)) {
      if (model->rubyCreateFunction && role == Engine::ScenarioRole)
        ret = rubyParser.renderRuby(ret, model->rubyCreateFunction);
      else
        ret = rubyParser.removeRuby(ret);
    }
    if (!model->textSeparators.isEmpty()) {
      char s[2] = {};
      for (int i = 0; i < model->textSeparators.size(); i++) {
        s[0] = i + 1;
        ret.replace(s, model->textSeparators[i]);
      }
    }
    // LCScriptEngine requires newLineString must be after textSeparators
    if (model->newLineString && ::strcmp(model->newLineString, "\n") && ret.contains('\n'))
      ret.replace("\n", model->newLineString);
    if (model->translationFilterFunction)
      ret = model->translationFilterFunction(ret, role);
    if (model->enableThin2WideCharacters)
      ret = Util::thin2wide(ret);
    return ret;
  }
};

EngineController *EngineControllerPrivate::globalInstance;

/** Public class */

// - Detection -

EngineController *EngineController::instance() { return D::globalInstance; }

// - Construction -

EngineController::EngineController(EngineModel *model)
  : d_(new D(model))
{
  switch (model->encoding) {
  case EngineModel::Utf16Encoding: setEncoding(ENC_UTF16); break;
  case EngineModel::Utf8Encoding: setEncoding(ENC_UTF8); break;
  default: setEncoding(ENC_SJIS);
  }
}

EngineController::~EngineController() { delete d_; }

EngineSettings *EngineController::settings() const { return &d_->settings; }
EngineModel *EngineController::model() const { return d_->model; }

const char *EngineController::name() const { return d_->model->name; }

const char *EngineController::encoding() const
{ return Util::encodingForCodePage(d_->codePage); }

bool EngineController::isDynamicEncodingEnabled() const
{ return d_->dynamicEncodingEnabled; }

void EngineController::setDynamicEncodingEnabled(bool t)
{
  if (d_->dynamicEncodingEnabled != t) {
    d_->dynamicEncodingEnabled = t;
    if (t && !d_->dynamicCodec && d_->finalized && d_->model->enableDynamicEncoding)
      d_->dynamicCodec = new DynamicCodec;
  }
}

void EngineController::setCodePage(uint v)
{
  if (v != d_->codePage) {
    d_->codePage = v;

    if (d_->finalized) {
      const char *encoding = Util::encodingForCodePage(v);
      d_->decoder = encoding ? Util::codecForName(encoding) : nullptr;
    }
  }
}

void EngineController::setEncoding(const QString &v)
{ setCodePage(Util::codePageForEncoding(v)); }

//bool EngineController::isTranscodingNeeded() const
//{ return d_->encoder != d_->decoder; }

void EngineController::setSpacePolicyEncoding(const QString &v)
{ d_->spaceCodec = v.isEmpty() ? nullptr : Util::codecForName(v.toAscii()); }

QString EngineController::decode(const QByteArray &v) const { return d_->decode(v); }
QByteArray EngineController::encode(const QString &v) const { return d_->encode(v); }

bool EngineController::isTextDecodable(const char *t) const { return d_->isDecodable(t); }

QTextCodec *EngineController::encoder() const { return d_->encoder; }
QTextCodec *EngineController::decoder() const { return d_->decoder; }

// - Attach -

bool EngineController::attach()
{
  if (d_->model->attachFunction)
    return d_->model->attachFunction();
  return false;

  //if (!d_->model->searchFunction)
  //  return false;
  //ulong startAddress,
  //      stopAddress;
  //if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
  //  return false;
  //ulong addr = d_->model->searchFunction(startAddress, stopAddress);
  ////ulong addr = startAddress + 0x31850; // 世界と世界の真ん中 体験版
  ////ulong addr = 0x41af90; // レミニセンス function address
  //if (addr) {
  //  DOUT("attached, engine =" << name() << ", absaddr =" << QString::number(addr, 16) << "reladdr =" << QString::number(addr - startAddress, 16));
  //  auto d = d_;
  //  auto callback = [addr, d](winhook::hook_stack *s) -> bool {
  //    if (d->globalDispatchFun)
  //      d->globalDispatchFun((EngineModel::HookStack *)s);
  //    return true;
  //  };
  //  return winhook::hook_before(addr, callback);

  //  //WinDbg::ThreadsSuspender suspendedThreads; // lock all threads to prevent crashing
  //  //d_->oldHookFun = Engine::replaceFunction<Engine::address_type>(addr, ::newHookFun);
  //  return true;
  //}
  //return false;
}

bool EngineController::load()
{
  bool ok = attach();
  if (ok) {
    d_->finalize();
    D::globalInstance = this;
  }
  return ok;
}

bool EngineController::unload() { return false; }

// - Exists -

bool EngineController::match()
{
  return d_->model->matchFunction ?
      d_->model->matchFunction() :
      matchFiles(d_->model->matchFiles);
}

bool EngineController::matchFiles(const QStringList &relpaths)
{
  if (relpaths.isEmpty())
    return false;
  foreach (const QString &path, relpaths)
    if (path.contains('|')) {
      bool found = false;
      foreach (const QString &it, path.split('|')) {
        if (Engine::matchFiles(it)) {
          found = true;
          break;
        }
      }
      if (!found)
        return false;
    } else if (!Engine::matchFiles(path))
      return false;

  DOUT("ret = true, relpaths =" << relpaths);
  return true;
}

// - Dispatch -

QByteArray EngineController::dispatchTextA(const QByteArray &data, int role, long signature, int maxSize, bool sendAllowed, bool *timeout)
{
  if (timeout)
    *timeout = false;
  if (data.isEmpty())
    return data;

  if (!d_->settings.enabled || Engine::isPauseKeyPressed())
    return data;

  if (!signature)
    signature = Engine::hashThreadSignature(role);
  if (!role)
    role = d_->settings.textRoleOf(signature);

  if (role == Engine::OtherRole
      && d_->containsTextHash(Engine::hashByteArray(data)))
    return data;

  QString text = d_->decode(data);
  if (text.isEmpty())
    return data;
  if (!d_->model->enableNonDecodableCharacters && text.contains(L'\xfffd'))
    return data;

  QString prefix,
          suffix,
          trimmedText = D::trimText(text, &prefix, &suffix);

  trimmedText = d_->filterText(trimmedText, role);

  if (role == Engine::ScenarioRole && d_->scenarioLineCapacity ||
      role == Engine::OtherRole && d_->otherLineCapacity)
    trimmedText = d_->mergeLines(trimmedText);

  if (trimmedText.isEmpty()) {
    if (!d_->settings.textVisible[role])
      return QByteArray();
    return data;
  }

  qint64 hash = Engine::hashWString(trimmedText);

  QString language;

  auto p = EmbedManager::instance();
  QString repl;
  if (role == Engine::OtherRole) { // skip sending text
    if (!d_->settings.textVisible[role])
      return QByteArray();
    if (!d_->settings.translationEnabled[role] || !Util::needsTranslation(trimmedText))
      return data;
    repl = p->findTranslation(hash, role, &language);
  }

  bool sent = false;
  bool needsTranslation = false;
  if (sendAllowed
      && !d_->settings.translationEnabled[role]
      && (d_->settings.extractionEnabled[role] || d_->settings.extractsAllTexts)
      && (role != Engine::OtherRole || repl.isEmpty())) {
    p->sendText(trimmedText, hash, signature, role, needsTranslation);
    sent = true;
  }

  if (!d_->settings.textVisible[role])
    return QByteArray();
  if (!d_->settings.translationEnabled[role])
    return d_->settings.transcodingEnabled[role] ? d_->encode(text) : data;

  if (repl.isEmpty())
    repl = p->findTranslation(hash, role, &language);

  if (sendAllowed && !sent) {
    needsTranslation = repl.isEmpty();
    if (role != Engine::OtherRole || needsTranslation) {
      p->sendText(trimmedText, hash, signature, role, needsTranslation);
      sent = true;
    }
  }
  if (sent && needsTranslation)
    repl = p->waitForTranslation(hash, role, &language);

  if (repl.isEmpty()) {
    if (timeout)
      *timeout = true;
    repl = trimmedText;
  } else if (repl != trimmedText) {
    if (!repl.isEmpty() && d_->model->newLineString) {
      bool wordWrap = Util::languageNeedsWordWrap(language);
      bool containsBBCode = role == Engine::ScenarioRole && d_->model->rubyCreateFunction;
      if (role == Engine::ScenarioRole) {
        if (d_->scenarioLineCapacity) {
          int capacity = D::getLineCapacity(d_->filterText(text, role));
          if (d_->scenarioLineCapacity < capacity)
            d_->scenarioLineCapacity = capacity;
          repl = d_->limitTextWidth(repl, d_->scenarioLineCapacity, wordWrap, containsBBCode);
        } else if (d_->settings.scenarioWidth)
          repl = d_->limitTextWidth(repl, d_->settings.scenarioWidth, wordWrap, containsBBCode);
      } else if (role == Engine::OtherRole && d_->otherLineCapacity) {
        int capacity = D::getLineCapacity(d_->filterText(text, role));
        if (d_->otherLineCapacity < capacity)
          d_->otherLineCapacity = capacity;
        repl = d_->limitTextWidth(repl, d_->otherLineCapacity, wordWrap, containsBBCode);
      }
    }
    repl = d_->filterTranslation(repl, role);
    switch (role) {
    case Engine::ScenarioRole:
      if (d_->settings.scenarioTextVisible)
        repl.append(d_->model->newLineString ? d_->model->newLineString : " ")
            .append(trimmedText);
      break;
    case Engine::NameRole:
      if (d_->settings.nameTextVisible)
        repl.append(d_->model->separatorString ? d_->model->separatorString : " ")
            .append(trimmedText);
      break;
    case Engine::OtherRole:
      if (d_->settings.otherTextVisible)
        repl.append(d_->model->separatorString ? d_->model->separatorString : " ")
            .append(trimmedText);
      break;
    }
  }

  repl = d_->adjustSpaces(repl);

  QByteArray ret;
  if (maxSize > 0) {
    QByteArray prefixData,
               suffixData;
    if (!prefix.isEmpty())
      prefixData = d_->encode(prefix);
    if (!suffix.isEmpty())
      suffixData = d_->encode(suffix);

    ret = (d_->dynamicEncodingEnabled && d_->dynamicCodec) ? d_->dynamicCodec->encode(repl)
        : d_->encode(repl);
    int capacity = maxSize - prefixData.size() - suffixData.size(); // excluding trailing \0
    if (capacity < ret.size()) {
      if (capacity >= 2) {
        const char *end = Hijack::oldCharPrevA(ret.constData(), ret.constData() + capacity);
        ret = ret.left(end - data.constData());
      } else
        ret = ret.left(capacity);
    }

    if (!prefixData.isEmpty())
      ret.prepend(prefixData);
    if (!suffixData.isEmpty())
      ret.append(suffixData);
  } else {
    if (!prefix.isEmpty())
      repl.prepend(prefix);
    if (!suffix.isEmpty())
      repl.append(suffix);
    ret = (d_->dynamicEncodingEnabled && d_->dynamicCodec) ? d_->dynamicCodec->encode(repl)
        : d_->encode(repl);
  }

  if (role == Engine::OtherRole)
    d_->addTextHash(Engine::hashByteArray(ret));
  return ret;
}

QString EngineController::dispatchTextW(const QString &text, int role, long signature, int maxSize, bool sendAllowed, bool *timeout)
{
  if (timeout)
    *timeout = false;
  if (text.isEmpty())
    return text;

  // Canceled
  if (!d_->settings.enabled || Engine::isPauseKeyPressed())
    return text;

  if (!signature)
    signature = Engine::hashThreadSignature(role);
  if (!role)
    role = d_->settings.textRoleOf(signature);

  if (role == Engine::OtherRole
      && d_->containsTextHash(Engine::hashWString(text)))
    return text;

  QString prefix,
          suffix,
          trimmedText = D::trimText(text, &prefix, &suffix);
  trimmedText = d_->filterText(trimmedText, role);
  if (role == Engine::ScenarioRole && d_->scenarioLineCapacity ||
      role == Engine::OtherRole && d_->otherLineCapacity)
    trimmedText = d_->mergeLines(trimmedText);

  if (trimmedText.isEmpty()) {
    if (!d_->settings.textVisible[role])
      return QString();
    return text;
  }

  qint64 hash = Engine::hashWString(trimmedText);

  QString language;

  auto p = EmbedManager::instance();
  QString repl;
  if (role == Engine::OtherRole) { // skip sending text
    if (!d_->settings.textVisible[role])
      return QString();
    if (!d_->settings.translationEnabled[role] || !Util::needsTranslation(trimmedText))
      return text;
    repl = p->findTranslation(hash, role, &language);
  }

  bool sent = false;
  bool needsTranslation = false;
  if (sendAllowed
      && !d_->settings.translationEnabled[role]
      && (d_->settings.extractionEnabled[role] || d_->settings.extractsAllTexts)
      && (role != Engine::OtherRole || repl.isEmpty())) {
    p->sendText(trimmedText, hash, signature, role, needsTranslation);
    sent = true;
  }

  if (!d_->settings.textVisible[role])
    return QString();
  if (!d_->settings.translationEnabled[role])
    return text;

  if (repl.isEmpty())
    repl = p->findTranslation(hash, role, &language);

  if (sendAllowed && !sent) {
    needsTranslation = repl.isEmpty();
    if (role != Engine::OtherRole || needsTranslation) {
      p->sendText(trimmedText, hash, signature, role, needsTranslation);
      sent = true;
    }
  }
  if (sent && needsTranslation)
    repl = p->waitForTranslation(hash, role, &language);

  if (repl.isEmpty()) {
    if (timeout)
      *timeout = true;
    repl = trimmedText; // prevent from deleting text
  } else if (repl != trimmedText) {
    if (!repl.isEmpty() && d_->model->newLineString) {
      bool wordWrap = Util::languageNeedsWordWrap(language);
      bool containsBBCode = role == Engine::ScenarioRole && d_->model->rubyCreateFunction;
      if (role == Engine::ScenarioRole) {
        if (d_->scenarioLineCapacity) {
          int capacity = D::getLineCapacity(d_->filterText(text, role));
          if (d_->scenarioLineCapacity < capacity)
            d_->scenarioLineCapacity = capacity;
          repl = d_->limitTextWidth(repl, d_->scenarioLineCapacity, wordWrap, containsBBCode);
        } else if (d_->settings.scenarioWidth)
          repl = d_->limitTextWidth(repl, d_->settings.scenarioWidth, wordWrap, containsBBCode);
      } else if (role == Engine::OtherRole && d_->otherLineCapacity) {
        int capacity = D::getLineCapacity(d_->filterText(text, role));
        if (d_->otherLineCapacity < capacity)
          d_->otherLineCapacity = capacity;
        repl = d_->limitTextWidth(repl, d_->otherLineCapacity, wordWrap, containsBBCode);
      }
    }
    repl = d_->filterTranslation(repl, role);
    switch (role) {
    case Engine::ScenarioRole:
      if (d_->settings.scenarioTextVisible)
        repl.append(d_->model->newLineString ? d_->model->newLineString : " ")
            .append(trimmedText);
      break;
    case Engine::NameRole:
      if (d_->settings.nameTextVisible)
        repl.append(d_->model->separatorString ? d_->model->separatorString : " ")
            .append(trimmedText);
      break;
    case Engine::OtherRole:
      if (d_->settings.otherTextVisible)
        repl.append(d_->model->separatorString ? d_->model->separatorString : " ")
            .append(trimmedText);
        //repl = QString("%1 / %2").arg(repl, trimmedText);
      break;
    }
  }

  repl = d_->adjustSpaces(repl);

  if (maxSize > 0 && maxSize < repl.size() + prefix.size() + suffix.size())
    repl = repl.left(maxSize - prefix.size() - suffix.size());

  if (!prefix.isEmpty())
    repl.prepend(prefix);
  if (!suffix.isEmpty())
    repl.append(suffix);

  if (role == Engine::OtherRole)
    d_->addTextHash(Engine::hashWString(repl));
  return repl;
}

// EOF

/*
// - Exchange -

// Qt is not allowed to appear in this function
const char *EngineController::exchangeTextA(const char *data, long signature, int role)
{
  auto d_mem = d_->exchangeMemory;
  if (!d_mem || !data)
    return data;

  ulong key = ::GetTickCount();
  d_mem->setRequestStatus(EngineSharedMemory::BusyStatus);
  d_mem->setRequestKey(key);
  d_mem->setRequestSignature(signature);
  d_mem->setRequestRole(role);
  d_mem->setRequestText(data);
  d_mem->setRequestStatus(EngineSharedMemory::ReadyStatus);

  // Spin lock
  while (d_mem->responseKey() != key ||
         d_mem->responseStatus() != EngineSharedMemory::ReadyStatus) {
    if (d_mem->responseStatus() == EngineSharedMemory::CancelStatus)
      return data;
    ::Sleep(D::ExchangeInterval);
  }
  return d_mem->responseText();
}

void EngineControllerPrivate::exchange()
{
  if (!exchangeMemory)
    return;
  if (exchangeMemory->requestStatus() == EngineSharedMemory::ReadyStatus) {
    exchangeMemory->setRequestStatus(EngineSharedMemory::EmptyStatus);
    if (auto req = exchangeMemory->requestText()) {
      auto key = exchangeMemory->requestKey();
      auto role = exchangeMemory->requestRole();
      auto sig = exchangeMemory->requestSignature();
      QByteArray resp = q_->dispatchTextA(req, role, sig);
      exchangeMemory->setResponseStatus(EngineSharedMemory::BusyStatus);
      exchangeMemory->setResponseText(resp);
      exchangeMemory->setResponseRole(role);
      exchangeMemory->setResponseKey(key);
      exchangeMemory->setResponseStatus(EngineSharedMemory::ReadyStatus);
    }
  }
}



typedef int (WINAPI *MultiByteToWideCharFun)(UINT CodePage, DWORD dwFlags, LPCSTR lpMultiByteStr, int cbMultiByte, LPWSTR lpWideCharStr, int cchWideChar);
typedef int (WINAPI *WideCharToMultiByteFun)(UINT CodePage, DWORD dwFlags, LPCWSTR lpWideCharStr, int cchWideChar, LPSTR lpMultiByteStr, int cbMultiByte, LPCSTR lpDefaultChar, LPBOOL lpUsedDefaultChar);
MultiByteToWideCharFun oldMultiByteToWideChar;
WideCharToMultiByteFun oldWideCharToMultiByte;
int WINAPI newMultiByteToWideChar(UINT CodePage, DWORD dwFlags, LPCSTR lpMultiByteStr, int cbMultiByte, LPWSTR lpWideCharStr, int cchWideChar)
{
  if (CodePage == 932)
    CodePage = 936;
  return ::oldMultiByteToWideChar(CodePage, dwFlags, lpMultiByteStr, cbMultiByte, lpWideCharStr, cchWideChar);
}

int WINAPI newWideCharToMultiByte(UINT CodePage, DWORD dwFlags, LPCWSTR lpWideCharStr, int cchWideChar, LPSTR lpMultiByteStr, int cbMultiByte, LPCSTR lpDefaultChar, LPBOOL lpUsedDefaultChar)
{
  if (CodePage == 932)
    CodePage = 936;
  return ::oldWideCharToMultiByte(CodePage, dwFlags, lpWideCharStr, cchWideChar, lpMultiByteStr, cbMultiByte, lpDefaultChar, lpUsedDefaultChar);
}
    ::oldMultiByteToWideChar = Engine::replaceFunction<MultiByteToWideCharFun>(addr, ::newMultiByteToWideChar);
    ::oldWideCharToMultiByte = Engine::replaceFunction<WideCharToMultiByteFun>(addr, ::newWideCharToMultiByte);
*/

/**
 *  The stack must be consistent with struct HookStack
 *
 *  Note for detours
 *  - It simply replaces the code with jmp and int3. Jmp to newHookFun
 *  - oldHookFun is the address to a code segment that jmp back to the original function
 */
/*
__declspec(naked) static int newHookFun()
{
  // The push order must be consistent with struct HookStack in enginemodel.h
  //static DWORD lastArg2;
  __asm // consistent with struct HookStack
  {
    //pushfd      // 5/25/2015: pushfd twice according to ith, not sure if it is really needed
    pushad      // increase esp by 0x20 = 4 * 8, push ecx for thiscall is enough, though
    pushfd      // eflags
    push esp    // arg1
    call EngineControllerPrivate::globalDispatchFun
    //add esp,4   // pop esp
    popfd
    popad
    //popfd
    // TODO: instead of jmp, allow modify the stack after calling the function
    jmp EngineControllerPrivate::globalOldHookFun
  }
}
*/
