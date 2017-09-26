
// default includes
#include <shiboken.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pytrcodec_python.h"

#include "translationcoder_wrapper.h"

// Extra includes
#include <trcodec.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_TranslationCoder_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::TranslationCoder >()))
        return -1;

    ::TranslationCoder* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // TranslationCoder()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::TranslationCoder();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::TranslationCoder >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_TranslationCoderFunc_clear(PyObject* self)
{
    ::TranslationCoder* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationCoder*)Shiboken::Conversions::cppPointer(SbkpytrcodecTypes[SBK_TRANSLATIONCODER_IDX], (SbkObject*)self));

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

static PyObject* Sbk_TranslationCoderFunc_decode(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::TranslationCoder* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationCoder*)Shiboken::Conversions::cppPointer(SbkpytrcodecTypes[SBK_TRANSLATIONCODER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 3) {
        PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.decode(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.decode(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OOO:decode", &(pyArgs[0]), &(pyArgs[1]), &(pyArgs[2])))
        return 0;


    // Overloaded function decisor
    // 0: decode(std::wstring,int,bool)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkpytrcodecTypeConverters[SBK_STD_WSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // decode(std::wstring,int,bool)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1])))) {
            if (numArgs == 2) {
                overloadId = 0; // decode(std::wstring,int,bool)const
            } else if ((pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[2])))) {
                overloadId = 0; // decode(std::wstring,int,bool)const
            }
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TranslationCoderFunc_decode_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "selector");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.decode(): got multiple values for keyword argument 'selector'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1]))))
                    goto Sbk_TranslationCoderFunc_decode_TypeError;
            }
            value = PyDict_GetItemString(kwds, "mark");
            if (value && pyArgs[2]) {
                PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.decode(): got multiple values for keyword argument 'mark'.");
                return 0;
            } else if (value) {
                pyArgs[2] = value;
                if (!(pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[2]))))
                    goto Sbk_TranslationCoderFunc_decode_TypeError;
            }
        }
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        int cppArg1 = -1;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);
        bool cppArg2 = false;
        if (pythonToCpp[2]) pythonToCpp[2](pyArgs[2], &cppArg2);

        if (!PyErr_Occurred()) {
            // decode(std::wstring,int,bool)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = const_cast<const ::TranslationCoder*>(cppSelf)->decode(cppArg0, cppArg1, cppArg2);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpytrcodecTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TranslationCoderFunc_decode_TypeError:
        const char* overloads[] = {"std::wstring, int = -1, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pytrcodec.TranslationCoder.decode", overloads);
        return 0;
}

static PyObject* Sbk_TranslationCoderFunc_encode(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::TranslationCoder* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationCoder*)Shiboken::Conversions::cppPointer(SbkpytrcodecTypes[SBK_TRANSLATIONCODER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 3) {
        PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.encode(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.encode(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OOO:encode", &(pyArgs[0]), &(pyArgs[1]), &(pyArgs[2])))
        return 0;


    // Overloaded function decisor
    // 0: encode(std::wstring,int,int)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkpytrcodecTypeConverters[SBK_STD_WSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // encode(std::wstring,int,int)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1])))) {
            if (numArgs == 2) {
                overloadId = 0; // encode(std::wstring,int,int)const
            } else if ((pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[2])))) {
                overloadId = 0; // encode(std::wstring,int,int)const
            }
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TranslationCoderFunc_encode_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "selector");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.encode(): got multiple values for keyword argument 'selector'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1]))))
                    goto Sbk_TranslationCoderFunc_encode_TypeError;
            }
            value = PyDict_GetItemString(kwds, "limit");
            if (value && pyArgs[2]) {
                PyErr_SetString(PyExc_TypeError, "pytrcodec.TranslationCoder.encode(): got multiple values for keyword argument 'limit'.");
                return 0;
            } else if (value) {
                pyArgs[2] = value;
                if (!(pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[2]))))
                    goto Sbk_TranslationCoderFunc_encode_TypeError;
            }
        }
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        int cppArg1 = -1;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);
        int cppArg2 = 100;
        if (pythonToCpp[2]) pythonToCpp[2](pyArgs[2], &cppArg2);

        if (!PyErr_Occurred()) {
            // encode(std::wstring,int,int)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = const_cast<const ::TranslationCoder*>(cppSelf)->encode(cppArg0, cppArg1, cppArg2);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpytrcodecTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TranslationCoderFunc_encode_TypeError:
        const char* overloads[] = {"std::wstring, int = -1, int = 100", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pytrcodec.TranslationCoder.encode", overloads);
        return 0;
}

static PyObject* Sbk_TranslationCoderFunc_isEmpty(PyObject* self)
{
    ::TranslationCoder* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationCoder*)Shiboken::Conversions::cppPointer(SbkpytrcodecTypes[SBK_TRANSLATIONCODER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isEmpty()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TranslationCoder*>(cppSelf)->isEmpty();
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

static PyObject* Sbk_TranslationCoderFunc_loadScript(PyObject* self, PyObject* pyArg)
{
    ::TranslationCoder* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationCoder*)Shiboken::Conversions::cppPointer(SbkpytrcodecTypes[SBK_TRANSLATIONCODER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: loadScript(std::wstring)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpytrcodecTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // loadScript(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TranslationCoderFunc_loadScript_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // loadScript(std::wstring)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->loadScript(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TranslationCoderFunc_loadScript_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytrcodec.TranslationCoder.loadScript", overloads);
        return 0;
}

static PyObject* Sbk_TranslationCoderFunc_size(PyObject* self)
{
    ::TranslationCoder* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationCoder*)Shiboken::Conversions::cppPointer(SbkpytrcodecTypes[SBK_TRANSLATIONCODER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // size()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::TranslationCoder*>(cppSelf)->size();
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

static PyMethodDef Sbk_TranslationCoder_methods[] = {
    {"clear", (PyCFunction)Sbk_TranslationCoderFunc_clear, METH_NOARGS},
    {"decode", (PyCFunction)Sbk_TranslationCoderFunc_decode, METH_VARARGS|METH_KEYWORDS},
    {"encode", (PyCFunction)Sbk_TranslationCoderFunc_encode, METH_VARARGS|METH_KEYWORDS},
    {"isEmpty", (PyCFunction)Sbk_TranslationCoderFunc_isEmpty, METH_NOARGS},
    {"loadScript", (PyCFunction)Sbk_TranslationCoderFunc_loadScript, METH_O},
    {"size", (PyCFunction)Sbk_TranslationCoderFunc_size, METH_NOARGS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_TranslationCoder_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_TranslationCoder_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_TranslationCoder_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pytrcodec.TranslationCoder",
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
    /*tp_traverse*/         Sbk_TranslationCoder_traverse,
    /*tp_clear*/            Sbk_TranslationCoder_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_TranslationCoder_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_TranslationCoder_Init,
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
static void TranslationCoder_PythonToCpp_TranslationCoder_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_TranslationCoder_Type, pyIn, cppOut);
}
static PythonToCppFunc is_TranslationCoder_PythonToCpp_TranslationCoder_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_TranslationCoder_Type))
        return TranslationCoder_PythonToCpp_TranslationCoder_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* TranslationCoder_PTR_CppToPython_TranslationCoder(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::TranslationCoder*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_TranslationCoder_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_TranslationCoder(PyObject* module)
{
    SbkpytrcodecTypes[SBK_TRANSLATIONCODER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_TranslationCoder_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "TranslationCoder", "TranslationCoder*",
        &Sbk_TranslationCoder_Type, &Shiboken::callCppDestructor< ::TranslationCoder >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_TranslationCoder_Type,
        TranslationCoder_PythonToCpp_TranslationCoder_PTR,
        is_TranslationCoder_PythonToCpp_TranslationCoder_PTR_Convertible,
        TranslationCoder_PTR_CppToPython_TranslationCoder);

    Shiboken::Conversions::registerConverterName(converter, "TranslationCoder");
    Shiboken::Conversions::registerConverterName(converter, "TranslationCoder*");
    Shiboken::Conversions::registerConverterName(converter, "TranslationCoder&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::TranslationCoder).name());



}
