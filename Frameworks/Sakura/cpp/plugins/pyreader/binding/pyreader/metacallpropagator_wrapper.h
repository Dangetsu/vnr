#ifndef SBK_METACALLPROPAGATORWRAPPER_H
#define SBK_METACALLPROPAGATORWRAPPER_H

#include <shiboken.h>

#include <metacallpropagator.h>

namespace PySide { class DynamicQMetaObject; }

class MetaCallPropagatorWrapper : public MetaCallPropagator
{
public:
    MetaCallPropagatorWrapper(QObject * parent = nullptr);
    inline void childEvent_protected(QChildEvent * arg__1) { MetaCallPropagator::childEvent(arg__1); }
    virtual void childEvent(QChildEvent * arg__1);
    inline void connectNotify_protected(const char * signal) { MetaCallPropagator::connectNotify(signal); }
    virtual void connectNotify(const char * signal);
    inline void customEvent_protected(QEvent * arg__1) { MetaCallPropagator::customEvent(arg__1); }
    virtual void customEvent(QEvent * arg__1);
    inline void disconnectNotify_protected(const char * signal) { MetaCallPropagator::disconnectNotify(signal); }
    virtual void disconnectNotify(const char * signal);
    virtual bool event(QEvent * arg__1);
    virtual bool eventFilter(QObject * arg__1, QEvent * arg__2);
    virtual const QMetaObject * metaObject() const;
    inline int receivers_protected(const char * signal) const { return MetaCallPropagator::receivers(signal); }
    inline QObject * sender_protected() const { return MetaCallPropagator::sender(); }
    inline int senderSignalIndex_protected() const { return MetaCallPropagator::senderSignalIndex(); }
    inline void timerEvent_protected(QTimerEvent * arg__1) { MetaCallPropagator::timerEvent(arg__1); }
    virtual void timerEvent(QTimerEvent * arg__1);
    virtual ~MetaCallPropagatorWrapper();
public:
    virtual int qt_metacall(QMetaObject::Call call, int id, void** args);
    virtual void* qt_metacast(const char* _clname);
    static void pysideInitQtMetaTypes();
};

#endif // SBK_METACALLPROPAGATORWRAPPER_H

