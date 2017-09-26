
// default includes
#include <shiboken.h>
#include <pysidesignal.h>
#include <pysideproperty.h>
#include <pyside.h>
#include <destroylistener.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pymsime_python.h"

#include "msime_wrapper.h"

// Extra includes
#include <QList>
#include <QPair>
#include <pymsime.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_Msime_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::Msime >()))
        return -1;

    ::Msime* cptr = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0 };
    SBK_UNUSED(pythonToCpp)
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0};

    // invalid argument lengths


    if (!PyArg_UnpackTuple(args, "Msime", 1, 1, &(pyArgs[0])))
        return -1;


    // Overloaded function decisor
    // 0: Msime(int)
    if (numArgs == 1
        && (pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[0])))) {
        overloadId = 0; // Msime(int)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_Msime_Init_TypeError;

    // Call function/method
    {
        int cppArg0;
        pythonToCpp[0](pyArgs[0], &cppArg0);

        if (!PyErr_Occurred()) {
            // Msime(int)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::Msime(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::Msime >(), cptr)) {
        delete cptr;
        return -1;
    }
    if (!cptr) goto Sbk_Msime_Init_TypeError;

    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;

    Sbk_Msime_Init_TypeError:
        const char* overloads[] = {"int", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pymsime.Msime", overloads);
        return -1;
}

static PyObject* Sbk_MsimeFunc_isValid(PyObject* self)
{
    ::Msime* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::Msime*)Shiboken::Conversions::cppPointer(SbkpymsimeTypes[SBK_MSIME_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isValid()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::Msime*>(cppSelf)->isValid();
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

static PyObject* Sbk_MsimeFunc_toKanji(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::Msime* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::Msime*)Shiboken::Conversions::cppPointer(SbkpymsimeTypes[SBK_MSIME_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pymsime.Msime.toKanji(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pymsime.Msime.toKanji(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:toKanji", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: toKanji(QString,ulong)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // toKanji(QString,ulong)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArgs[1])))) {
            overloadId = 0; // toKanji(QString,ulong)const
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_MsimeFunc_toKanji_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "flags");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pymsime.Msime.toKanji(): got multiple values for keyword argument 'flags'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArgs[1]))))
                    goto Sbk_MsimeFunc_toKanji_TypeError;
            }
        }
        ::QString cppArg0 = ::QString();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        ulong cppArg1 = 0;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // toKanji(QString,ulong)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::Msime*>(cppSelf)->toKanji(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_MsimeFunc_toKanji_TypeError:
        const char* overloads[] = {"unicode, unsigned long = 0", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pymsime.Msime.toKanji", overloads);
        return 0;
}

static PyObject* Sbk_MsimeFunc_toKanjiList(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::Msime* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::Msime*)Shiboken::Conversions::cppPointer(SbkpymsimeTypes[SBK_MSIME_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pymsime.Msime.toKanjiList(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pymsime.Msime.toKanjiList(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:toKanjiList", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: toKanjiList(QString,ulong)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // toKanjiList(QString,ulong)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArgs[1])))) {
            overloadId = 0; // toKanjiList(QString,ulong)const
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_MsimeFunc_toKanjiList_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "flags");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pymsime.Msime.toKanjiList(): got multiple values for keyword argument 'flags'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<ulong>(), (pyArgs[1]))))
                    goto Sbk_MsimeFunc_toKanjiList_TypeError;
            }
        }
        ::QString cppArg0 = ::QString();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        ulong cppArg1 = 0;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // toKanjiList(QString,ulong)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QList<QPair<QString, QString > > cppResult = const_cast<const ::Msime*>(cppSelf)->toKanjiList(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpymsimeTypeConverters[SBK_PYMSIME_QLIST_QPAIR_QSTRING_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_MsimeFunc_toKanjiList_TypeError:
        const char* overloads[] = {"unicode, unsigned long = 0", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pymsime.Msime.toKanjiList", overloads);
        return 0;
}

static PyObject* Sbk_MsimeFunc_toRuby(PyObject* self, PyObject* args)
{
    ::Msime* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::Msime*)Shiboken::Conversions::cppPointer(SbkpymsimeTypes[SBK_MSIME_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths


    if (!PyArg_UnpackTuple(args, "toRuby", 2, 2, &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: toRuby(QString,int)const
    if (numArgs == 2
        && (pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[0])))
        && (pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1])))) {
        overloadId = 0; // toRuby(QString,int)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_MsimeFunc_toRuby_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        int cppArg1;
        pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // toRuby(QString,int)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::Msime*>(cppSelf)->toRuby(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_MsimeFunc_toRuby_TypeError:
        const char* overloads[] = {"unicode, int", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pymsime.Msime.toRuby", overloads);
        return 0;
}

static PyObject* Sbk_MsimeFunc_toRubyList(PyObject* self, PyObject* args)
{
    ::Msime* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::Msime*)Shiboken::Conversions::cppPointer(SbkpymsimeTypes[SBK_MSIME_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths


    if (!PyArg_UnpackTuple(args, "toRubyList", 2, 2, &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: toRubyList(QString,int)const
    if (numArgs == 2
        && (pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArgs[0])))
        && (pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1])))) {
        overloadId = 0; // toRubyList(QString,int)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_MsimeFunc_toRubyList_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        int cppArg1;
        pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // toRubyList(QString,int)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QList<QPair<QString, QString > > cppResult = const_cast<const ::Msime*>(cppSelf)->toRubyList(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpymsimeTypeConverters[SBK_PYMSIME_QLIST_QPAIR_QSTRING_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_MsimeFunc_toRubyList_TypeError:
        const char* overloads[] = {"unicode, int", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pymsime.Msime.toRubyList", overloads);
        return 0;
}

static PyMethodDef Sbk_Msime_methods[] = {
    {"isValid", (PyCFunction)Sbk_MsimeFunc_isValid, METH_NOARGS},
    {"toKanji", (PyCFunction)Sbk_MsimeFunc_toKanji, METH_VARARGS|METH_KEYWORDS},
    {"toKanjiList", (PyCFunction)Sbk_MsimeFunc_toKanjiList, METH_VARARGS|METH_KEYWORDS},
    {"toRuby", (PyCFunction)Sbk_MsimeFunc_toRuby, METH_VARARGS},
    {"toRubyList", (PyCFunction)Sbk_MsimeFunc_toRubyList, METH_VARARGS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_Msime_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_Msime_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_Msime_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pymsime.Msime",
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
    /*tp_traverse*/         Sbk_Msime_traverse,
    /*tp_clear*/            Sbk_Msime_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_Msime_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_Msime_Init,
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

// Python to C++ enum conversion.
static void Msime_Ruby_PythonToCpp_Msime_Ruby(PyObject* pyIn, void* cppOut) {
    *((::Msime::Ruby*)cppOut) = (::Msime::Ruby) Shiboken::Enum::getValue(pyIn);

}
static PythonToCppFunc is_Msime_Ruby_PythonToCpp_Msime_Ruby_Convertible(PyObject* pyIn) {
    if (PyObject_TypeCheck(pyIn, SbkpymsimeTypes[SBK_MSIME_RUBY_IDX]))
        return Msime_Ruby_PythonToCpp_Msime_Ruby;
    return 0;
}
static PyObject* Msime_Ruby_CppToPython_Msime_Ruby(const void* cppIn) {
    int castCppIn = *((::Msime::Ruby*)cppIn);
    return Shiboken::Enum::newItem(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX], castCppIn);

}

static void Msime_Language_PythonToCpp_Msime_Language(PyObject* pyIn, void* cppOut) {
    *((::Msime::Language*)cppOut) = (::Msime::Language) Shiboken::Enum::getValue(pyIn);

}
static PythonToCppFunc is_Msime_Language_PythonToCpp_Msime_Language_Convertible(PyObject* pyIn) {
    if (PyObject_TypeCheck(pyIn, SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX]))
        return Msime_Language_PythonToCpp_Msime_Language;
    return 0;
}
static PyObject* Msime_Language_CppToPython_Msime_Language(const void* cppIn) {
    int castCppIn = *((::Msime::Language*)cppIn);
    return Shiboken::Enum::newItem(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX], castCppIn);

}

// Python to C++ pointer conversion - returns the C++ object of the Python wrapper (keeps object identity).
static void Msime_PythonToCpp_Msime_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_Msime_Type, pyIn, cppOut);
}
static PythonToCppFunc is_Msime_PythonToCpp_Msime_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_Msime_Type))
        return Msime_PythonToCpp_Msime_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* Msime_PTR_CppToPython_Msime(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::Msime*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_Msime_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_Msime(PyObject* module)
{
    SbkpymsimeTypes[SBK_MSIME_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_Msime_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "Msime", "Msime*",
        &Sbk_Msime_Type, &Shiboken::callCppDestructor< ::Msime >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_Msime_Type,
        Msime_PythonToCpp_Msime_PTR,
        is_Msime_PythonToCpp_Msime_PTR_Convertible,
        Msime_PTR_CppToPython_Msime);

    Shiboken::Conversions::registerConverterName(converter, "Msime");
    Shiboken::Conversions::registerConverterName(converter, "Msime*");
    Shiboken::Conversions::registerConverterName(converter, "Msime&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::Msime).name());


    // Initialization of enums.

    // Initialization of enum 'Ruby'.
    SbkpymsimeTypes[SBK_MSIME_RUBY_IDX] = Shiboken::Enum::createScopedEnum(&Sbk_Msime_Type,
        "Ruby",
        "pymsime.Msime.Ruby",
        "Msime::Ruby");
    if (!SbkpymsimeTypes[SBK_MSIME_RUBY_IDX])
        return ;

    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX],
        &Sbk_Msime_Type, "NoRuby", (long) Msime::NoRuby))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX],
        &Sbk_Msime_Type, "Pinyin", (long) Msime::Pinyin))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX],
        &Sbk_Msime_Type, "Roman", (long) Msime::Roman))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX],
        &Sbk_Msime_Type, "Hiragana", (long) Msime::Hiragana))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX],
        &Sbk_Msime_Type, "Katagana", (long) Msime::Katagana))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX],
        &Sbk_Msime_Type, "Hangul", (long) Msime::Hangul))
        return ;
    // Register converter for enum 'Msime::Ruby'.
    {
        SbkConverter* converter = Shiboken::Conversions::createConverter(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX],
            Msime_Ruby_CppToPython_Msime_Ruby);
        Shiboken::Conversions::addPythonToCppValueConversion(converter,
            Msime_Ruby_PythonToCpp_Msime_Ruby,
            is_Msime_Ruby_PythonToCpp_Msime_Ruby_Convertible);
        Shiboken::Enum::setTypeConverter(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX], converter);
        Shiboken::Enum::setTypeConverter(SbkpymsimeTypes[SBK_MSIME_RUBY_IDX], converter);
        Shiboken::Conversions::registerConverterName(converter, "Msime::Ruby");
        Shiboken::Conversions::registerConverterName(converter, "Ruby");
    }
    // End of 'Ruby' enum.

    // Initialization of enum 'Language'.
    SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX] = Shiboken::Enum::createScopedEnum(&Sbk_Msime_Type,
        "Language",
        "pymsime.Msime.Language",
        "Msime::Language");
    if (!SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX])
        return ;

    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX],
        &Sbk_Msime_Type, "NoLanguage", (long) Msime::NoLanguage))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX],
        &Sbk_Msime_Type, "SimplifiedChinese", (long) Msime::SimplifiedChinese))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX],
        &Sbk_Msime_Type, "TraditionalChinese", (long) Msime::TraditionalChinese))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX],
        &Sbk_Msime_Type, "Japanese", (long) Msime::Japanese))
        return ;
    if (!Shiboken::Enum::createScopedEnumItem(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX],
        &Sbk_Msime_Type, "Korean", (long) Msime::Korean))
        return ;
    // Register converter for enum 'Msime::Language'.
    {
        SbkConverter* converter = Shiboken::Conversions::createConverter(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX],
            Msime_Language_CppToPython_Msime_Language);
        Shiboken::Conversions::addPythonToCppValueConversion(converter,
            Msime_Language_PythonToCpp_Msime_Language,
            is_Msime_Language_PythonToCpp_Msime_Language_Convertible);
        Shiboken::Enum::setTypeConverter(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX], converter);
        Shiboken::Enum::setTypeConverter(SbkpymsimeTypes[SBK_MSIME_LANGUAGE_IDX], converter);
        Shiboken::Conversions::registerConverterName(converter, "Msime::Language");
        Shiboken::Conversions::registerConverterName(converter, "Language");
    }
    // End of 'Language' enum.


    qRegisterMetaType< ::Msime::Ruby >("Msime::Ruby");
    qRegisterMetaType< ::Msime::Language >("Msime::Language");
}
