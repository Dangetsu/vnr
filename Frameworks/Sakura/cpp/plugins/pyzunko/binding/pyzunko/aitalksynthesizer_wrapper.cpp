
// default includes
#include <shiboken.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pyzunko_python.h"

#include "aitalksynthesizer_wrapper.h"

// Extra includes
#include <aitalked.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_AITalkSynthesizer_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::AITalkSynthesizer >()))
        return -1;

    ::AITalkSynthesizer* cptr = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pyzunko.AITalkSynthesizer(): too many arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "|OO:AITalkSynthesizer", &(pyArgs[0]), &(pyArgs[1])))
        return -1;


    // Overloaded function decisor
    // 0: AITalkSynthesizer(float,uint)
    if (numArgs == 0) {
        overloadId = 0; // AITalkSynthesizer(float,uint)
    } else if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<float>(), (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // AITalkSynthesizer(float,uint)
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<unsigned int>(), (pyArgs[1])))) {
            overloadId = 0; // AITalkSynthesizer(float,uint)
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_AITalkSynthesizer_Init_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "volume");
            if (value && pyArgs[0]) {
                PyErr_SetString(PyExc_TypeError, "pyzunko.AITalkSynthesizer(): got multiple values for keyword argument 'volume'.");
                return -1;
            } else if (value) {
                pyArgs[0] = value;
                if (!(pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<float>(), (pyArgs[0]))))
                    goto Sbk_AITalkSynthesizer_Init_TypeError;
            }
            value = PyDict_GetItemString(kwds, "audioBufferSize");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pyzunko.AITalkSynthesizer(): got multiple values for keyword argument 'audioBufferSize'.");
                return -1;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<unsigned int>(), (pyArgs[1]))))
                    goto Sbk_AITalkSynthesizer_Init_TypeError;
            }
        }
        float cppArg0 = 1;
        if (pythonToCpp[0]) pythonToCpp[0](pyArgs[0], &cppArg0);
        unsigned int cppArg1 = 0;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // AITalkSynthesizer(float,uint)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::AITalkSynthesizer(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::AITalkSynthesizer >(), cptr)) {
        delete cptr;
        return -1;
    }
    if (!cptr) goto Sbk_AITalkSynthesizer_Init_TypeError;

    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;

    Sbk_AITalkSynthesizer_Init_TypeError:
        const char* overloads[] = {"float = 1, unsigned int = 0", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pyzunko.AITalkSynthesizer", overloads);
        return -1;
}

static PyObject* Sbk_AITalkSynthesizerFunc_init(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 1) {
        PyErr_SetString(PyExc_TypeError, "pyzunko.AITalkSynthesizer.init(): too many arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|O:init", &(pyArgs[0])))
        return 0;


    // Overloaded function decisor
    // 0: init(std::wstring)
    if (numArgs == 0) {
        overloadId = 0; // init(std::wstring)
    } else if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkpyzunkoTypeConverters[SBK_STD_WSTRING_IDX], (pyArgs[0])))) {
        overloadId = 0; // init(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_AITalkSynthesizerFunc_init_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "path");
            if (value && pyArgs[0]) {
                PyErr_SetString(PyExc_TypeError, "pyzunko.AITalkSynthesizer.init(): got multiple values for keyword argument 'path'.");
                return 0;
            } else if (value) {
                pyArgs[0] = value;
                if (!(pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkpyzunkoTypeConverters[SBK_STD_WSTRING_IDX], (pyArgs[0]))))
                    goto Sbk_AITalkSynthesizerFunc_init_TypeError;
            }
        }
        ::std::wstring cppArg0 = L"aitalked.dll";
        if (pythonToCpp[0]) pythonToCpp[0](pyArgs[0], &cppArg0);

        if (!PyErr_Occurred()) {
            // init(std::wstring)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->init(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_AITalkSynthesizerFunc_init_TypeError:
        const char* overloads[] = {"std::wstring = L\"aitalked.dll\"", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pyzunko.AITalkSynthesizer.init", overloads);
        return 0;
}

static PyObject* Sbk_AITalkSynthesizerFunc_isPlaying(PyObject* self)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isPlaying()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::AITalkSynthesizer*>(cppSelf)->isPlaying();
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

static PyObject* Sbk_AITalkSynthesizerFunc_isValid(PyObject* self)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isValid()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::AITalkSynthesizer*>(cppSelf)->isValid();
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

static PyObject* Sbk_AITalkSynthesizerFunc_pause(PyObject* self)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // pause()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->pause();
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

static PyObject* Sbk_AITalkSynthesizerFunc_resume(PyObject* self)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // resume()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->resume();
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

static PyObject* Sbk_AITalkSynthesizerFunc_setVolume(PyObject* self, PyObject* pyArg)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setVolume(float)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<float>(), (pyArg)))) {
        overloadId = 0; // setVolume(float)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_AITalkSynthesizerFunc_setVolume_TypeError;

    // Call function/method
    {
        float cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setVolume(float)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setVolume(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_AITalkSynthesizerFunc_setVolume_TypeError:
        const char* overloads[] = {"float", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyzunko.AITalkSynthesizer.setVolume", overloads);
        return 0;
}

static PyObject* Sbk_AITalkSynthesizerFunc_speak(PyObject* self, PyObject* pyArg)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: speak(const char*)
    if (Shiboken::String::check(pyArg) && (pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<const char*>(), (pyArg)))) {
        overloadId = 0; // speak(const char*)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_AITalkSynthesizerFunc_speak_TypeError;

    // Call function/method
    {
        const char* cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // speak(const char*)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->speak(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_AITalkSynthesizerFunc_speak_TypeError:
        const char* overloads[] = {"" SBK_STR_NAME "", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyzunko.AITalkSynthesizer.speak", overloads);
        return 0;
}

static PyObject* Sbk_AITalkSynthesizerFunc_stop(PyObject* self)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));

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

static PyObject* Sbk_AITalkSynthesizerFunc_volume(PyObject* self)
{
    ::AITalkSynthesizer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::AITalkSynthesizer*)Shiboken::Conversions::cppPointer(SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // volume()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            float cppResult = const_cast<const ::AITalkSynthesizer*>(cppSelf)->volume();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<float>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyMethodDef Sbk_AITalkSynthesizer_methods[] = {
    {"init", (PyCFunction)Sbk_AITalkSynthesizerFunc_init, METH_VARARGS|METH_KEYWORDS},
    {"isPlaying", (PyCFunction)Sbk_AITalkSynthesizerFunc_isPlaying, METH_NOARGS},
    {"isValid", (PyCFunction)Sbk_AITalkSynthesizerFunc_isValid, METH_NOARGS},
    {"pause", (PyCFunction)Sbk_AITalkSynthesizerFunc_pause, METH_NOARGS},
    {"resume", (PyCFunction)Sbk_AITalkSynthesizerFunc_resume, METH_NOARGS},
    {"setVolume", (PyCFunction)Sbk_AITalkSynthesizerFunc_setVolume, METH_O},
    {"speak", (PyCFunction)Sbk_AITalkSynthesizerFunc_speak, METH_O},
    {"stop", (PyCFunction)Sbk_AITalkSynthesizerFunc_stop, METH_NOARGS},
    {"volume", (PyCFunction)Sbk_AITalkSynthesizerFunc_volume, METH_NOARGS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_AITalkSynthesizer_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_AITalkSynthesizer_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_AITalkSynthesizer_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pyzunko.AITalkSynthesizer",
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
    /*tp_traverse*/         Sbk_AITalkSynthesizer_traverse,
    /*tp_clear*/            Sbk_AITalkSynthesizer_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_AITalkSynthesizer_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_AITalkSynthesizer_Init,
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
static void AITalkSynthesizer_PythonToCpp_AITalkSynthesizer_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_AITalkSynthesizer_Type, pyIn, cppOut);
}
static PythonToCppFunc is_AITalkSynthesizer_PythonToCpp_AITalkSynthesizer_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_AITalkSynthesizer_Type))
        return AITalkSynthesizer_PythonToCpp_AITalkSynthesizer_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* AITalkSynthesizer_PTR_CppToPython_AITalkSynthesizer(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::AITalkSynthesizer*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_AITalkSynthesizer_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_AITalkSynthesizer(PyObject* module)
{
    SbkpyzunkoTypes[SBK_AITALKSYNTHESIZER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_AITalkSynthesizer_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "AITalkSynthesizer", "AITalkSynthesizer*",
        &Sbk_AITalkSynthesizer_Type, &Shiboken::callCppDestructor< ::AITalkSynthesizer >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_AITalkSynthesizer_Type,
        AITalkSynthesizer_PythonToCpp_AITalkSynthesizer_PTR,
        is_AITalkSynthesizer_PythonToCpp_AITalkSynthesizer_PTR_Convertible,
        AITalkSynthesizer_PTR_CppToPython_AITalkSynthesizer);

    Shiboken::Conversions::registerConverterName(converter, "AITalkSynthesizer");
    Shiboken::Conversions::registerConverterName(converter, "AITalkSynthesizer*");
    Shiboken::Conversions::registerConverterName(converter, "AITalkSynthesizer&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::AITalkSynthesizer).name());



}
