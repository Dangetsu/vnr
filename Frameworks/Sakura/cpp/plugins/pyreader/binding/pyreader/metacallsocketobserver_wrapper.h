#ifndef SBK_METACALLSOCKETOBSERVERWRAPPER_H
#define SBK_METACALLSOCKETOBSERVERWRAPPER_H

#include <shiboken.h>

#include <metacallobserver.h>

namespace PySide { class DynamicQMetaObject; }

class MetaCallSocketObserverWrapper : public MetaCallSocketObserver
{
public:
    MetaCallSocketObserverWrapper(QObject * parent);
    inline void childEvent_protected(QChildEvent * arg__1) { MetaCallSocketObserver::childEvent(arg__1); }
    virtual void childEvent(QChildEvent * arg__1);
    inline void connectNotify_protected(const char * signal) { MetaCallSocketObserver::connectNotify(signal); }
    virtual void connectNotify(const char * signal);
    inline void customEvent_protected(QEvent * arg__1) { MetaCallSocketObserver::customEvent(arg__1); }
    virtual void customEvent(QEvent * arg__1);
    inline void disconnectNotify_protected(const char * signal) { MetaCallSocketObserver::disconnectNotify(signal); }
    virtual void disconnectNotify(const char * signal);
    virtual bool event(QEvent * arg__1);
    virtual bool eventFilter(QObject * arg__1, QEvent * arg__2);
    virtual const QMetaObject * metaObject() const;
    inline int receivers_protected(const char * signal) const { return MetaCallSocketObserver::receivers(signal); }
    inline QObject * sender_protected() const { return MetaCallSocketObserver::sender(); }
    inline int senderSignalIndex_protected() const { return MetaCallSocketObserver::senderSignalIndex(); }
    inline void timerEvent_protected(QTimerEvent * arg__1) { MetaCallSocketObserver::timerEvent(arg__1); }
    virtual void timerEvent(QTimerEvent * arg__1);
    virtual ~MetaCallSocketObserverWrapper();
public:
    virtual int qt_metacall(QMetaObject::Call call, int id, void** args);
    virtual void* qt_metacast(const char* _clname);
    static void pysideInitQtMetaTypes();
};

#endif // SBK_METACALLSOCKETOBSERVERWRAPPER_H

