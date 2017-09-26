#pragma once

// hookutil.h
// 5/29/2015 jichi
#include "winhook/hookdef.h"

WINHOOK_BEGIN_NAMESPACE

void *memcpy_(void *dst, const void *src, size_t num);
void *memset_(void *ptr, int value, size_t num);

/**
 *  Overwrite data at the target with the source data in the code section.
 *  @param  dst  target address to modify
 *  @param  src  address of the source data to copy
 *  @param  size  size of the source data to copy
 *  @return   if success
 */
bool csmemcpy(void *dst, const void *src, size_t size);

/**
 *  Overwrite data at the target with the source data in the code section.
 *  @param  dst  target address to modify
 *  @param  src  address of the source data to copy
 *  @param  size  size of the source data to copy
 *  @return   if success
 */
bool csmemset(void *dst, byte value, size_t num);

// Remove instruction at address by nop
bool remove_inst(ulong addr);

WINHOOK_END_NAMESPACE

// EOF
