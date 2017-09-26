
// default includes
#include <shiboken.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pycc_python.h"

#include "simplechineseconverter_wrapper.h"

// Extra includes
#include <simplecc.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_SimpleChineseConverter_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::SimpleChineseConverter >()))
        return -1;

    ::SimpleChineseConverter* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // SimpleChineseConverter()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::SimpleChineseConverter();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::SimpleChineseConverter >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_SimpleChineseConverterFunc_addFile(PyObject* self, PyObject* args, PyObject* kwds)
{
    ::SimpleChineseConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SimpleChineseConverter*)Shiboken::Conversions::cppPointer(SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp[] = { 0, 0 };
    SBK_UNUSED(pythonToCpp)
    int numNamedArgs = (kwds ? PyDict_Size(kwds) : 0);
    int numArgs = PyTuple_GET_SIZE(args);
    PyObject* pyArgs[] = {0, 0};

    // invalid argument lengths
    if (numArgs + numNamedArgs > 2) {
        PyErr_SetString(PyExc_TypeError, "pycc.SimpleChineseConverter.addFile(): too many arguments");
        return 0;
    } else if (numArgs < 1) {
        PyErr_SetString(PyExc_TypeError, "pycc.SimpleChineseConverter.addFile(): not enough arguments");
        return 0;
    }

    if (!PyArg_ParseTuple(args, "|OO:addFile", &(pyArgs[0]), &(pyArgs[1])))
        return 0;


    // Overloaded function decisor
    // 0: addFile(std::wstring,bool)
    if ((pythonToCpp[0] = Shiboken::Conversions::isPythonToCppConvertible(SbkpyccTypeConverters[SBK_STD_WSTRING_IDX], (pyArgs[0])))) {
        if (numArgs == 1) {
            overloadId = 0; // addFile(std::wstring,bool)
        } else if ((pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1])))) {
            overloadId = 0; // addFile(std::wstring,bool)
        }
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_SimpleChineseConverterFunc_addFile_TypeError;

    // Call function/method
    {
        if (kwds) {
            PyObject* value = PyDict_GetItemString(kwds, "reverse");
            if (value && pyArgs[1]) {
                PyErr_SetString(PyExc_TypeError, "pycc.SimpleChineseConverter.addFile(): got multiple values for keyword argument 'reverse'.");
                return 0;
            } else if (value) {
                pyArgs[1] = value;
                if (!(pythonToCpp[1] = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), (pyArgs[1]))))
                    goto Sbk_SimpleChineseConverterFunc_addFile_TypeError;
            }
        }
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp[0](pyArgs[0], &cppArg0);
        bool cppArg1 = false;
        if (pythonToCpp[1]) pythonToCpp[1](pyArgs[1], &cppArg1);

        if (!PyErr_Occurred()) {
            // addFile(std::wstring,bool)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->addFile(cppArg0, cppArg1);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_SimpleChineseConverterFunc_addFile_TypeError:
        const char* overloads[] = {"std::wstring, bool = false", 0};
        Shiboken::setErrorAboutWrongArguments(args, "pycc.SimpleChineseConverter.addFile", overloads);
        return 0;
}

static PyObject* Sbk_SimpleChineseConverterFunc_clear(PyObject* self)
{
    ::SimpleChineseConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SimpleChineseConverter*)Shiboken::Conversions::cppPointer(SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX], (SbkObject*)self));

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

static PyObject* Sbk_SimpleChineseConverterFunc_convert(PyObject* self, PyObject* pyArg)
{
    ::SimpleChineseConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SimpleChineseConverter*)Shiboken::Conversions::cppPointer(SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: convert(std::wstring)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpyccTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // convert(std::wstring)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_SimpleChineseConverterFunc_convert_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // convert(std::wstring)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = const_cast<const ::SimpleChineseConverter*>(cppSelf)->convert(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpyccTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_SimpleChineseConverterFunc_convert_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pycc.SimpleChineseConverter.convert", overloads);
        return 0;
}

static PyObject* Sbk_SimpleChineseConverterFunc_isEmpty(PyObject* self)
{
    ::SimpleChineseConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SimpleChineseConverter*)Shiboken::Conversions::cppPointer(SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isEmpty()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::SimpleChineseConverter*>(cppSelf)->isEmpty();
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

static PyObject* Sbk_SimpleChineseConverterFunc_needsConvert(PyObject* self, PyObject* pyArg)
{
    ::SimpleChineseConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SimpleChineseConverter*)Shiboken::Conversions::cppPointer(SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: needsConvert(std::wstring)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpyccTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // needsConvert(std::wstring)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_SimpleChineseConverterFunc_needsConvert_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // needsConvert(std::wstring)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::SimpleChineseConverter*>(cppSelf)->needsConvert(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_SimpleChineseConverterFunc_needsConvert_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pycc.SimpleChineseConverter.needsConvert", overloads);
        return 0;
}

static PyObject* Sbk_SimpleChineseConverterFunc_size(PyObject* self)
{
    ::SimpleChineseConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::SimpleChineseConverter*)Shiboken::Conversions::cppPointer(SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // size()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::SimpleChineseConverter*>(cppSelf)->size();
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

static PyMethodDef Sbk_SimpleChineseConverter_methods[] = {
    {"addFile", (PyCFunction)Sbk_SimpleChineseConverterFunc_addFile, METH_VARARGS|METH_KEYWORDS},
    {"clear", (PyCFunction)Sbk_SimpleChineseConverterFunc_clear, METH_NOARGS},
    {"convert", (PyCFunction)Sbk_SimpleChineseConverterFunc_convert, METH_O},
    {"isEmpty", (PyCFunction)Sbk_SimpleChineseConverterFunc_isEmpty, METH_NOARGS},
    {"needsConvert", (PyCFunction)Sbk_SimpleChineseConverterFunc_needsConvert, METH_O},
    {"size", (PyCFunction)Sbk_SimpleChineseConverterFunc_size, METH_NOARGS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_SimpleChineseConverter_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_SimpleChineseConverter_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_SimpleChineseConverter_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pycc.SimpleChineseConverter",
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
    /*tp_traverse*/         Sbk_SimpleChineseConverter_traverse,
    /*tp_clear*/            Sbk_SimpleChineseConverter_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_SimpleChineseConverter_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_SimpleChineseConverter_Init,
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
static void SimpleChineseConverter_PythonToCpp_SimpleChineseConverter_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_SimpleChineseConverter_Type, pyIn, cppOut);
}
static PythonToCppFunc is_SimpleChineseConverter_PythonToCpp_SimpleChineseConverter_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_SimpleChineseConverter_Type))
        return SimpleChineseConverter_PythonToCpp_SimpleChineseConverter_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* SimpleChineseConverter_PTR_CppToPython_SimpleChineseConverter(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::SimpleChineseConverter*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_SimpleChineseConverter_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_SimpleChineseConverter(PyObject* module)
{
    SbkpyccTypes[SBK_SIMPLECHINESECONVERTER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_SimpleChineseConverter_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "SimpleChineseConverter", "SimpleChineseConverter*",
        &Sbk_SimpleChineseConverter_Type, &Shiboken::callCppDestructor< ::SimpleChineseConverter >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_SimpleChineseConverter_Type,
        SimpleChineseConverter_PythonToCpp_SimpleChineseConverter_PTR,
        is_SimpleChineseConverter_PythonToCpp_SimpleChineseConverter_PTR_Convertible,
        SimpleChineseConverter_PTR_CppToPython_SimpleChineseConverter);

    Shiboken::Conversions::registerConverterName(converter, "SimpleChineseConverter");
    Shiboken::Conversions::registerConverterName(converter, "SimpleChineseConverter*");
    Shiboken::Conversions::registerConverterName(converter, "SimpleChineseConverter&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::SimpleChineseConverter).name());



}
