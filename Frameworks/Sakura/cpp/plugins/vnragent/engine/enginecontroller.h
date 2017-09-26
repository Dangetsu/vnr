#pragma once

// enginecontroller.h
// 4/20/2014 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QStringList>

QT_FORWARD_DECLARE_CLASS(QTextCodec)
class EngineModel;
class EngineSettings;
class EngineControllerPrivate;
class EngineController
{
  //Q_OBJECT
  SK_CLASS(EngineController)
  SK_DECLARE_PRIVATE(EngineControllerPrivate)
  SK_DISABLE_COPY(EngineController)

public:
  // Successful engine controller
  // TODO: get rid of global instance
  // Need to write my own ASM bytes to achieve C partial functions
  static Self *instance();

  ///  Model cannot be null. Engine does NOT take the ownership of the model.
  explicit EngineController(EngineModel *model);
  ~EngineController();

  EngineSettings *settings() const;
  EngineModel *model() const;

  const char *name() const;

  const char *encoding() const;
  void setEncoding(const QString &v);
  QByteArray encode(const QString &text) const;
  QString decode(const QByteArray &text) const;

  //bool encodable(const QString &text) const;
  bool isTextDecodable(const char *text) const;

  QTextCodec *encoder() const;
  QTextCodec *decoder() const;

  // Encoding for inserting spaces
  void setSpacePolicyEncoding(const QString &v);

  //bool isTranscodingNeeded() const;

  bool match(); // match files
  bool load();
  bool unload();

  //static bool isEnabled();
  //static void setEnabled(bool t);

protected:
  uint codePage() const;
  void setCodePage(uint cp);

  bool isDynamicEncodingEnabled() const;
  void setDynamicEncodingEnabled(bool t);

  bool attach(); ///< Invoked by load
  //bool detach(); ///< Invoked by unload

  // Hook

  ///  Return whether relpaths exist
  static bool matchFiles(const QStringList &relpaths);

  // Interface to descendant classes, supposed to be protected
public:
  ///  Send LPCSTR text to VNR, timeout == true iff translation timeout. MaxSize is the maximum data size excluding \0
  QByteArray dispatchTextA(const QByteArray &data, int role, long signature = 0, int maxSize = 0, bool sendAllowed = true, bool *timeout = nullptr);

  ///  Send LPCWSTR text to VNR, timeout == true iff translation timeout. MaxSize is the maximum text size excluding \0
  QString dispatchTextW(const QString &text, int role, long signature = 0, int maxSize = 0, bool sendAllowed = true, bool *timeout = nullptr);

  // This function is not thread-safe
  //const char *exchangeTextA(const char *data, long signature, int role = 0);
};

// EOF
