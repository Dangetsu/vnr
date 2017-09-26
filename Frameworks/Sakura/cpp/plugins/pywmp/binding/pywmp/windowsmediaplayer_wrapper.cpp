
// default includes
#include <shiboken.h>
#include <typeresolver.h>
#include <typeinfo>
#include "pywmp_python.h"

#include "windowsmediaplayer_wrapper.h"

// Extra includes
#include <pywmp.h>



// Target ---------------------------------------------------------

extern "C" {
static int
Sbk_WindowsMediaPlayer_Init(PyObject* self, PyObject* args, PyObject* kwds)
{
    SbkObject* sbkSelf = reinterpret_cast<SbkObject*>(self);
    if (Shiboken::Object::isUserType(self) && !Shiboken::ObjectType::canCallConstructor(self->ob_type, Shiboken::SbkType< ::WindowsMediaPlayer >()))
        return -1;

    ::WindowsMediaPlayer* cptr = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // WindowsMediaPlayer()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cptr = new ::WindowsMediaPlayer();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred() || !Shiboken::Object::setCppPointer(sbkSelf, Shiboken::SbkType< ::WindowsMediaPlayer >(), cptr)) {
        delete cptr;
        return -1;
    }
    Shiboken::Object::setValidCpp(sbkSelf, true);
    Shiboken::BindingManager::instance().registerWrapper(sbkSelf, cptr);


    return 1;
}

static PyObject* Sbk_WindowsMediaPlayerFunc_isValid(PyObject* self)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // isValid()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = const_cast<const ::WindowsMediaPlayer*>(cppSelf)->isValid();
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

static PyObject* Sbk_WindowsMediaPlayerFunc_play(PyObject* self, PyObject* pyArg)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: play(std::wstring)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(SbkpywmpTypeConverters[SBK_STD_WSTRING_IDX], (pyArg)))) {
        overloadId = 0; // play(std::wstring)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_WindowsMediaPlayerFunc_play_TypeError;

    // Call function/method
    {
        ::std::wstring cppArg0 = ::std::wstring();
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // play(std::wstring)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->play(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<bool>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;

    Sbk_WindowsMediaPlayerFunc_play_TypeError:
        const char* overloads[] = {"std::wstring", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pywmp.WindowsMediaPlayer.play", overloads);
        return 0;
}

static PyObject* Sbk_WindowsMediaPlayerFunc_setSpeed(PyObject* self, PyObject* pyArg)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setSpeed(double)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<double>(), (pyArg)))) {
        overloadId = 0; // setSpeed(double)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_WindowsMediaPlayerFunc_setSpeed_TypeError;

    // Call function/method
    {
        double cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setSpeed(double)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setSpeed(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_WindowsMediaPlayerFunc_setSpeed_TypeError:
        const char* overloads[] = {"float", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pywmp.WindowsMediaPlayer.setSpeed", overloads);
        return 0;
}

static PyObject* Sbk_WindowsMediaPlayerFunc_setVolume(PyObject* self, PyObject* pyArg)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    int overloadId = -1;
    PythonToCppFunc pythonToCpp;
    SBK_UNUSED(pythonToCpp)

    // Overloaded function decisor
    // 0: setVolume(int)
    if ((pythonToCpp = Shiboken::Conversions::isPythonToCppConvertible(Shiboken::Conversions::PrimitiveTypeConverter<int>(), (pyArg)))) {
        overloadId = 0; // setVolume(int)
    }

    // Function signature not found.
    if (overloadId == -1) goto Sbk_WindowsMediaPlayerFunc_setVolume_TypeError;

    // Call function/method
    {
        int cppArg0;
        pythonToCpp(pyArg, &cppArg0);

        if (!PyErr_Occurred()) {
            // setVolume(int)
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            cppSelf->setVolume(cppArg0);
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
        }
    }

    if (PyErr_Occurred()) {
        return 0;
    }
    Py_RETURN_NONE;

    Sbk_WindowsMediaPlayerFunc_setVolume_TypeError:
        const char* overloads[] = {"int", 0};
        Shiboken::setErrorAboutWrongArguments(pyArg, "pywmp.WindowsMediaPlayer.setVolume", overloads);
        return 0;
}

static PyObject* Sbk_WindowsMediaPlayerFunc_speed(PyObject* self)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // speed()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            double cppResult = const_cast<const ::WindowsMediaPlayer*>(cppSelf)->speed();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(Shiboken::Conversions::PrimitiveTypeConverter<double>(), &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_WindowsMediaPlayerFunc_stop(PyObject* self)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // stop()
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            bool cppResult = cppSelf->stop();
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

static PyObject* Sbk_WindowsMediaPlayerFunc_version(PyObject* self)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // version()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            std::wstring cppResult = const_cast<const ::WindowsMediaPlayer*>(cppSelf)->version();
            PyEval_RestoreThread(_save); // Py_END_ALLOW_THREADS
            pyResult = Shiboken::Conversions::copyToPython(SbkpywmpTypeConverters[SBK_STD_WSTRING_IDX], &cppResult);
        }
    }

    if (PyErr_Occurred() || !pyResult) {
        Py_XDECREF(pyResult);
        return 0;
    }
    return pyResult;
}

static PyObject* Sbk_WindowsMediaPlayerFunc_volume(PyObject* self)
{
    ::WindowsMediaPlayer* cppSelf = 0;
    SBK_UNUSED(cppSelf)
    if (!Shiboken::Object::isValid(self))
        return 0;
    cppSelf = ((::WindowsMediaPlayer*)Shiboken::Conversions::cppPointer(SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX], (SbkObject*)self));
    PyObject* pyResult = 0;

    // Call function/method
    {

        if (!PyErr_Occurred()) {
            // volume()const
            PyThreadState* _save = PyEval_SaveThread(); // Py_BEGIN_ALLOW_THREADS
            int cppResult = const_cast<const ::WindowsMediaPlayer*>(cppSelf)->volume();
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

static PyMethodDef Sbk_WindowsMediaPlayer_methods[] = {
    {"isValid", (PyCFunction)Sbk_WindowsMediaPlayerFunc_isValid, METH_NOARGS},
    {"play", (PyCFunction)Sbk_WindowsMediaPlayerFunc_play, METH_O},
    {"setSpeed", (PyCFunction)Sbk_WindowsMediaPlayerFunc_setSpeed, METH_O},
    {"setVolume", (PyCFunction)Sbk_WindowsMediaPlayerFunc_setVolume, METH_O},
    {"speed", (PyCFunction)Sbk_WindowsMediaPlayerFunc_speed, METH_NOARGS},
    {"stop", (PyCFunction)Sbk_WindowsMediaPlayerFunc_stop, METH_NOARGS},
    {"version", (PyCFunction)Sbk_WindowsMediaPlayerFunc_version, METH_NOARGS},
    {"volume", (PyCFunction)Sbk_WindowsMediaPlayerFunc_volume, METH_NOARGS},

    {0} // Sentinel
};

} // extern "C"

static int Sbk_WindowsMediaPlayer_traverse(PyObject* self, visitproc visit, void* arg)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_traverse(self, visit, arg);
}
static int Sbk_WindowsMediaPlayer_clear(PyObject* self)
{
    return reinterpret_cast<PyTypeObject*>(&SbkObject_Type)->tp_clear(self);
}
// Class Definition -----------------------------------------------
extern "C" {
static SbkObjectType Sbk_WindowsMediaPlayer_Type = { { {
    PyVarObject_HEAD_INIT(&SbkObjectType_Type, 0)
    /*tp_name*/             "pywmp.WindowsMediaPlayer",
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
    /*tp_traverse*/         Sbk_WindowsMediaPlayer_traverse,
    /*tp_clear*/            Sbk_WindowsMediaPlayer_clear,
    /*tp_richcompare*/      0,
    /*tp_weaklistoffset*/   0,
    /*tp_iter*/             0,
    /*tp_iternext*/         0,
    /*tp_methods*/          Sbk_WindowsMediaPlayer_methods,
    /*tp_members*/          0,
    /*tp_getset*/           0,
    /*tp_base*/             reinterpret_cast<PyTypeObject*>(&SbkObject_Type),
    /*tp_dict*/             0,
    /*tp_descr_get*/        0,
    /*tp_descr_set*/        0,
    /*tp_dictoffset*/       0,
    /*tp_init*/             Sbk_WindowsMediaPlayer_Init,
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
static void WindowsMediaPlayer_PythonToCpp_WindowsMediaPlayer_PTR(PyObject* pyIn, void* cppOut) {
    Shiboken::Conversions::pythonToCppPointer(&Sbk_WindowsMediaPlayer_Type, pyIn, cppOut);
}
static PythonToCppFunc is_WindowsMediaPlayer_PythonToCpp_WindowsMediaPlayer_PTR_Convertible(PyObject* pyIn) {
    if (pyIn == Py_None)
        return Shiboken::Conversions::nonePythonToCppNullPtr;
    if (PyObject_TypeCheck(pyIn, (PyTypeObject*)&Sbk_WindowsMediaPlayer_Type))
        return WindowsMediaPlayer_PythonToCpp_WindowsMediaPlayer_PTR;
    return 0;
}

// C++ to Python pointer conversion - tries to find the Python wrapper for the C++ object (keeps object identity).
static PyObject* WindowsMediaPlayer_PTR_CppToPython_WindowsMediaPlayer(const void* cppIn) {
    PyObject* pyOut = (PyObject*)Shiboken::BindingManager::instance().retrieveWrapper(cppIn);
    if (pyOut) {
        Py_INCREF(pyOut);
        return pyOut;
    }
    const char* typeName = typeid(*((::WindowsMediaPlayer*)cppIn)).name();
    return Shiboken::Object::newObject(&Sbk_WindowsMediaPlayer_Type, const_cast<void*>(cppIn), false, false, typeName);
}

void init_WindowsMediaPlayer(PyObject* module)
{
    SbkpywmpTypes[SBK_WINDOWSMEDIAPLAYER_IDX] = reinterpret_cast<PyTypeObject*>(&Sbk_WindowsMediaPlayer_Type);

    if (!Shiboken::ObjectType::introduceWrapperType(module, "WindowsMediaPlayer", "WindowsMediaPlayer*",
        &Sbk_WindowsMediaPlayer_Type, &Shiboken::callCppDestructor< ::WindowsMediaPlayer >)) {
        return;
    }

    // Register Converter
    SbkConverter* converter = Shiboken::Conversions::createConverter(&Sbk_WindowsMediaPlayer_Type,
        WindowsMediaPlayer_PythonToCpp_WindowsMediaPlayer_PTR,
        is_WindowsMediaPlayer_PythonToCpp_WindowsMediaPlayer_PTR_Convertible,
        WindowsMediaPlayer_PTR_CppToPython_WindowsMediaPlayer);

    Shiboken::Conversions::registerConverterName(converter, "WindowsMediaPlayer");
    Shiboken::Conversions::registerConverterName(converter, "WindowsMediaPlayer*");
    Shiboken::Conversions::registerConverterName(converter, "WindowsMediaPlayer&");
    Shiboken::Conversions::registerConverterName(converter, typeid(::WindowsMediaPlayer).name());



}
