
// default includes
#include <shiboken.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pytrscript_python.h"

#include "translationscriptperformer_wrapper.h"

// Extra includes
#include <trscript.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_TranslationScriptPerformer_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::TranslationScriptPerformer >()))
        return -1;

    ::TranslationScriptPerformer* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // TranslationScriptPerformer()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::TranslationScriptPerformer();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::TranslationScriptPerformer >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_TranslationScriptPerformerFunc_clear(PyObject* self)
{
    ::TranslationScriptPerformer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationScriptPerformer*)Shiboken::Conversions::cppPointer(SbkpytrscriptTypes[SBK_TRANSLATIONSCRIPTPERFORMER_IDX], (SbkObject*)self));

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

static PyObject* Sbk_TranslationScriptPerformerFunc_isEmpty(PyObject* self)
{
    ::TranslationScriptPerformer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationScriptPerformer*)Shiboken::Conversions::cppPointer(SbkpytrscriptTypes[SBK_TRANSLATIONSCRIPTPERFORMER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isEmpty()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TranslationScriptPerformer*>(cppSelf)->isEmpty();
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

static PyObject* Sbk_TranslationScriptPerformerFunc_loadScript(PyObject* self, PyObject* pyArg)
{
    ::TranslationScriptPerformer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationScriptPerformer*)Shiboken::Conversions::cppPointer(SbkpytrscriptTypes[SBK_TRANSLATIONSCRIPTPERFORMER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: loadScript(std::wstring)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpytrscriptTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // loadScript(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TranslationScriptPerformerFunc_loadScript_TypeError;

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

    Sbk_TranslationScriptPerformerFunc_loadScript_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytrscript.TranslationScriptPerformer.loadScript", overloads);
        return 0;
}

static PyObject* Sbk_TranslationScriptPerformerFunc_size(PyObject* self)
{
    ::TranslationScriptPerformer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationScriptPerformer*)Shiboken::Conversions::cppPointer(SbkpytrscriptTypes[SBK_TRANSLATIONSCRIPTPERFORMER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // size()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::TranslationScriptPerformer*>(cppSelf)->size();
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

static PyObject* Sbk_TranslationScriptPerformerFunc_transform(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::TranslationScriptPerformer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TranslationScriptPerformer*)Shiboken::Conversions::cppPointer(SbkpytrscriptTypes[SBK_TRANSLATIONSCRIPTPERFORMER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 3) {
        PyErr_SetString(PyExc_TypeError, "pytrscript.TranslationScriptPerformer.transform(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pytrscript.TranslationScriptPerformer.transform(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OOO:transform", &(pyArgs[0]), &(pyArgs[1]), &(pyArgs[2])))
        return 0;


    // Overloaded function decisor
    // 0: transform(std::wstring,int,bool)const
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkpytrscriptTypeConverters[SBK_STD_WSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // transform(std::wstring,int,bool)const
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1])))) {
            if (numArgs == 2) {
                overloadId = 0; // transform(std::wstring,int,bool)const
            } else if ((pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[2])))) {
                overloadId = 0; // transform(std::wstring,int,bool)const
            }
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TranslationScriptPerformerFunc_transform_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "category");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pytrscript.TranslationScriptPerformer.transform(): got multiple values for keyword argument 'category'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArgs[1]))))
                    goto Sbk_TranslationScriptPerformerFunc_transform_TypeError;
            }
            value = PyDict_GetItemString(kwds, "mark");
            if (value && pyArgs[2]) {
                PyErr_SetString(PyExc_TypeError, "pytrscript.TranslationScriptPerformer.transform(): got multiple values for keyword argument 'mark'.");
                return 0;
            } else if (value) {
                pyArgs[2] = value;
                if (!(pythonToCpp[2] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[2]))))
                    goto Sbk_TranslationScriptPerformerFunc_transform_TypeError;
            }
        }
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        int cppArg1 = -1;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);
        bool cppArg2 = false;
        if (pythonToCpp[2]) pythonToCpp[2](pyArgs[2], &cppArg2);

        if (!PyErr_Occurred()) {
            // transform(std::wstring,int,bool)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = const_cast<const ::TranslationScriptPerformer*>(cppSelf)->transform(cppArg0, cppArg1, cppArg2);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpytrscriptTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TranslationScriptPerformerFunc_transform_TypeError:
        const char* overloads[] = {"std::wstring, int = -1, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pytrscript.TranslationScriptPerformer.transform", overloads);
        return 0;
}

static PyMethodDef Sbk_TranslationScriptPerformer_methods[] = {
    {"clear", (PyCFunction)Sbk_TranslationScriptPerformerFunc_clear, METH_NOARGS},
    {"isEmpty", (PyCFunction)Sbk_TranslationScriptPerformerFunc_isEmpty, METH_NOARGS},
    {"loadScript", (PyCFunction)Sbk_TranslationScriptPerformerFunc_loadScript, METH_O},
    {"size", (PyCFunction)Sbk_TranslationScriptPerformerFunc_size, METH_NOARGS},
    {"transform", (PyCFunction)Sbk_TranslationScriptPerformerFunc_transform, METH_VARARGS|METH_KEYWORDS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_TranslationScriptPerformer_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_TranslationScriptPerformer_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_TranslationScriptPerformer_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pytrscript.TranslationScriptPerformer",
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
    /*tp_traverse*/         Sbk_TranslationScriptPerformer_traverse,
    /*tp_clear*/            Sbk_TranslationScriptPerformer_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_TranslationScriptPerformer_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_TranslationScriptPerformer_Init,
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
static void TranslationScriptPerformer_PythonToCpp_TranslationScriptPerformer_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_TranslationScriptPerformer_Type, pyIn, cppOut);
}
static PythonToCppFunc is_TranslationScriptPerformer_PythonToCpp_TranslationScriptPerformer_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_TranslationScriptPerformer_Type))
        return TranslationScriptPerformer_PythonToCpp_TranslationScriptPerformer_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* TranslationScriptPerformer_PTR_CppToPython_TranslationScriptPerformer(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::TranslationScriptPerformer*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_TranslationScriptPerformer_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_TranslationScriptPerformer(PyObject* module)
{
    SbkpytrscriptTypes[SBK_TRANSLATIONSCRIPTPERFORMER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_TranslationScriptPerformer_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "TranslationScriptPerformer", "TranslationScriptPerformer*",
        &Sbk_TranslationScriptPerformer_Type, &Shiboken::callCppDestructor< ::TranslationScriptPerformer >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_TranslationScriptPerformer_Type,
        TranslationScriptPerformer_PythonToCpp_TranslationScriptPerformer_PTR,
        is_TranslationScriptPerformer_PythonToCpp_TranslationScriptPerformer_PTR_Convertible,
        TranslationScriptPerformer_PTR_CppToPython_TranslationScriptPerformer);

    Shiboken::Conversions::registerConverterName(converter, "TranslationScriptPerformer");
    Shiboken::Conversions::registerConverterName(converter, "TranslationScriptPerformer*");
    Shiboken::Conversions::registerConverterName(converter, "TranslationScriptPerformer&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::TranslationScriptPerformer).name());



}
