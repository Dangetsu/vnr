
#include <sbkpython.h>
#include <shiboken.h>
#include <algorithm>
#include <pyside.h>
#include "pyhanja_python.h"



// Extra includes

// Current module's type array.
PyTypeObject** SbkpyhanjaTypes;
// Current module's converter array.
SbkConverter** SbkpyhanjaTypeConverters;
void cleanTypesAttributes(void) {
    for (int i = 0, imax = SBK_pyhanja_IDX_COUNT; i < imax; i++) {
        PyObject *pyType = reinterpret_cast<PyObject*>(SbkpyhanjaTypes[i]);
        if (pyType && PyObject_HasAttrString(pyType, "staticMetaObject"))
            PyObject_SetAttrString(pyType, "staticMetaObject", Py_None);
    }
}
// Global functions ------------------------------------------------------------

static PyMethodDef pyhanja_methods[] = {
    {0} // Sentinel
};

// Classes initialization functions ------------------------------------------------------------
void init_QHanjaHangulConverter(PyObject* module);
void init_QHangulHanjaConverter(PyObject* module);

// Required modules' type and converter arrays.
PyTypeObject** SbkPySide_QtCoreTypes;
SbkConverter** SbkPySide_QtCoreTypeConverters;

// Module initialization ------------------------------------------------------------
// Container Type converters.

// C++ to Python conversion for type 'QPair<QString, QString >'.
static PyObject* _QPair_QString_QString__CppToPython__QPair_QString_QString_(const void* cppIn) {
    ::QPair<QString, QString >& cppInRef = *((::QPair<QString, QString >*)cppIn);

            PyObject* pyOut = PyTuple_New(2);
            PyTuple_SET_ITEM(pyOut, 0, Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppInRef.first));
            PyTuple_SET_ITEM(pyOut, 1, Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppInRef.second));
            return pyOut;

}
static void _QPair_QString_QString__PythonToCpp__QPair_QString_QString_(PyObject* pyIn, void* cppOut) {
    ::QPair<QString, QString >& cppOutRef = *((::QPair<QString, QString >*)cppOut);

            Shiboken::Conversions::pythonToCppCopy(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], PySequence_Fast_GET_ITEM(pyIn, 0), &(cppOutRef.first));
            Shiboken::Conversions::pythonToCppCopy(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], PySequence_Fast_GET_ITEM(pyIn, 1), &(cppOutRef.second));

}
static PythonToCppFunc is__QPair_QString_QString__PythonToCpp__QPair_QString_QString__Convertible(PyObject* pyIn) {
    if (Shiboken::Conversions::convertiblePairTypes(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], false, SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], false, pyIn))
        return _QPair_QString_QString__PythonToCpp__QPair_QString_QString_;
    return 0;
}

// C++ to Python conversion for type 'QList<QPair<QString, QString > >'.
static PyObject* _QList_QPair_QString_QString___CppToPython__QList_QPair_QString_QString__(const void* cppIn) {
    ::QList<QPair<QString, QString > >& cppInRef = *((::QList<QPair<QString, QString > >*)cppIn);

                // TEMPLATE - cpplist_to_pylist_conversion - START
        PyObject* pyOut = PyList_New((int) cppInRef.size());
        ::QList<QPair<QString, QString > >::const_iterator it = cppInRef.begin();
        for (int idx = 0; it != cppInRef.end(); ++it, ++idx) {
            ::QPair<QString, QString > cppItem(*it);
            PyList_SET_ITEM(pyOut, idx, Shiboken::Conversions::copyToPython(SbkpyhanjaTypeConverters[SBK_PYHANJA_QPAIR_QSTRING_QSTRING_IDX], &cppItem));
        }
        return pyOut;
        // TEMPLATE - cpplist_to_pylist_conversion - END

}
static void _QList_QPair_QString_QString___PythonToCpp__QList_QPair_QString_QString__(PyObject* pyIn, void* cppOut) {
    ::QList<QPair<QString, QString > >& cppOutRef = *((::QList<QPair<QString, QString > >*)cppOut);

                // TEMPLATE - pyseq_to_cpplist_conversion - START
    for (int i = 0; i < PySequence_Size(pyIn); i++) {
        Shiboken::AutoDecRef pyItem(PySequence_GetItem(pyIn, i));
        ::QPair<QString, QString > cppItem = ::QPair<QString, QString >();
        Shiboken::Conversions::pythonToCppCopy(SbkpyhanjaTypeConverters[SBK_PYHANJA_QPAIR_QSTRING_QSTRING_IDX], pyItem, &(cppItem));
        cppOutRef << cppItem;
    }
    // TEMPLATE - pyseq_to_cpplist_conversion - END

}
static PythonToCppFunc is__QList_QPair_QString_QString___PythonToCpp__QList_QPair_QString_QString___Convertible(PyObject* pyIn) {
    if (Shiboken::Conversions::convertibleSequenceTypes(SbkpyhanjaTypeConverters[SBK_PYHANJA_QPAIR_QSTRING_QSTRING_IDX], pyIn))
        return _QList_QPair_QString_QString___PythonToCpp__QList_QPair_QString_QString__;
    return 0;
}

// C++ to Python conversion for type 'QList<QList<QPair<QString, QString > > >'.
static PyObject* _QList_QList_QPair_QString_QString____CppToPython__QList_QList_QPair_QString_QString___(const void* cppIn) {
    ::QList<QList<QPair<QString, QString > > >& cppInRef = *((::QList<QList<QPair<QString, QString > > >*)cppIn);

                // TEMPLATE - cpplist_to_pylist_conversion - START
        PyObject* pyOut = PyList_New((int) cppInRef.size());
        ::QList<QList<QPair<QString, QString > > >::const_iterator it = cppInRef.begin();
        for (int idx = 0; it != cppInRef.end(); ++it, ++idx) {
            ::QList<QPair<QString, QString > > cppItem(*it);
            PyList_SET_ITEM(pyOut, idx, Shiboken::Conversions::copyToPython(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QPAIR_QSTRING_QSTRING_IDX], &cppItem));
        }
        return pyOut;
        // TEMPLATE - cpplist_to_pylist_conversion - END

}
static void _QList_QList_QPair_QString_QString____PythonToCpp__QList_QList_QPair_QString_QString___(PyObject* pyIn, void* cppOut) {
    ::QList<QList<QPair<QString, QString > > >& cppOutRef = *((::QList<QList<QPair<QString, QString > > >*)cppOut);

                // TEMPLATE - pyseq_to_cpplist_conversion - START
    for (int i = 0; i < PySequence_Size(pyIn); i++) {
        Shiboken::AutoDecRef pyItem(PySequence_GetItem(pyIn, i));
        ::QList<QPair<QString, QString > > cppItem = ::QList<QPair<QString, QString > >();
        Shiboken::Conversions::pythonToCppCopy(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QPAIR_QSTRING_QSTRING_IDX], pyItem, &(cppItem));
        cppOutRef << cppItem;
    }
    // TEMPLATE - pyseq_to_cpplist_conversion - END

}
static PythonToCppFunc is__QList_QList_QPair_QString_QString____PythonToCpp__QList_QList_QPair_QString_QString____Convertible(PyObject* pyIn) {
    if (Shiboken::Conversions::convertibleSequenceTypes(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QPAIR_QSTRING_QSTRING_IDX], pyIn))
        return _QList_QList_QPair_QString_QString____PythonToCpp__QList_QList_QPair_QString_QString___;
    return 0;
}

// C++ to Python conversion for type 'QList<QVariant >'.
static PyObject* _QList_QVariant__CppToPython__QList_QVariant_(const void* cppIn) {
    ::QList<QVariant >& cppInRef = *((::QList<QVariant >*)cppIn);

                // TEMPLATE - cpplist_to_pylist_conversion - START
        PyObject* pyOut = PyList_New((int) cppInRef.size());
        ::QList<QVariant >::const_iterator it = cppInRef.begin();
        for (int idx = 0; it != cppInRef.end(); ++it, ++idx) {
            ::QVariant cppItem(*it);
            PyList_SET_ITEM(pyOut, idx, Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QVARIANT_IDX], &cppItem));
        }
        return pyOut;
        // TEMPLATE - cpplist_to_pylist_conversion - END

}
static void _QList_QVariant__PythonToCpp__QList_QVariant_(PyObject* pyIn, void* cppOut) {
    ::QList<QVariant >& cppOutRef = *((::QList<QVariant >*)cppOut);

                // TEMPLATE - pyseq_to_cpplist_conversion - START
    for (int i = 0; i < PySequence_Size(pyIn); i++) {
        Shiboken::AutoDecRef pyItem(PySequence_GetItem(pyIn, i));
        ::QVariant cppItem = ::QVariant();
        Shiboken::Conversions::pythonToCppCopy(SbkPySide_QtCoreTypeConverters[SBK_QVARIANT_IDX], pyItem, &(cppItem));
        cppOutRef << cppItem;
    }
    // TEMPLATE - pyseq_to_cpplist_conversion - END

}
static PythonToCppFunc is__QList_QVariant__PythonToCpp__QList_QVariant__Convertible(PyObject* pyIn) {
    if (Shiboken::Conversions::convertibleSequenceTypes(SbkPySide_QtCoreTypeConverters[SBK_QVARIANT_IDX], pyIn))
        return _QList_QVariant__PythonToCpp__QList_QVariant_;
    return 0;
}

// C++ to Python conversion for type 'QList<QString >'.
static PyObject* _QList_QString__CppToPython__QList_QString_(const void* cppIn) {
    ::QList<QString >& cppInRef = *((::QList<QString >*)cppIn);

                // TEMPLATE - cpplist_to_pylist_conversion - START
        PyObject* pyOut = PyList_New((int) cppInRef.size());
        ::QList<QString >::const_iterator it = cppInRef.begin();
        for (int idx = 0; it != cppInRef.end(); ++it, ++idx) {
            ::QString cppItem(*it);
            PyList_SET_ITEM(pyOut, idx, Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &cppItem));
        }
        return pyOut;
        // TEMPLATE - cpplist_to_pylist_conversion - END

}
static void _QList_QString__PythonToCpp__QList_QString_(PyObject* pyIn, void* cppOut) {
    ::QList<QString >& cppOutRef = *((::QList<QString >*)cppOut);

                // TEMPLATE - pyseq_to_cpplist_conversion - START
    for (int i = 0; i < PySequence_Size(pyIn); i++) {
        Shiboken::AutoDecRef pyItem(PySequence_GetItem(pyIn, i));
        ::QString cppItem = ::QString();
        Shiboken::Conversions::pythonToCppCopy(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], pyItem, &(cppItem));
        cppOutRef << cppItem;
    }
    // TEMPLATE - pyseq_to_cpplist_conversion - END

}
static PythonToCppFunc is__QList_QString__PythonToCpp__QList_QString__Convertible(PyObject* pyIn) {
    if (Shiboken::Conversions::convertibleSequenceTypes(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], pyIn))
        return _QList_QString__PythonToCpp__QList_QString_;
    return 0;
}

// C++ to Python conversion for type 'QMap<QString, QVariant >'.
static PyObject* _QMap_QString_QVariant__CppToPython__QMap_QString_QVariant_(const void* cppIn) {
    ::QMap<QString, QVariant >& cppInRef = *((::QMap<QString, QVariant >*)cppIn);

                // TEMPLATE - cppmap_to_pymap_conversion - START
        PyObject* pyOut = PyDict_New();
        ::QMap<QString, QVariant >::const_iterator it = cppInRef.begin();
        for (; it != cppInRef.end(); ++it) {
            ::QString key = it.key();
            ::QVariant value = it.value();
            PyObject* pyKey = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], &key);
            PyObject* pyValue = Shiboken::Conversions::copyToPython(SbkPySide_QtCoreTypeConverters[SBK_QVARIANT_IDX], &value);
            PyDict_SetItem(pyOut, pyKey, pyValue);
            Py_DECREF(pyKey);
            Py_DECREF(pyValue);
        }
        return pyOut;
      // TEMPLATE - cppmap_to_pymap_conversion - END

}
static void _QMap_QString_QVariant__PythonToCpp__QMap_QString_QVariant_(PyObject* pyIn, void* cppOut) {
    ::QMap<QString, QVariant >& cppOutRef = *((::QMap<QString, QVariant >*)cppOut);

                // TEMPLATE - pydict_to_cppmap_conversion - START
    PyObject* key;
    PyObject* value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(pyIn, &pos, &key, &value)) {
        ::QString cppKey = ::QString();
        Shiboken::Conversions::pythonToCppCopy(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], key, &(cppKey));
        ::QVariant cppValue = ::QVariant();
        Shiboken::Conversions::pythonToCppCopy(SbkPySide_QtCoreTypeConverters[SBK_QVARIANT_IDX], value, &(cppValue));
        cppOutRef.insert(cppKey, cppValue);
    }
    // TEMPLATE - pydict_to_cppmap_conversion - END

}
static PythonToCppFunc is__QMap_QString_QVariant__PythonToCpp__QMap_QString_QVariant__Convertible(PyObject* pyIn) {
    if (Shiboken::Conversions::convertibleDictTypes(SbkPySide_QtCoreTypeConverters[SBK_QSTRING_IDX], false, SbkPySide_QtCoreTypeConverters[SBK_QVARIANT_IDX], false, pyIn))
        return _QMap_QString_QVariant__PythonToCpp__QMap_QString_QVariant_;
    return 0;
}


#if defined _WIN32 || defined __CYGWIN__
    #define SBK_EXPORT_MODULE __declspec(dllexport)
#elif __GNUC__ >= 4
    #define SBK_EXPORT_MODULE __attribute__ ((visibility("default")))
#else
    #define SBK_EXPORT_MODULE
#endif

#ifdef IS_PY3K
static struct PyModuleDef moduledef = {
    /* m_base     */ PyModuleDef_HEAD_INIT,
    /* m_name     */ "pyhanja",
    /* m_doc      */ 0,
    /* m_size     */ -1,
    /* m_methods  */ pyhanja_methods,
    /* m_reload   */ 0,
    /* m_traverse */ 0,
    /* m_clear    */ 0,
    /* m_free     */ 0
};

#endif
SBK_MODULE_INIT_FUNCTION_BEGIN(pyhanja)
    {
        Shiboken::AutoDecRef requiredModule(Shiboken::Module::import("PySide.QtCore"));
        if (requiredModule.isNull())
            return SBK_MODULE_INIT_ERROR;
        SbkPySide_QtCoreTypes = Shiboken::Module::getTypes(requiredModule);
        SbkPySide_QtCoreTypeConverters = Shiboken::Module::getTypeConverters(requiredModule);
    }

    // Create an array of wrapper types for the current module.
    static PyTypeObject* cppApi[SBK_pyhanja_IDX_COUNT];
    SbkpyhanjaTypes = cppApi;

    // Create an array of primitive type converters for the current module.
    static SbkConverter* sbkConverters[SBK_pyhanja_CONVERTERS_IDX_COUNT];
    SbkpyhanjaTypeConverters = sbkConverters;

#ifdef IS_PY3K
    PyObject* module = Shiboken::Module::create("pyhanja", &moduledef);
#else
    PyObject* module = Shiboken::Module::create("pyhanja", pyhanja_methods);
#endif

    // Initialize classes in the type system
    init_QHanjaHangulConverter(module);
    init_QHangulHanjaConverter(module);

    // Register converter for type 'QPair<QString,QString>'.
    SbkpyhanjaTypeConverters[SBK_PYHANJA_QPAIR_QSTRING_QSTRING_IDX] = Shiboken::Conversions::createConverter(&PyList_Type, _QPair_QString_QString__CppToPython__QPair_QString_QString_);
    Shiboken::Conversions::registerConverterName(SbkpyhanjaTypeConverters[SBK_PYHANJA_QPAIR_QSTRING_QSTRING_IDX], "QPair<QString,QString>");
    Shiboken::Conversions::addPythonToCppValueConversion(SbkpyhanjaTypeConverters[SBK_PYHANJA_QPAIR_QSTRING_QSTRING_IDX],
        _QPair_QString_QString__PythonToCpp__QPair_QString_QString_,
        is__QPair_QString_QString__PythonToCpp__QPair_QString_QString__Convertible);

    // Register converter for type 'QList<QPair<QString,QString>>'.
    SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QPAIR_QSTRING_QSTRING_IDX] = Shiboken::Conversions::createConverter(&PyList_Type, _QList_QPair_QString_QString___CppToPython__QList_QPair_QString_QString__);
    Shiboken::Conversions::registerConverterName(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QPAIR_QSTRING_QSTRING_IDX], "QList<QPair<QString,QString>>");
    Shiboken::Conversions::addPythonToCppValueConversion(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QPAIR_QSTRING_QSTRING_IDX],
        _QList_QPair_QString_QString___PythonToCpp__QList_QPair_QString_QString__,
        is__QList_QPair_QString_QString___PythonToCpp__QList_QPair_QString_QString___Convertible);

    // Register converter for type 'QList<QList<QPair<QString,QString>>>'.
    SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QLIST_QPAIR_QSTRING_QSTRING_IDX] = Shiboken::Conversions::createConverter(&PyList_Type, _QList_QList_QPair_QString_QString____CppToPython__QList_QList_QPair_QString_QString___);
    Shiboken::Conversions::registerConverterName(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QLIST_QPAIR_QSTRING_QSTRING_IDX], "QList<QList<QPair<QString,QString>>>");
    Shiboken::Conversions::addPythonToCppValueConversion(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QLIST_QPAIR_QSTRING_QSTRING_IDX],
        _QList_QList_QPair_QString_QString____PythonToCpp__QList_QList_QPair_QString_QString___,
        is__QList_QList_QPair_QString_QString____PythonToCpp__QList_QList_QPair_QString_QString____Convertible);

    // Register converter for type 'QList<QVariant>'.
    SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QVARIANT_IDX] = Shiboken::Conversions::createConverter(&PyList_Type, _QList_QVariant__CppToPython__QList_QVariant_);
    Shiboken::Conversions::registerConverterName(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QVARIANT_IDX], "QList<QVariant>");
    Shiboken::Conversions::addPythonToCppValueConversion(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QVARIANT_IDX],
        _QList_QVariant__PythonToCpp__QList_QVariant_,
        is__QList_QVariant__PythonToCpp__QList_QVariant__Convertible);

    // Register converter for type 'QList<QString>'.
    SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QSTRING_IDX] = Shiboken::Conversions::createConverter(&PyList_Type, _QList_QString__CppToPython__QList_QString_);
    Shiboken::Conversions::registerConverterName(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QSTRING_IDX], "QList<QString>");
    Shiboken::Conversions::addPythonToCppValueConversion(SbkpyhanjaTypeConverters[SBK_PYHANJA_QLIST_QSTRING_IDX],
        _QList_QString__PythonToCpp__QList_QString_,
        is__QList_QString__PythonToCpp__QList_QString__Convertible);

    // Register converter for type 'QMap<QString,QVariant>'.
    SbkpyhanjaTypeConverters[SBK_PYHANJA_QMAP_QSTRING_QVARIANT_IDX] = Shiboken::Conversions::createConverter(&PyDict_Type, _QMap_QString_QVariant__CppToPython__QMap_QString_QVariant_);
    Shiboken::Conversions::registerConverterName(SbkpyhanjaTypeConverters[SBK_PYHANJA_QMAP_QSTRING_QVARIANT_IDX], "QMap<QString,QVariant>");
    Shiboken::Conversions::addPythonToCppValueConversion(SbkpyhanjaTypeConverters[SBK_PYHANJA_QMAP_QSTRING_QVARIANT_IDX],
        _QMap_QString_QVariant__PythonToCpp__QMap_QString_QVariant_,
        is__QMap_QString_QVariant__PythonToCpp__QMap_QString_QVariant__Convertible);

    // Register primitive types converters.

    Shiboken::Module::registerTypes(module, SbkpyhanjaTypes);
    Shiboken::Module::registerTypeConverters(module, SbkpyhanjaTypeConverters);

    if (PyErr_Occurred()) {
        PyErr_Print();
        Py_FatalError("can't initialize module pyhanja");
    }
    PySide::registerCleanupFunction(cleanTypesAttributes);
SBK_MODULE_INIT_FUNCTION_END
