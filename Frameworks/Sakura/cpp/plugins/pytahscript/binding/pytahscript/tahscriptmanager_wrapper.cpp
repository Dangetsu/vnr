
// default includes
#include <shiboken.h>
#include <pysidesignal.h>
#include <pysideproperty.h>
#include <pyside.h>
#include <destroylistener.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pytahscript_python.h"

#include "tahscriptmanager_wrapper.h"

// Extra includes
#include <tahscript.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_TahScriptManager_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::TahScriptManager >()))
        return -1;

    ::TahScriptManager* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // TahScriptManager()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::TahScriptManager();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::TahScriptManager >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_TahScriptManagerFunc_clear(PyObject* self)
{
    ::TahScriptManager* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TahScriptManager*)Shiboken::Conversions::cppPointer(SbkpytahscriptTypes[SBK_TAHSCRIPTMANAGER_IDX], (SbkObject*)self));

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

static PyObject* Sbk_TahScriptManagerFunc_isEmpty(PyObject* self)
{
    ::TahScriptManager* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TahScriptManager*)Shiboken::Conversions::cppPointer(SbkpytahscriptTypes[SBK_TAHSCRIPTMANAGER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isEmpty()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::TahScriptManager*>(cppSelf)->isEmpty();
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

static PyObject* Sbk_TahScriptManagerFunc_loadFile(PyObject* self, PyObject* pyArg)
{
    ::TahScriptManager* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TahScriptManager*)Shiboken::Conversions::cppPointer(SbkpytahscriptTypes[SBK_TAHSCRIPTMANAGER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: loadFile(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // loadFile(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TahScriptManagerFunc_loadFile_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // loadFile(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->loadFile(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TahScriptManagerFunc_loadFile_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytahscript.TahScriptManager.loadFile", overloads);
        return 0;
}

static PyObject* Sbk_TahScriptManagerFunc_size(PyObject* self)
{
    ::TahScriptManager* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TahScriptManager*)Shiboken::Conversions::cppPointer(SbkpytahscriptTypes[SBK_TAHSCRIPTMANAGER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // size()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::TahScriptManager*>(cppSelf)->size();
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

static PyObject* Sbk_TahScriptManagerFunc_translate(PyObject* self, PyObject* pyArg)
{
    ::TahScriptManager* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::TahScriptManager*)Shiboken::Conversions::cppPointer(SbkpytahscriptTypes[SBK_TAHSCRIPTMANAGER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: translate(QString)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // translate(QString)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_TahScriptManagerFunc_translate_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // translate(QString)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::TahScriptManager*>(cppSelf)->translate(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_TahScriptManagerFunc_translate_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pytahscript.TahScriptManager.translate", overloads);
        return 0;
}

static PyMethodDef Sbk_TahScriptManager_methods[] = {
    {"clear", (PyCFunction)Sbk_TahScriptManagerFunc_clear, METH_NOARGS},
    {"isEmpty", (PyCFunction)Sbk_TahScriptManagerFunc_isEmpty, METH_NOARGS},
    {"loadFile", (PyCFunction)Sbk_TahScriptManagerFunc_loadFile, METH_O},
    {"size", (PyCFunction)Sbk_TahScriptManagerFunc_size, METH_NOARGS},
    {"translate", (PyCFunction)Sbk_TahScriptManagerFunc_translate, METH_O},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_TahScriptManager_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_TahScriptManager_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_TahScriptManager_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pytahscript.TahScriptManager",
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
    /*tp_traverse*/         Sbk_TahScriptManager_traverse,
    /*tp_clear*/            Sbk_TahScriptManager_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_TahScriptManager_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_TahScriptManager_Init,
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
static void TahScriptManager_PythonToCpp_TahScriptManager_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_TahScriptManager_Type, pyIn, cppOut);
}
static PythonToCppFunc is_TahScriptManager_PythonToCpp_TahScriptManager_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_TahScriptManager_Type))
        return TahScriptManager_PythonToCpp_TahScriptManager_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* TahScriptManager_PTR_CppToPython_TahScriptManager(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::TahScriptManager*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_TahScriptManager_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_TahScriptManager(PyObject* module)
{
    SbkpytahscriptTypes[SBK_TAHSCRIPTMANAGER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_TahScriptManager_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "TahScriptManager", "TahScriptManager*",
        &Sbk_TahScriptManager_Type, &Shiboken::callCppDestructor< ::TahScriptManager >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_TahScriptManager_Type,
        TahScriptManager_PythonToCpp_TahScriptManager_PTR,
        is_TahScriptManager_PythonToCpp_TahScriptManager_PTR_Convertible,
        TahScriptManager_PTR_CppToPython_TahScriptManager);

    Shiboken::Conversions::registerConverterName(converter, "TahScriptManager");
    Shiboken::Conversions::registerConverterName(converter, "TahScriptManager*");
    Shiboken::Conversions::registerConverterName(converter, "TahScriptManager&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::TahScriptManager).name());



}
