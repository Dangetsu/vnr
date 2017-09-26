#pragma once
#ifdef __cplusplus
// kstl/mutex.h
// 12/11/2011 jichi

#include "kstl/new.h"
#include "kstl/win.h"
//#include <boost/scoped_ptr.hpp>

// - kstl_mutex_traits -

template <typename _Mutex>
  class kstl_mutex_traits
  {
    typedef _Mutex mutex_type;
    enum {
      has_irql = 0,
      has_try_lock = 1
    };
  };

// - kstl_mutex_locker -

template <typename _Mutex>
  class kstl_mutex_locker
  {
    typedef kstl_mutex_locker<_Mutex> _Self;
    kstl_mutex(const _Self&);
    _Self &operator=(const _Self&);

    _Mutex *_M_mutex;
  public:
    typedef _Mutex mutex_type;
    explicit kstl_mutex_locker(mutex_type *mutex)
      : _M_mutex(mutex) { mutex->lock(); }
    ~kstl_mutex_locker() { _M_mutex->unlock(); }
    mutex_type *mutex() const { return _M_mutex; }
  };

// - kstl_mutex -

template <typename _Mutex, size_t _Irql = 0>
  class kstl_mutex
  {
    typedef kstl_mutex<_Mutex> _Self;
    typedef _Mutex __native_type;
    enum { __minimal_irql = _Irql };
    __native_type _M_mutex;

    kstl_mutex(const _Self&);
    _Self &operator=(const _Self&);
  private:
    kstl_mutex() {}
    typedef __native_type *native_handle_type;
    native_handle_type native_handle() { return &_M_mutex; }
    static size_t minimal_irql() { return __minimal_irql; }

    void unlock() {}
    void lock() {}
    bool try_lock() {}
  };

template <>
  class kstl_mutex<KSPIN_LOCK>
  {
    typedef kstl_mutex<KSPIN_LOCK> _Self;
    typedef KSPIN_LOCK __native_type;
    enum { __minimal_irql = 0 };

     KIRQL _M_irql;
     __native_type _M_mutex;

    kstl_mutex(const _Self&);
    _Self &operator=(const _Self&);
    bool try_lock();
  public:
    typedef __native_type *native_handle_type;
    native_handle_type native_handle() { return &_M_mutex; }
    static size_t minimal_irql() { return __minimal_irql; }

    kstl_mutex() { ::KeInitializeSpinLock(&_M_mutex); }
    void lock() { KeAcquireSpinLock(&_M_mutex, &_M_irql); }
    void unlock() { ::KeReleaseSpinLock(&_M_mutex, _M_irql); }
  };

template <>
  class kstl_mutex<KSPIN_LOCK, DISPATCH_LEVEL>
  {
    typedef kstl_mutex<KSPIN_LOCK> _Self;
    typedef KSPIN_LOCK __native_type;
    enum { __minimal_irql = DISPATCH_LEVEL };

     __native_type _M_mutex;

    kstl_mutex(const _Self&);
    _Self &operator=(const _Self&);
  public:
    typedef __native_type *native_handle_type;
    native_handle_type native_handle() { return &_M_mutex; }
    static size_t minimal_irql() { return 0; }

    kstl_mutex() { ::KeInitializeSpinLock(&_M_mutex); }
    void lock() { ::KeAcquireSpinLockAtDpcLevel(&_M_mutex); }
    bool try_lock() { return ::KeTryToAcquireSpinLockAtDpcLevel(&_M_mutex); }
    void unlock() { ::KeReleaseSpinLockFromDpcLevel(&_M_mutex); }
  };

template <>
  class kstl_mutex<KMUTEX>
  {
    //  MSDN:
    //  Storage for a mutex object must be resident: in the device extension of a
    //  driver-created device object, in the controller extension of a driver-created
    //  controller object, or in nonpaged pool allocated by the caller.
    typedef kstl_mutex<KMUTEX> _Self;
    typedef KMUTEX __native_type;
    enum { __minimal_irql = 0 };

    //boost::scoped_ptr<__native_type> _M_handle;
    __native_type *_M_handle;

    kstl_mutex(const _Self&);
    _Self &operator=(const _Self&);
    bool try_lock();
  public:
    typedef __native_type *native_handle_type;
    native_handle_type native_handle() { return _M_handle; }
    static size_t minimal_irql() { return __minimal_irql; }

    ///  out-of-memory not checked.
    explicit kstl_mutex(ULONG level = 0)
    { ::KeInitializeMutex(_M_handle = new __native_type, level); }

    ~kstl_mutex() { delete _M_handle; }

    bool lock()
    {
      return NT_SUCCESS(
        ::KeWaitForMutexObject(_M_handle, Executive, KernelMode, FALSE, nullptr)
      );
    }

    bool lock(LONGLONG timeout)
    {
      return NT_SUCCESS(
       ::KeWaitForMutexObject(_M_handle, Executive, KernelMode, FALSE,
         reinterpret_cast<PLARGE_INTEGER>(&timeout)
      ));
    }

    void unlock() { ::KeReleaseMutex(_M_handle, FALSE); }
  };

template <>
  class kstl_mutex<FAST_MUTEX>
  {
    typedef kstl_mutex<FAST_MUTEX> _Self;
    typedef FAST_MUTEX __native_type;
    enum { __minimal_irql = 0 };

    //  FAST_MUTEX structure, which represents the fast mutex, in the nonpaged memory pool.
    __native_type *_M_handle;

    kstl_mutex(const _Self&);
    _Self &operator=(const _Self&);
  public:
    typedef __native_type *native_handle_type;
    native_handle_type native_handle() { return _M_handle; }
    static size_t minimal_irql() { return __minimal_irql; }

    kstl_mutex() { ::ExInitializeFastMutex(_M_handle = new __native_type); }
    ~kstl_mutex() { delete _M_handle; }

    void lock() { ::ExAcquireFastMutex(_M_handle); }
    bool try_lock() { return ::ExTryToAcquireFastMutex(_M_handle); }
    void unlock() { ::ExReleaseFastMutex(_M_handle); }
  };

template <>
  class kstl_mutex<KGUARDED_MUTEX> // faster then FAST_MUTEX, not avaiable in Windows XP
  {
    typedef kstl_mutex<KGUARDED_MUTEX> _Self;
    typedef KGUARDED_MUTEX __native_type;
    enum { __minimal_irql = 0 };

    __native_type *_M_handle;

    kstl_mutex(const _Self&);
    _Self &operator=(const _Self&);
  public:
    typedef __native_type *native_handle_type;
    native_handle_type native_handle() { return _M_handle; }
    static size_t minimal_irql() { return __minimal_irql; }

    kstl_mutex() { ::KeInitializeGuardedMutex(_M_handle = new __native_type); }
    ~kstl_mutex() { delete _M_handle; }

    void lock() { ::KeAcquireGuardedMutex(_M_handle); }
    bool try_lock() { return ::KeTryToAcquireGuardedMutex(_M_handle); }
    void unlock() { ::KeReleaseGuardedMutex(_M_handle); }
  };

// - mutex -
namespace kstd { typedef ::kstl_mutex<FAST_MUTEX> mutex; }

#endif // __cplusplus
// EOF

/*
  struct once_flag
  {
  private:
    typedef __gthread_once_t __native_type;
    __native_type  _M_once;

  public:
    constexpr once_flag() : _M_once(__GTHREAD_ONCE_INIT) {}

    once_flag(const once_flag&) = delete;
    once_flag& operator=(const once_flag&) = delete;

    template<typename _Callable, typename... _Args>
      friend void
      call_once(once_flag& __once, _Callable&& __f, _Args&&... __args);
  };
*/

/*
template<class Event>
class AutoEventSetter
{
   Event& event_;
   bool bSet_;
   AutoEventSetter();

   AutoEventSetter(const AutoEventSetter& );
   AutoEventSetter& operator = (const AutoEventSetter& );
public:
   explicit AutoEventSetter(Event& event, bool bSet = true ):event_(event),bSet_(bSet){}
   ~AutoEventSetter()
   {
      if ( bSet_ )
        event_.set();
      else
        event_.reset ();

   }
};

template<class Guard>
class AutoGuard
{
   Guard & guard_;
   bool m_bCallDestructor;
   AutoGuard();
   AutoGuard(AutoGuard&);
   AutoGuard& operator = (const AutoGuard& );
public:
   explicit AutoGuard(Guard& guard)
      :guard_(guard),m_bCallDestructor(true)
   {
      guard_.enter();
   }
   ~AutoGuard()
   {
      if (m_bCallDestructor)
        guard_.leave();
   }
   void Release()
   {
      if (m_bCallDestructor)
      {
        m_bCallDestructor = false;
        guard_.leave();
      }
   }
};
template<class Guard>
class AutoGuardPtr
{
   Guard* guard_;
   AutoGuardPtr(const AutoGuardPtr&);
   AutoGuardPtr& operator =(const AutoGuardPtr&);
public:
   explicit AutoGuardPtr(Guard* guard)
      :guard_(guard)
   {
      if (guard_)
        guard_->enter();
   }
   void reset(Guard* guard)
   {
      if (guard_)
        guard_->leave();
      guard_= guard;
      if (guard_)
        guard_->enter();
   }
   ~AutoGuardPtr()
   {
      if (guard_)
        guard_->leave();
   }
};
inline void CloseUserOrKernelHandle(HANDLE hFile)
{
   if (IS_KERNEL_HANDLE(hFile))
      ZwClose(hFile);
   else
      NtClose(hFile);
};
class HandleGuard
{
   HANDLE h_;
   HandleGuard(HandleGuard&);
   HandleGuard& operator=(HandleGuard&);
public:
   explicit HandleGuard(HANDLE h)
      :h_(h){}
      ~HandleGuard(void)
      {
        if (h_)
        {
           CloseUserOrKernelHandle(h_);
        }
      }
      HANDLE get(){return h_;}
      HANDLE release()
      {
        HANDLE tmp = h_;
        h_ = 0;
        return tmp;
      }
      void reset(HANDLE h)
      {
        if (h_)
        {
           CloseUserOrKernelHandle(h_);
        }
        h_ = h;
      }
};
class ObjectGuard
{
   PVOID h_;
   ObjectGuard(ObjectGuard&);
   ObjectGuard& operator=(ObjectGuard&);
public:
   explicit ObjectGuard(PVOID h)
      :h_(h){}
      ~ObjectGuard(void)
      {
        if (h_)
           ObDereferenceObject(h_);
      }
      PVOID get(){return h_;}
      PVOID release()
      {
        PVOID tmp = h_;
        h_ = 0;
        return tmp;
      }
      void reset(PVOID h)
      {
        if (h_)
           ObDereferenceObject(h_);
        h_ = h;
      }
};
template<class Type>
class ObjectGuard2:protected ObjectGuard
{
public:
   explicit ObjectGuard2(Type *  ptr=0)
      : ObjectGuard(ptr)
   {
   }

   Type * get() { return (Type * )ObjectGuard::get(); }
   Type * release() { return (Type * )ObjectGuard::release(); }
   void reset(Type * ptr) { ObjectGuard::reset(ptr); }
   Type * operator -> () { return get(); }
};
class ProcessAttacher
{
   PEPROCESS h_;
   ProcessAttacher(ProcessAttacher&);
   ProcessAttacher& operator=(ProcessAttacher&);
public:
   explicit ProcessAttacher(PEPROCESS h)
      :h_(h){}
      ~ProcessAttacher()
      {
        if (h_)
           KeAttachProcess(h_);
      }
      PEPROCESS get(){return h_;}
      PEPROCESS release()
      {
        PEPROCESS tmp = h_;
        h_ = 0;
        return tmp;
      }
      void reset(PEPROCESS h)
      {
        if (h_)
           KeDetachProcess();
        h_ = h;
      }
};
typedef AutoGuard<Mutex> AutoMutex;
typedef AutoGuard<SpinLock> AutoSpinLock;
typedef AutoGuard<FastMutex> AutoFastMutex;


class CSyncMutexStrategy_BuiltIn
{
   Mutex  m_section;
public:
   typedef AutoMutex GuardType;
   typedef Mutex  SyncType;
   typedef AutoMutex ReadGuardType;

   SyncType & GetSyncObject() { return m_section; }
};

class CSyncMutexStrategy_Outside
{
   Mutex  * m_pSection;
public:
      CSyncMutexStrategy_Outside(Mutex  * pSection)
        : m_pSection(pSection)
      {
      }

   typedef AutoMutex GuardType;
   typedef Mutex  SyncType;
   typedef AutoMutex ReadGuardType;
   SyncType & GetSyncObject() { return *m_pSection; }
};

class CSyncSpinLockStrategy_BuiltIn

{
   SpinLock  m_section;
public:
   typedef AutoSpinLock GuardType;
   typedef SpinLock  SyncType;
   typedef AutoMutex ReadGuardType;
   SyncType & GetSyncObject() { return m_section; }
};

inline NTSTATUS WaitTwoEvents(PVOID Event0, PVOID Event1,
                WAIT_TYPE WaitType = WaitAny,
                KWAIT_REASON WaitReason = Executive,
                KPROCESSOR_MODE WaitMode = KernelMode,
                BOOLEAN Alertable = false,
                PLARGE_INTEGER Timeout = NULL,
                PKWAIT_BLOCK WaitBlockArray = NULL)
{
   ASSERT(Event0);
   ASSERT(Event1);

   PVOID  events[] = {Event0, Event1};

   return KeWaitForMultipleObjects(
        sizeof(events) / sizeof(events[0]),
        events,
        WaitAny,
        Executive,
        KernelMode,
        false,
        NULL,
        NULL);
}

template<EVENT_TYPE eventType>
class KernelCustomEvent
{
    KEVENT event_;

    KernelCustomEvent(const KernelCustomEvent&);
    KernelCustomEvent& operator =(const KernelCustomEvent&);
public:
    KernelCustomEvent(BOOLEAN initState = FALSE)
    {
        KeInitializeEvent(&event_, eventType, initState);
    }
    KEVENT* getPointer()
    {
        return &event_;
    }
    void wait()
    {
        NTSTATUS status = KeWaitForSingleObject(&event_, Executive, KernelMode, FALSE, NULL);
        if (!NT_SUCCESS(status))
        {
            KdPrint((__FUNCTION__" KeWaitForMutexObject fail %08X\n", status));
            __asm int 3;
        }
    }
    bool readState()
    {
        return KeReadStateEvent(&event_) != 0;
    }
    void set()
    {
        KeSetEvent(&event_, 0, FALSE);
    }
    void reset()
    {
        KeClearEvent(&event_);
    }
};

typedef KernelCustomEvent<NotificationEvent> KernelNotificationEvent;
typedef KernelCustomEvent<SynchronizationEvent> KernelSynchronizationEvent;

template<class LockType>
class ReverseSemaphore
{
    KernelNotificationEvent readyEvent_;
    LockType lock_;
    int count_;
public:
    ReverseSemaphore():count_(0), readyEvent_(TRUE){}
    KEVENT* getPointer()
    {
        return readyEvent_.getPointer();
    }
    void enter()
    {
        AutoGuard<LockType> guard(lock_);
        ++count_;
        readyEvent_.reset();
    }
    void leave()
    {
    bool ready = false;
    {
            AutoGuard<LockType> guard(lock_);
            --count_;
            ASSERT(count_ >= 0);
            if (count_ == 0)
            ready = true;
    }
    if (ready)
            readyEvent_.set();
    }
};
typedef ReverseSemaphore<Mutex> ReverseMutexSemaphore;
typedef AutoGuard<ReverseMutexSemaphore> AutoReverseMutexSemaphore;
typedef AutoGuardPtr<ReverseMutexSemaphore> AutoReverseMutexSemaphorePtr;


//---------------------------------------------------------------
// auto_ptr_kernel
template<class ResourceType>
class auto_ptr_kernel
{
    ResourceType * m_pResource;
public:
    auto_ptr_kernel()
        : m_pResource(0)
    {
    }

    explicit auto_ptr_kernel(ResourceType * pResource)
        : m_pResource( pResource )
    {
    }
    auto_ptr_kernel(auto_ptr_kernel & source_ptr)
        :
        m_pResource( source_ptr.get() )
    {
        source_ptr.m_pResource = 0;
    }

    auto_ptr_kernel & operator = (auto_ptr_kernel & source_ptr)
    {
        m_pResource = source_ptr.get();
        source_ptr.m_pResource = 0;
        return *this;
    }

    ~auto_ptr_kernel()
    {
        if (m_pResource)
            ExFreePool( m_pResource );
    }

    const ResourceType * get() const { return m_pResource; }
    ResourceType * get() { return m_pResource; }

    ResourceType * release()
    {
        ResourceType * pRes = m_pResource;
        m_pResource = 0;
        return pRes;
    }

    ResourceType * operator -> ()   {   return m_pResource;    }
    const ResourceType * operator -> () const {   return m_pResource;    }
    ResourceType & operator * ()   {   return *m_pResource;    }
    const ResourceType & operator * () const {   return *m_pResource;    }

    // non-standard
    ResourceType ** getPtr2()
    {
        if (m_pResource)
            throw std::exception("Cannot access member");
        return &m_pResource;
    }
};
//--------------------------------------------------------------
inline void * AllocatePaged(int iAdditionalSize)
{
    void * pData = ExAllocatePool(PagedPool, iAdditionalSize);
    if (!pData)
        throw std::bad_alloc();
    return pData;
}
//--------------------------------------------------------------
template<class Type>
Type * AllocatePaged(int iAdditionalSize=0)
{
    void * pData = ExAllocatePool(PagedPool, sizeof(Type)+iAdditionalSize);
    if (!pData)
        throw std::bad_alloc();
    memset(pData, 0, sizeof(Type));
    return (Type * )pData;
}
//--------------------------------------------------------------
template<class Type>
Type * AllocateNonPaged(int iAdditionalSize=0)
{
    void * pData = ExAllocatePool(NonPagedPool, sizeof(Type)+iAdditionalSize);
    if (!pData)
        throw std::bad_alloc();
    memset(pData, 0, sizeof(Type));
    return (Type * )pData;
}
//--------------------------------------------------------------

*/
