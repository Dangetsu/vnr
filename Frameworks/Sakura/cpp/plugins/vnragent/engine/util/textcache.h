#pragma once

// textcache.h
// 8/30/2015 jichi

#include <cstdint>
#include <list>

// A simple but very inefficient implementation for LRU cache.
class TextHashCache
{
  int capacity_;
  std::list<uint64_t> hashes_;
public:
  explicit TextHashCache(int capacity) : capacity_(capacity) {}

  bool contains(uint64_t h) const
  { return std::find(hashes_.begin(), hashes_.end(), h) != hashes_.end(); }

  void add(uint64_t h)
  {
    if (hashes_.size() == capacity_)
      hashes_.pop_back();
    hashes_.push_front(h);
  }

};

// EOF
