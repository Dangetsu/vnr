#pragma once

// ceviotts.h
// 4/15/2014 jichi

#ifdef _MSC_VER
# include <cstddef> // for wchar_t
#endif // _MSC_VER

// - Types -

// Original type:
//
// namespace CeVIO {
//   struct __declspec(uuid("5dd7584f-c9a9-326d-8396-404911a5550b"))
//   ITalker : IDispatch
//
namespace CeVIO
{
  struct IServiceControl;
  struct ISpeakingState;
  struct ITalker;
}
typedef CeVIO::IServiceControl cevioservice_t; // opaque handle
typedef CeVIO::ITalker ceviotts_t; // opaque handle
typedef CeVIO::ISpeakingState ceviotask_t; // opaque handle

// - Functions -

/**
 * Start the CeVIO service
 * @param  launch  start CeVIO process if not exist
 * @return  service handle
 */
cevioservice_t *cevioservice_create(bool launch = true);
void cevioservice_destroy(cevioservice_t *service);

ceviotts_t *ceviotts_create();
void ceviotts_destroy(ceviotts_t *talker);

ceviotask_t *ceviotts_speak(ceviotts_t *talker, const char *text);
bool ceviotask_wait(ceviotask_t *state);
bool ceviotask_wait(ceviotask_t *state, double seconds);

void ceviotts_set_cast(ceviotts_t *talker, const char *value);
void ceviotts_set_volume(ceviotts_t *talker, long value);
void ceviotts_set_speed(ceviotts_t *talker, long value);
void ceviotts_set_tone(ceviotts_t *talker, long value);
void ceviotts_set_alpha(ceviotts_t *talker, long value);

// EOF
