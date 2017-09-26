// main.cc
// 2/25/2014 jichi
// http://docs.python.org/2/c-api/veryhigh.html
// http://stackoverflow.com/questions/1387906/c-with-python-embedding-crash-if-python-not-installed
// http://stackoverflow.com/questions/18428600/unable-to-get-python-embedded-to-work-with-zipd-library
// http://wendal.net/2013/0325.html
// https://github.com/goagent/pybuild
// https://raw.github.com/schmir/bbfreeze/master/bbfreeze/py.py

#include <Python.h>
#include <cstdio>

int main(int argc, char *argv[])
{
  printf("enter\n");
  Py_SetProgramName(argv[0]);
    Py_Initialize();
    PySys_SetArgv(argc, argv);
    FILE * fp = fopen("/home/xxx/yyy/zzz.py", "r");
    //PyRun_SimpleFile(fp, "zzz.py");
    PyRun_AnyFile(fp, "zzz.py");
    Py_Finalize();
    return 0;

    /*
  char pyHome[] = ".";
  //Py_NoSiteFlag = 1;
  //Py_SetProgramName(argv[0]);
  //Py_SetPythonHome(pyHome);
  Py_Initialize();

  FILE *fp = fopen("python27.py", "r");
  //PyCompilerFlags flags = {PyCF_SOURCE_IS_UTF8};

  printf("run: fp = %x\n", fp);

  int ret = PyRun_AnyFile(fp, "python27.py");
  //int ret = PyRun_AnyFileFlags(fp, "python27.py", &flags);

  //PyRun_SimpleString("import sys");
  //PyRun_SimpleString("sys.path = ['.','python27.zip','python27.zip/DLLs','python27.zip/Lib','site-packages']");
  //PyRun_SimpleString("print 'hello'");

  //PyRun_SimpleString("from time import time,ctime\n"
  //     dssssssssssssssssssssssssssssdffxdxfxfZx            "print 'Today is',ctime(time())\n");
  fclose(fp);

  //cerr << Py_GetPath() << endl;
  Py_Finalize();

  printf("leave: ret = %i\n", ret);
  return ret;
  */
}

// EOF
