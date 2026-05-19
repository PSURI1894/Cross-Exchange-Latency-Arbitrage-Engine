// circular_buffer.hpp
#pragma once
#include <atomic>
#include <cstddef>
template <typename T, size_t Capacity>
class CircularBuffer {
public:
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2");
    CircularBuffer() : head_(0), tail_(0) {}
    bool push(const T& val) {
        size_t current_tail = tail_.load(std::memory_order_relaxed);
        size_t current_head = head_.load(std::memory_order_acquire);
        if ((current_tail - current_head) >= Capacity) return false;
        buffer_[current_tail & (Capacity - 1)] = val;
        tail_.store(current_tail + 1, std::memory_order_release);
        return true;
    }
    bool pop(T& val) {
        size_t current_head = head_.load(std::memory_order_relaxed);
        size_t current_tail = tail_.load(std::memory_order_acquire);
        if (current_head == current_tail) return false;
        val = buffer_[current_head & (Capacity - 1)];
        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }
private:
    alignas(64) T buffer_[Capacity];
    alignas(64) std::atomic<size_t> head_;
    alignas(64) std::atomic<size_t> tail_;
};
