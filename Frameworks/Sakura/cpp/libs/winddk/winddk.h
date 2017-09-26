#pragma once

// zwapi.h
// 9/23/2011 jichi
// Zw series APIs from winddk.

#include <windows.h>

// <wdm.h>
NTSYSAPI
NTSTATUS
NTAPI
ZwCreateFile(
    __out PHANDLE FileHandle,
    __in ACCESS_MASK DesiredAccess,
    __in POBJECT_ATTRIBUTES ObjectAttributes,
    __out PIO_STATUS_BLOCK IoStatusBlock,
    __in_opt PLARGE_INTEGER AllocationSize,
    __in ULONG FileAttributes,
    __in ULONG ShareAccess,
    __in ULONG CreateDisposition,
    __in ULONG CreateOptions,
    __in_bcount_opt(EaLength) PVOID EaBuffer,
    __in ULONG EaLength
    );

// <wdm.h>
NTSYSAPI
NTSTATUS
NTAPI
ZwClose(
    __in HANDLE Handle
    );

// EOF
