#ifndef SBK_KEYBOARDSIGNALWRAPPER_H
#define SBK_KEYBOARDSIGNALWRAPPER_H

#include <shiboken.h>

#include <keyboardsignal.h>

namespace PySide { class DynamicQMetaObject; }

class KeyboardSignalWrapper : public KeyboardSignal
{
public:
    KeyboardSignalWrapper(QObject * parent = nullptr);
    inline void childEvent_protected(QChildEvent * arg__1) { KeyboardSignal::childEvent(arg__1); }
    virtual void childEvent(QChildEvent * arg__1);
    inline void connectNotify_protected(const char * signal) { KeyboardSignal::connectNotify(signal); }
    virtual void connectNotify(const char * signal);
    inline void customEvent_protected(QEvent * arg__1) { KeyboardSignal::customEvent(arg__1); }
    virtual void customEvent(QEvent * arg__1);
    inline void disconnectNotify_protected(const char * signal) { KeyboardSignal::disconnectNotify(signal); }
    virtual void disconnectNotify(const char * signal);
    virtual bool event(QEvent * arg__1);
    virtual bool eventFilter(QObject * arg__1, QEvent * arg__2);
    virtual const QMetaObject * metaObject() const;
    inline int receivers_protected(const char * signal) const { return KeyboardSignal::receivers(signal); }
    inline QObject * sender_protected() const { return KeyboardSignal::sender(); }
    inline int senderSignalIndex_protected() const { return KeyboardSignal::senderSignalIndex(); }
    inline void timerEvent_protected(QTimerEvent * arg__1) { KeyboardSignal::timerEvent(arg__1); }
    virtual void timerEvent(QTimerEvent * arg__1);
    virtual ~KeyboardSignalWrapper();
public:
    virtual int qt_metacall(QMetaObject::Call call, int id, void** args);
    virtual void* qt_metacast(const char* _clname);
    static void pysideInitQtMetaTypes();
};

#endif // SBK_KEYBOARDSIGNALWRAPPER_H

