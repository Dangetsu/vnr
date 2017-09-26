
// default includes
#include <shiboken.h>
#include <pysidesignal.h>
#include <pysideproperty.h>
#include <pyside.h>
#include <destroylistener.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pyhanja_python.h"

#include "qhanjahangulconverter_wrapper.h"

// Extra includes
#include <qhanjahangulconv.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_QHanjaHangulConverter_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::QHanjaHangulConverter >()))
        return -1;

    ::QHanjaHangulConverter* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // QHanjaHangulConverter()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::QHanjaHangulConverter();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::QHanjaHangulConverter >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_QHanjaHangulConverterFunc_addCharacterDictionary(PyObject* self, PyObject* pyArg)
{
    ::QHanjaHangulConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::QHanjaHangulConverter*)Shiboken::Conversions::cppPointer(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: addCharacterDictionary(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // addCharacterDictionary(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_QHanjaHangulConverterFunc_addCharacterDictionary_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // addCharacterDictionary(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->addCharacterDictionary(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_QHanjaHangulConverterFunc_addCharacterDictionary_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanja.QHanjaHangulConverter.addCharacterDictionary", overloads);
        return 0;
}

static PyObject* Sbk_QHanjaHangulConverterFunc_addWordDictionary(PyObject* self, PyObject* pyArg)
{
    ::QHanjaHangulConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::QHanjaHangulConverter*)Shiboken::Conversions::cppPointer(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: addWordDictionary(QString)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // addWordDictionary(QString)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_QHanjaHangulConverterFunc_addWordDictionary_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // addWordDictionary(QString)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->addWordDictionary(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_QHanjaHangulConverterFunc_addWordDictionary_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanja.QHanjaHangulConverter.addWordDictionary", overloads);
        return 0;
}

static PyObject* Sbk_QHanjaHangulConverterFunc_clear(PyObject* self)
{
    ::QHanjaHangulConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::QHanjaHangulConverter*)Shiboken::Conversions::cppPointer(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX], (SbkObject*)self));

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

static PyObject* Sbk_QHanjaHangulConverterFunc_convert(PyObject* self, PyObject* pyArg)
{
    ::QHanjaHangulConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::QHanjaHangulConverter*)Shiboken::Conversions::cppPointer(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: convert(QString)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // convert(QString)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_QHanjaHangulConverterFunc_convert_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // convert(QString)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::QHanjaHangulConverter*>(cppSelf)->convert(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_QHanjaHangulConverterFunc_convert_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanja.QHanjaHangulConverter.convert", overloads);
        return 0;
}

static PyObject* Sbk_QHanjaHangulConverterFunc_isEmpty(PyObject* self)
{
    ::QHanjaHangulConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::QHanjaHangulConverter*)Shiboken::Conversions::cppPointer(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isEmpty()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::QHanjaHangulConverter*>(cppSelf)->isEmpty();
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

static PyObject* Sbk_QHanjaHangulConverterFunc_lookup(PyObject* self, PyObject* pyArg)
{
    ::QHanjaHangulConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::QHanjaHangulConverter*)Shiboken::Conversions::cppPointer(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: lookup(QString)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], (pyArg)))) {
        overloadId = 0; // lookup(QString)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_QHanjaHangulConverterFunc_lookup_TypeError;

    // Call function/method
    {
        ::QString cppArg0 = ::QString();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // lookup(QString)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            QString cppResult = const_cast<const ::QHanjaHangulConverter*>(cppSelf)->lookup(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_QHanjaHangulConverterFunc_lookup_TypeError:
        const char* overloads[] = {"unicode", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanja.QHanjaHangulConverter.lookup", overloads);
        return 0;
}

static PyObject* Sbk_QHanjaHangulConverterFunc_lookupCharacter(PyObject* self, PyObject* pyArg)
{
    ::QHanjaHangulConverter* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::QHanjaHangulConverter*)Shiboken::Conversions::cppPointer(SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: lookupCharacter(int)const
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArg)))) {
        overloadId = 0; // lookupCharacter(int)const
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_QHanjaHangulConverterFunc_lookupCharacter_TypeError;

    // Call function/method
    {
        int cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // lookupCharacter(int)const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::QHanjaHangulConverter*>(cppSelf)->lookupCharacter(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<int>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_QHanjaHangulConverterFunc_lookupCharacter_TypeError:
        const char* overloads[] = {"int", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pyhanja.QHanjaHangulConverter.lookupCharacter", overloads);
        return 0;
}

static PyMethodDef Sbk_QHanjaHangulConverter_methods[] = {
    {"addCharacterDictionary", (PyCFunction)Sbk_QHanjaHangulConverterFunc_addCharacterDictionary, METH_O},
    {"addWordDictionary", (PyCFunction)Sbk_QHanjaHangulConverterFunc_addWordDictionary, METH_O},
    {"clear", (PyCFunction)Sbk_QHanjaHangulConverterFunc_clear, METH_NOARGS},
    {"convert", (PyCFunction)Sbk_QHanjaHangulConverterFunc_convert, METH_O},
    {"isEmpty", (PyCFunction)Sbk_QHanjaHangulConverterFunc_isEmpty, METH_NOARGS},
    {"lookup", (PyCFunction)Sbk_QHanjaHangulConverterFunc_lookup, METH_O},
    {"lookupCharacter", (PyCFunction)Sbk_QHanjaHangulConverterFunc_lookupCharacter, METH_O},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_QHanjaHangulConverter_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_QHanjaHangulConverter_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_QHanjaHangulConverter_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pyhanja.QHanjaHangulConverter",
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
    /*tp_traverse*/         Sbk_QHanjaHangulConverter_traverse,
    /*tp_clear*/            Sbk_QHanjaHangulConverter_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_QHanjaHangulConverter_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_QHanjaHangulConverter_Init,
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
static void QHanjaHangulConverter_PythonToCpp_QHanjaHangulConverter_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_QHanjaHangulConverter_Type, pyIn, cppOut);
}
static PythonToCppFunc is_QHanjaHangulConverter_PythonToCpp_QHanjaHangulConverter_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_QHanjaHangulConverter_Type))
        return QHanjaHangulConverter_PythonToCpp_QHanjaHangulConverter_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* QHanjaHangulConverter_PTR_CppToPython_QHanjaHangulConverter(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::QHanjaHangulConverter*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_QHanjaHangulConverter_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_QHanjaHangulConverter(PyObject* module)
{
    SbkpyhanjaTypes[SBK_QHANJAHANGULCONVERTER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_QHanjaHangulConverter_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "QHanjaHangulConverter", "QHanjaHangulConverter*",
        &Sbk_QHanjaHangulConverter_Type, &Shiboken::callCppDestructor< ::QHanjaHangulConverter >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_QHanjaHangulConverter_Type,
        QHanjaHangulConverter_PythonToCpp_QHanjaHangulConverter_PTR,
        is_QHanjaHangulConverter_PythonToCpp_QHanjaHangulConverter_PTR_Convertible,
        QHanjaHangulConverter_PTR_CppToPython_QHanjaHangulConverter);

    Shiboken::Conversions::registerConverterName(converter, "QHanjaHangulConverter");
    Shiboken::Conversions::registerConverterName(converter, "QHanjaHangulConverter*");
    Shiboken::Conversions::registerConverterName(converter, "QHanjaHangulConverter&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::QHanjaHangulConverter).name());



}
