
// default includes
#include <shiboken.h>
#include <pysidesignal.h>
#include <pysideproperty.h>
#include <pyside.h>
#include <destroylistener.h>
#include <typeresolver.h>
#include <typeinfo>
#include <signalmanager.h>
#include <pysidemetafunction.h>
#include "pytexthook_python.h"

#include "texthook_wrapper.h"

// Extra includes
#include <QList>
#include <qbytearray.h>
#include <qcoreevent.h>
#include <qmetaobject.h>
#include <qobject.h>
#include <qobjectdefs.h>
#include <qthread.h>
#include <texthook.h>


// Native ---------------------------------------------------------

void TextHookWrapper::pysideInitQtMetaTypes()
{
}

TextHookWrapper::TextHookWrapper(QObject * parent) : TextHook(parent) {
    // ... middle
}

void TextHookWrapper::childEvent(QChildEvent * arg__1)
{
    Shiboken::GilState gil;
    if (PyErr_Occurred())
        return ;
    Shiboken::AutoDecRef pyOverride(Shiboken::BindingManager::instance().getOverride(this, "childEvent"));
    if (pyOverride.isNull()) {
        gil.release();
        return this->::QObject::childEvent(arg__1);
    }

    Shiboken::AutoDecRef pyArgs(Py_BuildValue("(N)",
        Shiboken::Conversions::pointerToPython((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QCHILDEVENT_IDX], arg__1)
    ));
    bool invalidateArg1 = PyTuple_GET_ITEM(pyArgs, 0)->ob_refcnt == 1;

    Shiboken::AutoDecRef pyResult(PyObject_Call(pyOverride, pyArgs, NULL));
    // An error happened in python code!
    if (pyResult.isNull()) {
        PyErr_Print();
        return ;
    }
    if (invalidateArg1)
        Shiboken::Object::invalidate(PyTuple_GET_ITEM(pyArgs, 0));
}

void TextHookWrapper::connectNotify(const char * signal)
{
    Shiboken::GilState gil;
    if (PyErr_Occurred())
        return ;
    Shiboken::AutoDecRef pyOverride(Shiboken::BindingManager::instance().getOverride(this, "connectNotify"));
    if (pyOverride.isNull()) {
        gil.release();
        return this->::QObject::connectNotify(signal);
    }

    Shiboken::AutoDecRef pyArgs(Py_BuildValue("(N)",
        Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<const char*>(), signal)
    ));

    Shiboken::AutoDecRef pyResult(PyObject_Call(pyOverride, pyArgs, NULL));
    // An error happened in python code!
    if (pyResult.isNull()) {
        PyErr_Print();
        return ;
    }
}

void TextHookWrapper::customEvent(QEvent * arg__1)
{
    Shiboken::GilState gil;
    if (PyErr_Occurred())
        return ;
    Shiboken::AutoDecRef pyOverride(Shiboken::BindingManager::instance().getOverride(this, "customEvent"));
    if (pyOverride.isNull()) {
        gil.release();
        return this->::QObject::customEvent(arg__1);
    }

    Shiboken::AutoDecRef pyArgs(Py_BuildValue("(N)",
        Shiboken::Conversions::pointerToPython((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QEVENT_IDX], arg__1)
    ));
    bool invalidateArg1 = PyTuple_GET_ITEM(pyArgs, 0)->ob_refcnt == 1;

    Shiboken::AutoDecRef pyResult(PyObject_Call(pyOverride, pyArgs, NULL));
    // An error happened in python code!
    if (pyResult.isNull()) {
        PyErr_Print();
        return ;
    }
    if (invalidateArg1)
        Shiboken::Object::invalidate(PyTuple_GET_ITEM(pyArgs, 0));
}

void TextHookWrapper::disconnectNotify(const char * signal)
{
    Shiboken::GilState gil;
    if (PyErr_Occurred())
        return ;
    Shiboken::AutoDecRef pyOverride(Shiboken::BindingManager::instance().getOverride(this, "disconnectNotify"));
    if (pyOverride.isNull()) {
        gil.release();
        return this->::QObject::disconnectNotify(signal);
    }

    Shiboken::AutoDecRef pyArgs(Py_BuildValue("(N)",
        Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<const char*>(), signal)
    ));

    Shiboken::AutoDecRef pyResult(PyObject_Call(pyOverride, pyArgs, NULL));
    // An error happened in python code!
    if (pyResult.isNull()) {
        PyErr_Print();
        return ;
    }
}

bool TextHookWrapper::event(QEvent * arg__1)
{
    Shiboken::GilState gil;
    if (PyErr_Occurred())
        return ((bool)0);
    Shiboken::AutoDecRef pyOverride(Shiboken::BindingManager::instance().getOverride(this, "event"));
    if (pyOverride.isNull()) {
        gil.release();
        return this->::QObject::event(arg__1);
    }

    Shiboken::AutoDecRef pyArgs(Py_BuildValue("(N)",
        Shiboken::Conversions::pointerToPython((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QEVENT_IDX], arg__1)
    ));
    bool invalidateArg1 = PyTuple_GET_ITEM(pyArgs, 0)->ob_refcnt == 1;

    Shiboken::AutoDecRef pyResult(PyObject_Call(pyOverride, pyArgs, NULL));
    // An error happened in python code!
    if (pyResult.isNull()) {
        PyErr_Print();
        return ((bool)0);
    }
    // Check return type
    PythonToCppFunc pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), pyResult);
    if (!pythonToCpp) {
        Shiboken::warning(PyExc_RuntimeWarning, 2, "Invalid return value in function %s, expected %s, got %s.", "TextHook.event", "bool", pyResult->ob_type->tp_name);
        return ((bool)0);
    }
    bool cppResult;
    pythonToCpp(pyResult, &cppResult);
    if (invalidateArg1)
        Shiboken::Object::invalidate(PyTuple_GET_ITEM(pyArgs, 0));
    return cppResult;
}

bool TextHookWrapper::eventFilter(QObject * arg__1, QEvent * arg__2)
{
    Shiboken::GilState gil;
    if (PyErr_Occurred())
        return ((bool)0);
    Shiboken::AutoDecRef pyOverride(Shiboken::BindingManager::instance().getOverride(this, "eventFilter"));
    if (pyOverride.isNull()) {
        gil.release();
        return this->::QObject::eventFilter(arg__1, arg__2);
    }

    Shiboken::AutoDecRef pyArgs(Py_BuildValue("(NN)",
        Shiboken::Conversions::pointerToPython((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QOBJECT_IDX], arg__1),
        Shiboken::Conversions::pointerToPython((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QEVENT_IDX], arg__2)
    ));
    bool invalidateArg2 = PyTuple_GET_ITEM(pyArgs, 1)->ob_refcnt == 1;

    Shiboken::AutoDecRef pyResult(PyObject_Call(pyOverride, pyArgs, NULL));
    // An error happened in python code!
    if (pyResult.isNull()) {
        PyErr_Print();
        return ((bool)0);
    }
    // Check return type
    PythonToCppFunc pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), pyResult);
    if (!pythonToCpp) {
        Shiboken::warning(PyExc_RuntimeWarning, 2, "Invalid return value in function %s, expected %s, got %s.", "TextHook.eventFilter", "bool", pyResult->ob_type->tp_name);
        return ((bool)0);
    }
    bool cppResult;
    pythonToCpp(pyResult, &cppResult);
    if (invalidateArg2)
        Shiboken::Object::invalidate(PyTuple_GET_ITEM(pyArgs, 1));
    return cppResult;
}

void TextHookWrapper::timerEvent(QTimerEvent * arg__1)
{
    Shiboken::GilState gil;
    if (PyErr_Occurred())
        return ;
    Shiboken::AutoDecRef pyOverride(Shiboken::BindingManager::instance().getOverride(this, "timerEvent"));
    if (pyOverride.isNull()) {
        gil.release();
        return this->::QObject::timerEvent(arg__1);
    }

    Shiboken::AutoDecRef pyArgs(Py_BuildValue("(N)",
        Shiboken::Conversions::pointerToPython((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QTIMEREVENT_IDX], arg__1)
    ));
    bool invalidateArg1 = PyTuple_GET_ITEM(pyArgs, 0)->ob_refcnt == 1;

    Shiboken::AutoDecRef pyResult(PyObject_Call(pyOverride, pyArgs, NULL));
    // An error happened in python code!
    if (pyResult.isNull()) {
        PyErr_Print();
        return ;
    }
    if (invalidateArg1)
        Shiboken::Object::invalidate(PyTuple_GET_ITEM(pyArgs, 0));
}

const QMetaObject* TextHookWrapper::metaObject() const
{
    #if QT_VERSION >= 0x040700
    if (QObject::d_ptr->metaObject) return QObject::d_ptr->metaObject;
    #endif
    SbkObject* pySelf = Shiboken::BindingManager::instance().retrieveWrapper(this);
    if (pySelf == NULL)
        return TextHook::metaObject();
    return PySide::SignalManager::retriveMetaObject(reinterpret_cast<PyObject*>(pySelf));
}

int TextHookWrapper::qt_metacall(QMetaObject::Call call, int id, void** args)
{
    int result = TextHook::qt_metacall(call, id, args);
    return result < 0 ? result : PySide::SignalManager::qt_metacall(this, call, id, args);
}

void* TextHookWrapper::qt_metacast(const char* _clname)
{
        if (!_clname) return 0;
        SbkObject* pySelf = Shiboken::BindingManager::instance().retrieveWrapper(this);
        if (pySelf && PySide::inherits(Py_TYPE(pySelf), _clname))
                return static_cast<void*>(const_cast< TextHookWrapper* >(this));
        return TextHook::qt_metacast(_clname);
}

TextHookWrapper::~TextHookWrapper()
{
    SbkObject* wrapper = Shiboken::BindingManager::instance().retrieveWrapper(this);
    Shiboken::Object::destroy(wrapper, this);
}

// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_TextHook_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    const char* argNames[] = {"parent"};
    const QMetaObject* metaObject;
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::TextHook >()))
        return -1;

    ::TextHookWrapper* cptr = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0 };
    SBK_UNUSED(pythonToCpp)
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0};

    // invalid argument lengths


    if (!PyArg_ParseTuple(args, "|O:TextHook", &(pyArgs[0])))
        return -1;


    // Overloaded function decisor
    // 0: TextHook(QObject*)
    if (numArgs == 0) {
        overloadId = 0; // TextHook(QObject*)
    } else if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppPointerConvertible((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QOBJECT_IDX], (pyArgs[0])))) {
        overloadId = 0; // TextHook(QObject*)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHook_Init_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "parent");
            if (value && pyArgs[0]) {
                PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook(): got multiple values for keyword argument 'parent'.");
                return -1;
            } else if (value) {
                pyArgs[0] = value;
                if (!(pythonToCpp[0] = Shiboken::Conversions::isPythonToCppPointerConvertible((SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QOBJECT_IDX], (pyArgs[0]))))
                    goto Sbk_TextHook_Init_TypeError;
            }
        }
        if (!Shiboken::Object::isValid(pyArgs[0]))
            return -1;
        ::QObject* cppArg0 = nullptr;
        if (pythonToCpp[0]) pythonToCpp[0](pyArgs[0], &cppArg0);

        if (!PyErr_Occurred()) {
            // TextHook(QObject*)
            void* addr = PySide::nextQObjectMemoryAddr();
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            if (addr) {
                cptr = new (addr) ::TextHookWrapper(cppArg0);
                PySide::setNextQObjectMemoryAddr(0);
            } else {
                cptr = new ::TextHookWrapper(cppArg0);
            }

            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            Shiboken::Object::setParent(pyArgs[0], self);
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::TextHook >(), cptr)) {
        delete cptr;
        return -1;
    }
    if (!cptr) goto Sbk_TextHook_Init_TypeError;

    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::Object::setHasCppWrapper(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);

    // QObject setup
    PySide::Signal::updateSourceObject(self);
    metaObject = cptr->metaObject(); // <- init python qt properties
    if (kwds && !PySide::fillQtProperties(self, metaObject, kwds, argNames, 1))
        return -1;


    return 1;

    Sbk_TextHook_Init_TypeError:
        const char* overloads[] = {"PySide.QtCore.QObject = nullptr", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pytexthook.TextHook", overloads);
        return -1;
}

static PyObject* Sbk_TextHookFunc_addHookCode(PyObject* self, PyObject* args, PyObject* kwds)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0, 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0, 0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 4) {
        PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.addHookCode(): too many arguments");
        return 0;
    } else if (numArgs < 2) {
        PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.addHookCode(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OOOO:addHookCode", &(pyArgs[0]), &(pyArgs[1]), &(pyArgs[2]), &(pyArgs[3])))
        return 0;


    // Overloaded function decisor
    // 0: addHookCode(ulong,QString,QString,bool)
    if (numArgs >= 2
        && (pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArgs[0])))
        && (pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[1])))) {
        if (numArgs == 2) {
            overloadId = 0; // addHookCode(ulong,QString,QString,bool)
        } else if ((pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[2])))) {
            if (numArgs == 3) {
                overloadId = 0; // addHookCode(ulong,QString,QString,bool)
            } else if ((pythonToCpp[3] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[3])))) {
                overloadId = 0; // addHookCode(ulong,QString,QString,bool)
            }
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_addHookCode_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "name");
            if (value && pyArgs[2]) {
                PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.addHookCode(): got multiple values for keyword argument 'name'.");
                return 0;
            } else if (value) {
                pyArgs[2] = value;
                if (!(pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[2]))))
                    goto Sbk_TextHookFunc_addHookCode_TypeError;
            }
            value = PyDict_GetItemString(kwds, "verbose");
            if (value && pyArgs[3]) {
                PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.addHookCode(): got multiple values for keyword argument 'verbose'.");
                return 0;
            } else if (value) {
                pyArgs[3] = value;
                if (!(pythonToCpp[3] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[3]))))
                    goto Sbk_TextHookFunc_addHookCode_TypeError;
            }
        }
        ulong cppArg0;
        pythonToCpp[0](pyArgs[0], &cppArg0);
        ::QString cppArg1 = ::QString();
        pythonToCpp[1](pyArgs[1], &cppArg1);
        ::QString cppArg2 = QString();
        if (pythonToCpp[2]) pythonToCpp[2](pyArgs[2], &cppArg2);
        bool cppArg3 = true;
        if (pythonToCpp[3]) pythonToCpp[3](pyArgs[3], &cppArg3);

        if (!PyErr_Occurred()) {
            // addHookCode(ulong,QString,QString,bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->addHookCode(cppArg0, cppArg1, cppArg2, cppArg3);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TextHookFunc_addHookCode_TypeError:
        const char* overloads[] = {"unsigned long, unicode, unicode = QString(), bool = true", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pytexthook.TextHook.addHookCode", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_attachProcess(PyObject* self, PyObject* args, PyObject* kwds)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.attachProcess(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.attachProcess(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:attachProcess", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: attachProcess(ulong,bool)
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // attachProcess(ulong,bool)
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1])))) {
            overloadId = 0; // attachProcess(ulong,bool)
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_attachProcess_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "checkActive");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.attachProcess(): got multiple values for keyword argument 'checkActive'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1]))))
                    goto Sbk_TextHookFunc_attachProcess_TypeError;
            }
        }
        ulong cppArg0;
        pythonToCpp[0](pyArgs[0], &cppArg0);
        bool cppArg1 = false;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // attachProcess(ulong,bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->attachProcess(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TextHookFunc_attachProcess_TypeError:
        const char* overloads[] = {"unsigned long, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pytexthook.TextHook.attachProcess", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_capacity(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // capacity()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->capacity();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<int>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_clear(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // clear()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->clear();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;
}

static PyObject* Sbk_TextHookFunc_clearThreadWhitelist(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // clearThreadWhitelist()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->clearThreadWhitelist();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;
}

static PyObject* Sbk_TextHookFunc_containsProcess(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: containsProcess(ulong)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArg)))) {
        overloadId = 0; // containsProcess(ulong)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_containsProcess_TypeError;

    // Call function/method
    {
        ulong cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // containsProcess(ulong)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->containsProcess(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TextHookFunc_containsProcess_TypeError:
        const char* overloads[] = {"unsigned long", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.containsProcess", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_dataCapacity(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // dataCapacity()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->dataCapacity();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<int>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_defaultHookName(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // defaultHookName()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->defaultHookName();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_detachProcess(PyObject* self, PyObject* args, PyObject* kwds)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.detachProcess(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.detachProcess(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:detachProcess", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: detachProcess(ulong,bool)
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // detachProcess(ulong,bool)
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1])))) {
            overloadId = 0; // detachProcess(ulong,bool)
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_detachProcess_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "checkActive");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pytexthook.TextHook.detachProcess(): got multiple values for keyword argument 'checkActive'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1]))))
                    goto Sbk_TextHookFunc_detachProcess_TypeError;
            }
        }
        ulong cppArg0;
        pythonToCpp[0](pyArgs[0], &cppArg0);
        bool cppArg1 = false;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // detachProcess(ulong,bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->detachProcess(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TextHookFunc_detachProcess_TypeError:
        const char* overloads[] = {"unsigned long, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pytexthook.TextHook.detachProcess", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_hijackProcess(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: hijackProcess(ulong)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArg)))) {
        overloadId = 0; // hijackProcess(ulong)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_hijackProcess_TypeError;

    // Call function/method
    {
        ulong cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // hijackProcess(ulong)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->hijackProcess(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TextHookFunc_hijackProcess_TypeError:
        const char* overloads[] = {"unsigned long", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.hijackProcess", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_interval(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // interval()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->interval();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<int>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_isActive(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isActive()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->isActive();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_isEmpty(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isEmpty()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->isEmpty();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_isEnabled(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isEnabled()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->isEnabled();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_isThreadWhitelistEnabled(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isThreadWhitelistEnabled()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->isThreadWhitelistEnabled();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_keepsSpace(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // keepsSpace()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->keepsSpace();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_keptThreadName(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // keptThreadName()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->keptThreadName();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_parentWinId(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // parentWinId()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            WId cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->parentWinId();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtGuiTypeConverters[SBK_WID_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_removeHookCode(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: removeHookCode(ulong)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArg)))) {
        overloadId = 0; // removeHookCode(ulong)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_removeHookCode_TypeError;

    // Call function/method
    {
        ulong cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // removeHookCode(ulong)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->removeHookCode(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TextHookFunc_removeHookCode_TypeError:
        const char* overloads[] = {"unsigned long", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.removeHookCode", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_removesRepeat(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // removesRepeat()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->removesRepeat();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_setDataCapacity(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setDataCapacity(int)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArg)))) {
        overloadId = 0; // setDataCapacity(int)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setDataCapacity_TypeError;

    // Call function/method
    {
        int cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setDataCapacity(int)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setDataCapacity(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setDataCapacity_TypeError:
        const char* overloads[] = {"int", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setDataCapacity", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setDefaultHookName(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setDefaultHookName(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // setDefaultHookName(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setDefaultHookName_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setDefaultHookName(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setDefaultHookName(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setDefaultHookName_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setDefaultHookName", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setEnabled(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setEnabled(bool)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArg)))) {
        overloadId = 0; // setEnabled(bool)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setEnabled_TypeError;

    // Call function/method
    {
        bool cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setEnabled(bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setEnabled(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setEnabled_TypeError:
        const char* overloads[] = {"bool", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setEnabled", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setInterval(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setInterval(int)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArg)))) {
        overloadId = 0; // setInterval(int)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setInterval_TypeError;

    // Call function/method
    {
        int cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setInterval(int)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setInterval(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setInterval_TypeError:
        const char* overloads[] = {"int", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setInterval", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setKeepsSpace(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setKeepsSpace(bool)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArg)))) {
        overloadId = 0; // setKeepsSpace(bool)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setKeepsSpace_TypeError;

    // Call function/method
    {
        bool cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setKeepsSpace(bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setKeepsSpace(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setKeepsSpace_TypeError:
        const char* overloads[] = {"bool", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setKeepsSpace", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setKeptThreadName(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setKeptThreadName(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // setKeptThreadName(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setKeptThreadName_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setKeptThreadName(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setKeptThreadName(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setKeptThreadName_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setKeptThreadName", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setParentWinId(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setParentWinId(WId)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtGuiTypeConverters[SBK_WID_IDX], (pyArg)))) {
        overloadId = 0; // setParentWinId(WId)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setParentWinId_TypeError;

    // Call function/method
    {
        ::WId cppArg0 = ::WId();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setParentWinId(WId)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setParentWinId(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setParentWinId_TypeError:
        const char* overloads[] = {"HWND", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setParentWinId", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setRemovesRepeat(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setRemovesRepeat(bool)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArg)))) {
        overloadId = 0; // setRemovesRepeat(bool)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setRemovesRepeat_TypeError;

    // Call function/method
    {
        bool cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setRemovesRepeat(bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setRemovesRepeat(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setRemovesRepeat_TypeError:
        const char* overloads[] = {"bool", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setRemovesRepeat", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setThreadWhitelist(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setThreadWhitelist(QList<qint32>)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpytexthookTypeConverters[SBK_PYTEXTHOOK_QLIST_QINT32_IDX], (pyArg)))) {
        overloadId = 0; // setThreadWhitelist(QList<qint32>)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setThreadWhitelist_TypeError;

    // Call function/method
    {
        ::QList<qint32 > cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setThreadWhitelist(QList<qint32>)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setThreadWhitelist(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setThreadWhitelist_TypeError:
        const char* overloads[] = {"list", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setThreadWhitelist", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setThreadWhitelistEnabled(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setThreadWhitelistEnabled(bool)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArg)))) {
        overloadId = 0; // setThreadWhitelistEnabled(bool)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setThreadWhitelistEnabled_TypeError;

    // Call function/method
    {
        bool cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setThreadWhitelistEnabled(bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setThreadWhitelistEnabled(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setThreadWhitelistEnabled_TypeError:
        const char* overloads[] = {"bool", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setThreadWhitelistEnabled", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_setWideCharacter(PyObject* self, PyObject* pyArg)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setWideCharacter(bool)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArg)))) {
        overloadId = 0; // setWideCharacter(bool)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_setWideCharacter_TypeError;

    // Call function/method
    {
        bool cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setWideCharacter(bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setWideCharacter(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_TextHookFunc_setWideCharacter_TypeError:
        const char* overloads[] = {"bool", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.setWideCharacter", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_start(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // start()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->start();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;
}

static PyObject* Sbk_TextHookFunc_stop(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // stop()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->stop();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;
}

static PyObject* Sbk_TextHookFunc_threadWhitelist(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // threadWhitelist()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QList<qint32 > cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->threadWhitelist();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpytexthookTypeConverters[SBK_PYTEXTHOOK_QLIST_QINT32_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_TextHookFunc_verifyHookCode(PyObject* self, PyObject* pyArg)
{
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: verifyHookCode(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // verifyHookCode(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TextHookFunc_verifyHookCode_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // verifyHookCode(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = ::TextHook::verifyHookCode(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TextHookFunc_verifyHookCode_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytexthook.TextHook.verifyHookCode", overloads);
        return 0;
}

static PyObject* Sbk_TextHookFunc_wideCharacter(PyObject* self)
{
    TextHookWrapper* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = (TextHookWrapper*)((::TextHook*)Shiboken::Conversions::cppPointer(SbkpytexthookTypes[SBK_TEXTHOOK_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // wideCharacter()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TextHookWrapper*>(cppSelf)->wideCharacter();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyMethodDef Sbk_TextHook_methods[] = {
    {"addHookCode", (PyCFunction)Sbk_TextHookFunc_addHookCode, METH_VARARGS|METH_KEYWORDS},
    {"attachProcess", (PyCFunction)Sbk_TextHookFunc_attachProcess, METH_VARARGS|METH_KEYWORDS},
    {"capacity", (PyCFunction)Sbk_TextHookFunc_capacity, METH_NOARGS},
    {"clear", (PyCFunction)Sbk_TextHookFunc_clear, METH_NOARGS},
    {"clearThreadWhitelist", (PyCFunction)Sbk_TextHookFunc_clearThreadWhitelist, METH_NOARGS},
    {"containsProcess", (PyCFunction)Sbk_TextHookFunc_containsProcess, METH_O},
    {"dataCapacity", (PyCFunction)Sbk_TextHookFunc_dataCapacity, METH_NOARGS},
    {"defaultHookName", (PyCFunction)Sbk_TextHookFunc_defaultHookName, METH_NOARGS},
    {"detachProcess", (PyCFunction)Sbk_TextHookFunc_detachProcess, METH_VARARGS|METH_KEYWORDS},
    {"hijackProcess", (PyCFunction)Sbk_TextHookFunc_hijackProcess, METH_O},
    {"interval", (PyCFunction)Sbk_TextHookFunc_interval, METH_NOARGS},
    {"isActive", (PyCFunction)Sbk_TextHookFunc_isActive, METH_NOARGS},
    {"isEmpty", (PyCFunction)Sbk_TextHookFunc_isEmpty, METH_NOARGS},
    {"isEnabled", (PyCFunction)Sbk_TextHookFunc_isEnabled, METH_NOARGS},
    {"isThreadWhitelistEnabled", (PyCFunction)Sbk_TextHookFunc_isThreadWhitelistEnabled, METH_NOARGS},
    {"keepsSpace", (PyCFunction)Sbk_TextHookFunc_keepsSpace, METH_NOARGS},
    {"keptThreadName", (PyCFunction)Sbk_TextHookFunc_keptThreadName, METH_NOARGS},
    {"parentWinId", (PyCFunction)Sbk_TextHookFunc_parentWinId, METH_NOARGS},
    {"removeHookCode", (PyCFunction)Sbk_TextHookFunc_removeHookCode, METH_O},
    {"removesRepeat", (PyCFunction)Sbk_TextHookFunc_removesRepeat, METH_NOARGS},
    {"setDataCapacity", (PyCFunction)Sbk_TextHookFunc_setDataCapacity, METH_O},
    {"setDefaultHookName", (PyCFunction)Sbk_TextHookFunc_setDefaultHookName, METH_O},
    {"setEnabled", (PyCFunction)Sbk_TextHookFunc_setEnabled, METH_O},
    {"setInterval", (PyCFunction)Sbk_TextHookFunc_setInterval, METH_O},
    {"setKeepsSpace", (PyCFunction)Sbk_TextHookFunc_setKeepsSpace, METH_O},
    {"setKeptThreadName", (PyCFunction)Sbk_TextHookFunc_setKeptThreadName, METH_O},
    {"setParentWinId", (PyCFunction)Sbk_TextHookFunc_setParentWinId, METH_O},
    {"setRemovesRepeat", (PyCFunction)Sbk_TextHookFunc_setRemovesRepeat, METH_O},
    {"setThreadWhitelist", (PyCFunction)Sbk_TextHookFunc_setThreadWhitelist, METH_O},
    {"setThreadWhitelistEnabled", (PyCFunction)Sbk_TextHookFunc_setThreadWhitelistEnabled, METH_O},
    {"setWideCharacter", (PyCFunction)Sbk_TextHookFunc_setWideCharacter, METH_O},
    {"start", (PyCFunction)Sbk_TextHookFunc_start, METH_NOARGS},
    {"stop", (PyCFunction)Sbk_TextHookFunc_stop, METH_NOARGS},
    {"threadWhitelist", (PyCFunction)Sbk_TextHookFunc_threadWhitelist, METH_NOARGS},
    {"verifyHookCode", (PyCFunction)Sbk_TextHookFunc_verifyHookCode, METH_O|METH_STATIC},
    {"wideCharacter", (PyCFunction)Sbk_TextHookFunc_wideCharacter, METH_NOARGS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_TextHook_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_TextHook_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_TextHook_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pytexthook.TextHook",
    /*tp_basicsize*/        sizeof(SbkObject),
    /*tp_itemsize*/         0,
    /*tp_dealloc*/          &SbkDeallocWrapper,
    /*tp_print*/            0,
    /*tp_getattr*/          0,
    /*tp_setattr*/          0,
    /*tp_compare*/          0,
    /*tp_repr*/             0,
    /*tp_as_number*/        0,
    /*tp_as_sequence*/      0,
    /*tp_as_mapping*/       0,
    /*tp_hash*/             0,
    /*tp_call*/             0,
    /*tp_str*/              0,
    /*tp_getattro*/         0,
    /*tp_setattro*/         0,
    /*tp_as_buffer*/        0,
    /*tp_flags*/            Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_CHECKTYPES|Py_TPFLAGS_HAVE_GC,
    /*tp_doc*/              0,
    /*tp_traverse*/         Sbk_TextHook_traverse,
    /*tp_clear*/            Sbk_TextHook_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_TextHook_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             0,
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_TextHook_Init,
    /*tp_alloc*/            0,
    /*tp_new*/              SbkObjectTpNew,
    /*tp_free*/             0,
    /*tp_is_gc*/            0,
    /*tp_bases*/            0,
    /*tp_mro*/              0,
    /*tp_cache*/            0,
    /*tp_subclasses*/       0,
    /*tp_weaklist*/         0
}, },
    /*priv_data*/           0
};
} //extern

static void* Sbk_TextHook_typeDiscovery(void* cptr, SbkObjectType* instanceType)
{
    if (instanceType == reinterpret_cast<SbkObjectType*>(Shiboken::SbkType< ::QObject >()))
        return dynamic_cast< ::TextHook*>(reinterpret_cast< ::QObject*>(cptr));
    return 0;
}


// Type conversion functions.

// Python to C++ pointer conversion - returns the C++ object of the Python wrapper (keeps object identity).
static void TextHook_PythonToCpp_TextHook_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_TextHook_Type, pyIn, cppOut);
}
static PythonToCppFunc is_TextHook_PythonToCpp_TextHook_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_TextHook_Type))
        return TextHook_PythonToCpp_TextHook_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* TextHook_PTR_CppToPython_TextHook(const void* cppIn) {
    return PySide::getWrapperForQObject((::TextHook*)cppIn, &Sbk_TextHook_Type);

}

void init_TextHook(PyObject* module)
{
    SbkpytexthookTypes[SBK_TEXTHOOK_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_TextHook_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "TextHook", "TextHook*",
        &Sbk_TextHook_Type, &Shiboken::callCppDestructor< ::TextHook >, (SbkObjectType*)SbkPySide_QtCoreTypes[SBK_QOBJECT_IDX])) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_TextHook_Type,
        TextHook_PythonToCpp_TextHook_PTR,
        is_TextHook_PythonToCpp_TextHook_PTR_Convertible,
        TextHook_PTR_CppToPython_TextHook);

    Shiboken::Conversions::registerConverterName(converter, "TextHook");
    Shiboken::Conversions::registerConverterName(converter, "TextHook*");
    Shiboken::Conversions::registerConverterName(converter, "TextHook&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::TextHook).name());
    Shiboken::Conversions::registerConverterName(converter, typeid(::TextHookWrapper).name());


    Shiboken::ObjectType::setTypeDiscoveryFunctionV2(&Sbk_TextHook_Type, &Sbk_TextHook_typeDiscovery);

    PySide::Signal::registerSignals(&Sbk_TextHook_Type, &::TextHook::staticMetaObject);

    TextHookWrapper::pysideInitQtMetaTypes();
    Shiboken::ObjectType::setSubTypeInitHook(&Sbk_TextHook_Type, &PySide::initQObjectSubType);
    PySide::initDynamicMetaObject(&Sbk_TextHook_Type, &::TextHook::staticMetaObject, sizeof(::TextHook));
}
