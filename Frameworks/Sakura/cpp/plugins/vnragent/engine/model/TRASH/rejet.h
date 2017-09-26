#pragma once

// rejet.h
// 5/25/2014 jichi

#include "engine/engine.h"
#include "util/codepage.h"

// TODO: This class is not completed
class RejetEngine : public AbstractEngine
{
  SK_EXTEND_CLASS(RejetEngine, AbstractEngine)
  SK_DISABLE_COPY(RejetEngine)
public:
  RejetEngine() : Base("Rejet", Util::SjisCodePage, BlockingAttribute|HtmlAttribute) {}

  static bool match();
protected:
  bool attach() override;
  //bool detach() override;
};

// EOF
