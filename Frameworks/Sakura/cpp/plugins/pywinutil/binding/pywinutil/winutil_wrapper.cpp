
// default includes
#include <shiboken.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pywinutil_python.h"

#include "winutil_wrapper.h"

// Extra includes



// Target ---------------------------------------------------------

extern "C" {
static PyObject* Sbk_WinUtilFunc_resolveLink(PyObject* self, PyObject* pyArg)
{
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: resolveLink(std::wstring)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpywinutilTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // resolveLink(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_WinUtilFunc_resolveLink_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // resolveLink(std::wstring)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = ::WinUtil::resolveLink(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpywinutilTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_WinUtilFunc_resolveLink_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pywinutil.WinUtil.resolveLink", overloads);
        return 0;
}

static PyObject* Sbk_WinUtilFunc_toLongPath(PyObject* self, PyObject* pyArg)
{
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: toLongPath(std::wstring)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpywinutilTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // toLongPath(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_WinUtilFunc_toLongPath_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // toLongPath(std::wstring)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = ::WinUtil::toLongPath(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpywinutilTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_WinUtilFunc_toLongPath_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pywinutil.WinUtil.toLongPath", overloads);
        return 0;
}

static PyObject* Sbk_WinUtilFunc_toShortPath(PyObject* self, PyObject* pyArg)
{
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: toShortPath(std::wstring)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpywinutilTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // toShortPath(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_WinUtilFunc_toShortPath_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // toShortPath(std::wstring)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = ::WinUtil::toShortPath(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpywinutilTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_WinUtilFunc_toShortPath_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pywinutil.WinUtil.toShortPath", overloads);
        return 0;
}

static PyMethodDef Sbk_WinUtil_methods[] = {
    {"resolveLink", (PyCFunction)Sbk_WinUtilFunc_resolveLink, METH_O|METH_STATIC},
    {"toLongPath", (PyCFunction)Sbk_WinUtilFunc_toLongPath, METH_O|METH_STATIC},
    {"toShortPath", (PyCFunction)Sbk_WinUtilFunc_toShortPath, METH_O|METH_STATIC},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_WinUtil_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_WinUtil_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_WinUtil_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pywinutil.WinUtil",
    /*tp_basicsize*/        sizeof(SbkObject),
    /*tp_itemsize*/         0,
    /*tp_dealloc*/          0,
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
    /*tp_flags*/            Py_TPFLAGS_DEFAULT|Py_TPFLAGS_CHECKTYPES|Py_TPFLAGS_HAVE_GC,
    /*tp_doc*/              0,
    /*tp_traverse*/         Sbk_WinUtil_traverse,
    /*tp_clear*/            Sbk_WinUtil_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_WinUtil_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             0,
    /*tp_alloc*/            0,
    /*tp_new*/              0,
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

void init_WinUtil(PyObject* module)
{
    SbkpywinutilTypes[SBK_WINUTIL_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_WinUtil_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "WinUtil", "WinUtil",
        &Sbk_WinUtil_Type)) {
        return;
    }



}
