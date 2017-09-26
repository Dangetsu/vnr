
// default includes
#include <shiboken.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pysapi_python.h"

#include "sapiplayer_wrapper.h"

// Extra includes
#include <pysapi.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_SapiPlayer_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::SapiPlayer >()))
        return -1;

    ::SapiPlayer* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // SapiPlayer()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::SapiPlayer();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::SapiPlayer >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_SapiPlayerFunc_hasVoice(PyObject* self)
{
    ::SapiPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SapiPlayer*)Shiboken::Conversions::cppPointer(SbkpysapiTypes[SBK_SAPIPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // hasVoice()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::SapiPlayer*>(cppSelf)->hasVoice();
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

static PyObject* Sbk_SapiPlayerFunc_isValid(PyObject* self)
{
    ::SapiPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SapiPlayer*)Shiboken::Conversions::cppPointer(SbkpysapiTypes[SBK_SAPIPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isValid()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::SapiPlayer*>(cppSelf)->isValid();
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

static PyObject* Sbk_SapiPlayerFunc_purge(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::SapiPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SapiPlayer*)Shiboken::Conversions::cppPointer(SbkpysapiTypes[SBK_SAPIPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 1) {
        PyErr_SetString(PyExc_TypeError, "pysapi.SapiPlayer.purge(): too many arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|O:purge", &(pyArgs[0])))
        return 0;


    // Overloaded function decisor
    // 0: purge(bool)const
    if (numArgs == 0) {
        overloadId = 0; // purge(bool)const
    } else if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[0])))) {
        overloadId = 0; // purge(bool)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_SapiPlayerFunc_purge_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "async");
            if (value && pyArgs[0]) {
                PyErr_SetString(PyExc_TypeError, "pysapi.SapiPlayer.purge(): got multiple values for keyword argument 'async'.");
                return 0;
            } else if (value) {
                pyArgs[0] = value;
                if (!(pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[0]))))
                    goto Sbk_SapiPlayerFunc_purge_TypeError;
            }
        }
        bool cppArg0 = false;
        if (pythonToCpp[0]) pythonToCpp[0](pyArgs[0], &cppArg0);

        if (!PyErr_Occurred()) {
            // purge(bool)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::SapiPlayer*>(cppSelf)->purge(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_SapiPlayerFunc_purge_TypeError:
        const char* overloads[] = {"bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pysapi.SapiPlayer.purge", overloads);
        return 0;
}

static PyObject* Sbk_SapiPlayerFunc_setVoice(PyObject* self, PyObject* pyArg)
{
    ::SapiPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SapiPlayer*)Shiboken::Conversions::cppPointer(SbkpysapiTypes[SBK_SAPIPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setVoice(std::wstring)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpysapiTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // setVoice(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_SapiPlayerFunc_setVoice_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setVoice(std::wstring)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->setVoice(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_SapiPlayerFunc_setVoice_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pysapi.SapiPlayer.setVoice", overloads);
        return 0;
}

static PyObject* Sbk_SapiPlayerFunc_speak(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::SapiPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SapiPlayer*)Shiboken::Conversions::cppPointer(SbkpysapiTypes[SBK_SAPIPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pysapi.SapiPlayer.speak(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pysapi.SapiPlayer.speak(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:speak", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: speak(std::wstring,bool)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkpysapiTypeConverters[SBK_STD_WSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // speak(std::wstring,bool)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1])))) {
            overloadId = 0; // speak(std::wstring,bool)const
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_SapiPlayerFunc_speak_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "async");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pysapi.SapiPlayer.speak(): got multiple values for keyword argument 'async'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1]))))
                    goto Sbk_SapiPlayerFunc_speak_TypeError;
            }
        }
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        bool cppArg1 = false;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // speak(std::wstring,bool)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::SapiPlayer*>(cppSelf)->speak(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_SapiPlayerFunc_speak_TypeError:
        const char* overloads[] = {"std::wstring, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pysapi.SapiPlayer.speak", overloads);
        return 0;
}

static PyObject* Sbk_SapiPlayerFunc_voice(PyObject* self)
{
    ::SapiPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SapiPlayer*)Shiboken::Conversions::cppPointer(SbkpysapiTypes[SBK_SAPIPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // voice()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = const_cast<const ::SapiPlayer*>(cppSelf)->voice();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpysapiTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyMethodDef Sbk_SapiPlayer_methods[] = {
    {"hasVoice", (PyCFunction)Sbk_SapiPlayerFunc_hasVoice, METH_NOARGS},
    {"isValid", (PyCFunction)Sbk_SapiPlayerFunc_isValid, METH_NOARGS},
    {"purge", (PyCFunction)Sbk_SapiPlayerFunc_purge, METH_VARARGS|METH_KEYWORDS},
    {"setVoice", (PyCFunction)Sbk_SapiPlayerFunc_setVoice, METH_O},
    {"speak", (PyCFunction)Sbk_SapiPlayerFunc_speak, METH_VARARGS|METH_KEYWORDS},
    {"voice", (PyCFunction)Sbk_SapiPlayerFunc_voice, METH_NOARGS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_SapiPlayer_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_SapiPlayer_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_SapiPlayer_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pysapi.SapiPlayer",
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
    /*tp_traverse*/         Sbk_SapiPlayer_traverse,
    /*tp_clear*/            Sbk_SapiPlayer_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_SapiPlayer_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_SapiPlayer_Init,
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
static void SapiPlayer_PythonToCpp_SapiPlayer_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_SapiPlayer_Type, pyIn, cppOut);
}
static PythonToCppFunc is_SapiPlayer_PythonToCpp_SapiPlayer_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_SapiPlayer_Type))
        return SapiPlayer_PythonToCpp_SapiPlayer_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* SapiPlayer_PTR_CppToPython_SapiPlayer(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::SapiPlayer*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_SapiPlayer_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_SapiPlayer(PyObject* module)
{
    SbkpysapiTypes[SBK_SAPIPLAYER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_SapiPlayer_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "SapiPlayer", "SapiPlayer*",
        &Sbk_SapiPlayer_Type, &Shiboken::callCppDestructor< ::SapiPlayer >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_SapiPlayer_Type,
        SapiPlayer_PythonToCpp_SapiPlayer_PTR,
        is_SapiPlayer_PythonToCpp_SapiPlayer_PTR_Convertible,
        SapiPlayer_PTR_CppToPython_SapiPlayer);

    Shiboken::Conversions::registerConverterName(converter, "SapiPlayer");
    Shiboken::Conversions::registerConverterName(converter, "SapiPlayer*");
    Shiboken::Conversions::registerConverterName(converter, "SapiPlayer&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::SapiPlayer).name());



}
