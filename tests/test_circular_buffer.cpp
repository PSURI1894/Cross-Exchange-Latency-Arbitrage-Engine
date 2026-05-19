#include "circular_buffer.hpp"
#include <cassert>
#include <iostream>
int main() {
    CircularBuffer<int, 4> buf;
    assert(buf.push(10) == true);
    assert(buf.push(20) == true);
    int val = 0;
    assert(buf.pop(val) == true); assert(val == 10);
    std::cout << "[TEST] CircularBuffer passed!" << std::endl;
    return 0;
}
