#pragma once
#include <cstdint>
#include <vector>
class SolarflareBypass {
public:
    SolarflareBypass();
    ~SolarflareBypass();
    bool init();
    int poll_rx(uint8_t* buffer, int max_len);
    void transmit(const uint8_t* data, int len);
};
