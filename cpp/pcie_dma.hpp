#pragma once
#include <cstdint>
struct FPGARegisters {
    uint32_t cfg_stock_id;
    uint64_t slow_venue_bid;
    uint64_t slow_venue_ask;
    uint32_t cfg_threshold;
    uint32_t cfg_max_pos;
    uint32_t cfg_max_loss;
    uint32_t hardware_kill_switch;
    uint32_t risk_breached;
};
class PCIeDMA {
public:
    PCIeDMA();
    void write_mmio_reg(uint32_t offset, uint64_t val);
    uint64_t read_mmio_reg(uint32_t offset);
private:
    FPGARegisters regs_;
};
