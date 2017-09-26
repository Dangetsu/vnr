// msvcrt/rtti.c
// 12/17/2011 jichi
// See: msvcrt/cpp.c from wine

// EOF
///*
//    This is a C++ run-time library for Windows kernel-mode drivers.
//    Copyright (C) 2004 Bo Branten.
//*/
//
///*
//    The following is a modified subset of wine/dlls/msvcrt/cpp.c
//    from version wine20040505.
//*/
//
///*
// * msvcrt.dll C++ objects
// *
// * Copyright 2000 Jon Griffiths
// * Copyright 2003 Alexandre Julliard
// *
// * This library is free software; you can redistribute it and/or
// * modify it under the terms of the GNU Lesser General Public
// * License as published by the Free Software Foundation; either
// * version 2.1 of the License, or (at your option) any later version.
// *
// * This library is distributed in the hope that it will be useful,
// * but WITHOUT ANY WARRANTY; without even the implied warranty of
// * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// * Lesser General Public License for more details.
// *
// * You should have received a copy of the GNU Lesser General Public
// * License along with this library; if not, write to the Free Software
// * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
// */
//
//#include <exception>
//#include <typeinfo>
//
//extern "C" unsigned char __stdcall IsBadReadPtr(const void*, unsigned int);
//
//typedef void (*v_table_ptr)();
//
//typedef struct _cpp_object
//{
//    v_table_ptr*    vtable;
//} cpp_object;
//
//typedef struct _rtti_base_descriptor
//{
//    type_info*      type_descriptor;
//    int             num_base_classes;
//    int             base_class_offset;
//    unsigned int    flags;
//    int             unknown1;
//    int             unknown2;
//} rtti_base_descriptor;
//
//typedef struct _rtti_base_array
//{
//    const rtti_base_descriptor* bases[3];   /* First element is the class itself */
//} rtti_base_array;
//
//typedef struct _rtti_object_hierachy
//{
//    int                     unknown1;
//    int                     unknown2;
//    int                     array_len;  /* Size of the array pointed to by 'base_classes' */
//    const rtti_base_array*  base_classes;
//} rtti_object_hierachy;
//
//typedef struct _rtti_object_locator
//{
//    int                         unknown1;
//    int                         base_class_offset;
//    unsigned int                flags;
//    type_info*                  type_descriptor;
//    const rtti_object_hierachy* type_hierachy;
//} rtti_object_locator;
//
///* Get type info from an object (internal) */
//static const rtti_object_locator* RTTI_GetObjectLocator(void* inptr)
//{
//    cpp_object* cppobj = (cpp_object*) inptr;
//    const rtti_object_locator* obj_locator = 0;
//
//    if (!IsBadReadPtr(cppobj, sizeof(void*)) &&
//        !IsBadReadPtr(cppobj->vtable - 1, sizeof(void*)) &&
//        !IsBadReadPtr((void*)cppobj->vtable[-1], sizeof(rtti_object_locator)))
//    {
//        obj_locator = (rtti_object_locator*) cppobj->vtable[-1];
//    }
//
//    return obj_locator;
//}
//
///******************************************************************
// *      __RTtypeid (MSVCRT.@)
// *
// * Retrieve the Run Time Type Information (RTTI) for a C++ object.
// *
// * PARAMS
// *  cppobj [I] C++ object to get type information for.
// *
// * RETURNS
// *  Success: A type_info object describing cppobj.
// *  Failure: If the object to be cast has no RTTI, a __non_rtti_object
// *           exception is thrown. If cppobj is NULL, a bad_typeid exception
// *           is thrown. In either case, this function does not return.
// *
// * NOTES
// *  This function is usually called by compiler generated code as a result
// *  of using one of the C++ dynamic cast statements.
// */
//extern "C" void* __cdecl __RTtypeid(void* inptr)
//{
//    cpp_object* cppobj = (cpp_object*) inptr;
//    const rtti_object_locator* obj_locator = RTTI_GetObjectLocator(cppobj);
//
//    if (!obj_locator)
//    {
//        if (!cppobj)
//        {
//            throw std::bad_typeid();
//        }
//        else
//        {
//            throw std::__non_rtti_object("");
//        }
//    }
//
//    return obj_locator->type_descriptor;
//}
//
///******************************************************************
// *      __RTDynamicCast (MSVCRT.@)
// *
// * Dynamically cast a C++ object to one of its base classes.
// *
// * PARAMS
// *  inptr       [I] Any C++ object to cast
// *  unknown     [I] Reserved, set to 0
// *  SrcType     [I] type_info object describing cppobj
// *  TargetType  [I] type_info object describing the base class to cast to
// *  isReference [I] TRUE = throw an exception if the cast fails, FALSE = don't
// *
// * RETURNS
// *  Success: The address of cppobj, cast to the object described by dst.
// *  Failure: NULL, If the object to be cast has no RTTI, or dst is not a
// *           valid cast for cppobj. If isReference is TRUE, a bad_cast exception
// *           is thrown and this function does not return.
// *
// * NOTES
// *  This function is usually called by compiler generated code as a result
// *  of using one of the C++ dynamic cast statements.
// */
//extern "C" void* __cdecl __RTDynamicCast(void* inptr, long unknown, void* SrcType, void* TargetType, int isReference)
//{
//    cpp_object* cppobj = (cpp_object*) inptr;
//    type_info* src = (type_info*) SrcType;
//    type_info* dst = (type_info*) TargetType;
//    const rtti_object_locator* obj_locator;
//
//    if (unknown)
//    {
//        //DbgPrint("Unknown parameter is non-zero: please report\n");
//    }
//
//    if (!cppobj)
//    {
//        return 0;
//    }
//
//    obj_locator = RTTI_GetObjectLocator(cppobj);
//
//    /* To cast an object at runtime:
//     * 1.Find out the true type of the object from the typeinfo at vtable[-1]
//     * 2.Search for the destination type in the class hierarchy
//     * 3.If destination type is found, return base object address + dest offset
//     *   Otherwise, fail the cast
//     */
//    if (obj_locator)
//    {
//        int count = 0;
//        const rtti_object_hierachy* obj_bases = obj_locator->type_hierachy;
//        const rtti_base_descriptor* const * base_desc = obj_bases->base_classes->bases;
//        int src_offset = obj_locator->base_class_offset, dst_offset = -1;
//
//        while (count < obj_bases->array_len)
//        {
//            const type_info* typ = (*base_desc)->type_descriptor;
//
//            if (typ == dst)
//            {
//                dst_offset = (*base_desc)->base_class_offset;
//                break;
//            }
//            base_desc++;
//            count++;
//        }
//        if (dst_offset >= 0)
//        {
//            return (void*)((unsigned long)cppobj - src_offset + dst_offset);
//        }
//    }
//
//    /* VC++ sets isReference to 1 when the result of a dynamic_cast is assigned
//     * to a reference, since references cannot be NULL.
//     */
//    if (isReference)
//    {
//        throw std::bad_cast();
//    }
//
//    return 0;
//}
//
///******************************************************************
// *      __RTCastToVoid (MSVCRT.@)
// *
// * Dynamically cast a C++ object to a void*.
// *
// * PARAMS
// *  cppobj [I] The C++ object to cast
// *
// * RETURNS
// *  Success: The base address of the object as a void*.
// *  Failure: NULL, if cppobj is NULL or has no RTTI.
// *
// * NOTES
// *  This function is usually called by compiler generated code as a result
// *  of using one of the C++ dynamic cast statements.
// */
//extern "C" void* __cdecl __RTCastToVoid(void* inptr)
//{
//    cpp_object* cppobj = (cpp_object*) inptr;
//    const rtti_object_locator* obj_locator = RTTI_GetObjectLocator(cppobj);
//
//    if (!obj_locator)
//    {
//        return 0;
//    }
//
//    /* Casts to void* simply cast to the base object */
//    return (void*)((unsigned long)cppobj - obj_locator->base_class_offset);
//}
