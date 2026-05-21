#pragma once
#include <atomic>
#include <iostream>
class SoftwareRiskGate {
public:
    SoftwareRiskGate(int max_pos) : max_position_(max_pos), current_position_(0) {}
    inline bool check_and_record_order(int size, bool side) {
        int cur = current_position_.load(std::memory_order_relaxed);
        int next = side ? (cur + size) : (cur - size);
        if (abs(next) > max_position_) return false;
        current_position_.store(next);
        return true;
    }
private:
    int max_position_;
    std::atomic<int> current_position_;
};
