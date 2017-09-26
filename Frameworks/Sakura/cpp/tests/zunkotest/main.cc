// main.cc
// 10/11/2014 jichi
#include "main.h"
#include "aitalked/aitalked.h"
#include <windows.h>
#include <iostream>
#include <string>

void test()
{
  const char *text = "hello world!";
  //const char *text = "\x83\x6E\x21\x83\x8D\x81\x5B";
  //const char *text = "\x91\x9e\x82\xb5\x82\xdd";

  std::cerr << "enter" << std::endl;
  auto ai = new AITalkSynthesizer;
  ai->init(L"aitalked.dll");
  bool ok = ai->isValid();
  std::cerr << "init: " << ok << std::endl;

  auto r = ai->speak(text);
  std::cerr << "tts: " << (int)r << std::endl;

  std::cerr << "leave" << std::endl;
}

void TestThread::run()
{
  test();
  exec();
}

int main(int argc, char *argv[])
{
  QCoreApplication app(argc, argv);
  TestThread t;
  t.start();
  std::cerr << "exec" << std::endl;
  app.exec();
  return 0;
}

// EOF
