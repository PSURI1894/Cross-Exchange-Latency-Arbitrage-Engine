#include "solarflare_mock.hpp"
#include <iostream>
SolarflareBypass::SolarflareBypass() {}
SolarflareBypass::~SolarflareBypass() {}
bool SolarflareBypass::init() {
    std::cout << "[EF_VI] Driver bypass setup at root." << std::endl;
    return true;
}
int SolarflareBypass::poll_rx(uint8_t* buffer, int max_len) { return 0; }
void SolarflareBypass::transmit(const uint8_t* data, int len) {}
