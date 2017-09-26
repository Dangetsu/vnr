
// default includes
#include <shiboken.h>
#include <pysidesignal.h>
#include <pysideproperty.h>
#include <pyside.h>
#include <destroylistener.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pyhanviet_python.h"

#include "hanviettranslator_wrapper.h"

// Extra includes
#include <QList>
#include <QPair>
#include <hanviettrans.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_HanVietTranslator_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::HanVietTranslator >()))
        return -1;

    ::HanVietTranslator* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // HanVietTranslator()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::HanVietTranslator();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::HanVietTranslator >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_HanVietTranslatorFunc_addPhraseFile(PyObject* self, PyObject* pyArg)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: addPhraseFile(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // addPhraseFile(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_HanVietTranslatorFunc_addPhraseFile_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // addPhraseFile(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->addPhraseFile(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_HanVietTranslatorFunc_addPhraseFile_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanviet.HanVietTranslator.addPhraseFile", overloads);
        return 0;
}

static PyObject* Sbk_HanVietTranslatorFunc_addWordFile(PyObject* self, PyObject* pyArg)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: addWordFile(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // addWordFile(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_HanVietTranslatorFunc_addWordFile_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // addWordFile(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->addWordFile(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_HanVietTranslatorFunc_addWordFile_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanviet.HanVietTranslator.addWordFile", overloads);
        return 0;
}

static PyObject* Sbk_HanVietTranslatorFunc_analyze(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pyhanviet.HanVietTranslator.analyze(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pyhanviet.HanVietTranslator.analyze(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:analyze", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: analyze(QString,bool)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // analyze(QString,bool)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1])))) {
            overloadId = 0; // analyze(QString,bool)const
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_HanVietTranslatorFunc_analyze_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "mark");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pyhanviet.HanVietTranslator.analyze(): got multiple values for keyword argument 'mark'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1]))))
                    goto Sbk_HanVietTranslatorFunc_analyze_TypeError;
            }
        }
        ::QString cppArg0 = ::QString();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        bool cppArg1 = false;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // analyze(QString,bool)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QPair<QString, QList<QPair<QString, QString > > > cppResult = const_cast<const ::HanVietTranslator*>(cppSelf)->analyze(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpyhanvietTypeConverters[SBK_PYHANVIET_QPAIR_QSTRING_QLIST_QPAIR_QSTRING_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_HanVietTranslatorFunc_analyze_TypeError:
        const char* overloads[] = {"unicode, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pyhanviet.HanVietTranslator.analyze", overloads);
        return 0;
}

static PyObject* Sbk_HanVietTranslatorFunc_clear(PyObject* self)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));

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

static PyObject* Sbk_HanVietTranslatorFunc_lookupPhrase(PyObject* self, PyObject* pyArg)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: lookupPhrase(QString)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // lookupPhrase(QString)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_HanVietTranslatorFunc_lookupPhrase_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // lookupPhrase(QString)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::HanVietTranslator*>(cppSelf)->lookupPhrase(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_HanVietTranslatorFunc_lookupPhrase_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanviet.HanVietTranslator.lookupPhrase", overloads);
        return 0;
}

static PyObject* Sbk_HanVietTranslatorFunc_lookupWord(PyObject* self, PyObject* pyArg)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: lookupWord(int)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArg)))) {
        overloadId = 0; // lookupWord(int)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_HanVietTranslatorFunc_lookupWord_TypeError;

    // Call function/method
    {
        int cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // lookupWord(int)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::HanVietTranslator*>(cppSelf)->lookupWord(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_HanVietTranslatorFunc_lookupWord_TypeError:
        const char* overloads[] = {"int", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanviet.HanVietTranslator.lookupWord", overloads);
        return 0;
}

static PyObject* Sbk_HanVietTranslatorFunc_toReading(PyObject* self, PyObject* pyArg)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: toReading(QString)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // toReading(QString)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_HanVietTranslatorFunc_toReading_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // toReading(QString)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::HanVietTranslator*>(cppSelf)->toReading(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_HanVietTranslatorFunc_toReading_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanviet.HanVietTranslator.toReading", overloads);
        return 0;
}

static PyObject* Sbk_HanVietTranslatorFunc_translate(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::HanVietTranslator* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::HanVietTranslator*)Shiboken::Conversions::cppPointer(SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pyhanviet.HanVietTranslator.translate(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pyhanviet.HanVietTranslator.translate(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:translate", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: translate(QString,bool)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // translate(QString,bool)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1])))) {
            overloadId = 0; // translate(QString,bool)const
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_HanVietTranslatorFunc_translate_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "mark");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pyhanviet.HanVietTranslator.translate(): got multiple values for keyword argument 'mark'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1]))))
                    goto Sbk_HanVietTranslatorFunc_translate_TypeError;
            }
        }
        ::QString cppArg0 = ::QString();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        bool cppArg1 = false;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // translate(QString,bool)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::HanVietTranslator*>(cppSelf)->translate(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_HanVietTranslatorFunc_translate_TypeError:
        const char* overloads[] = {"unicode, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pyhanviet.HanVietTranslator.translate", overloads);
        return 0;
}

static PyMethodDef Sbk_HanVietTranslator_methods[] = {
    {"addPhraseFile", (PyCFunction)Sbk_HanVietTranslatorFunc_addPhraseFile, METH_O},
    {"addWordFile", (PyCFunction)Sbk_HanVietTranslatorFunc_addWordFile, METH_O},
    {"analyze", (PyCFunction)Sbk_HanVietTranslatorFunc_analyze, METH_VARARGS|METH_KEYWORDS},
    {"clear", (PyCFunction)Sbk_HanVietTranslatorFunc_clear, METH_NOARGS},
    {"lookupPhrase", (PyCFunction)Sbk_HanVietTranslatorFunc_lookupPhrase, METH_O},
    {"lookupWord", (PyCFunction)Sbk_HanVietTranslatorFunc_lookupWord, METH_O},
    {"toReading", (PyCFunction)Sbk_HanVietTranslatorFunc_toReading, METH_O},
    {"translate", (PyCFunction)Sbk_HanVietTranslatorFunc_translate, METH_VARARGS|METH_KEYWORDS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_HanVietTranslator_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_HanVietTranslator_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_HanVietTranslator_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pyhanviet.HanVietTranslator",
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
    /*tp_traverse*/         Sbk_HanVietTranslator_traverse,
    /*tp_clear*/            Sbk_HanVietTranslator_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_HanVietTranslator_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_HanVietTranslator_Init,
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


// Type conversion functions.

// Python to C++ pointer conversion - returns the C++ object of the Python wrapper (keeps object identity).
static void HanVietTranslator_PythonToCpp_HanVietTranslator_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_HanVietTranslator_Type, pyIn, cppOut);
}
static PythonToCppFunc is_HanVietTranslator_PythonToCpp_HanVietTranslator_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_HanVietTranslator_Type))
        return HanVietTranslator_PythonToCpp_HanVietTranslator_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* HanVietTranslator_PTR_CppToPython_HanVietTranslator(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::HanVietTranslator*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_HanVietTranslator_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_HanVietTranslator(PyObject* module)
{
    SbkpyhanvietTypes[SBK_HANVIETTRANSLATOR_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_HanVietTranslator_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "HanVietTranslator", "HanVietTranslator*",
        &Sbk_HanVietTranslator_Type, &Shiboken::callCppDestructor< ::HanVietTranslator >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_HanVietTranslator_Type,
        HanVietTranslator_PythonToCpp_HanVietTranslator_PTR,
        is_HanVietTranslator_PythonToCpp_HanVietTranslator_PTR_Convertible,
        HanVietTranslator_PTR_CppToPython_HanVietTranslator);

    Shiboken::Conversions::registerConverterName(converter, "HanVietTranslator");
    Shiboken::Conversions::registerConverterName(converter, "HanVietTranslator*");
    Shiboken::Conversions::registerConverterName(converter, "HanVietTranslator&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::HanVietTranslator).name());



}
