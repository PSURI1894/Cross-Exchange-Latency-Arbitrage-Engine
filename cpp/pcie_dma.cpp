#include "pcie_dma.hpp"
#include <atomic>
#include <iostream>
PCIeDMA::PCIeDMA() {
    regs_.cfg_stock_id = 0; regs_.slow_venue_bid = 0; regs_.slow_venue_ask = 0;
    regs_.cfg_threshold = 0; regs_.cfg_max_pos = 0; regs_.cfg_max_loss = 0;
    regs_.hardware_kill_switch = 0; regs_.risk_breached = 0;
}
void PCIeDMA::write_mmio_reg(uint32_t offset, uint64_t val) {
    std::atomic_thread_fence(std::memory_order_release);
    switch(offset) {
        case 0x00: regs_.cfg_stock_id = val; break;
        case 0x08: regs_.slow_venue_bid = val; break;
        case 0x10: regs_.slow_venue_ask = val; break;
        case 0x18: regs_.cfg_threshold = val; break;
        case 0x20: regs_.cfg_max_pos = val; break;
        case 0x28: regs_.cfg_max_loss = val; break;
        case 0x30: regs_.hardware_kill_switch = val; break;
    }
}
uint64_t PCIeDMA::read_mmio_reg(uint32_t offset) {
    uint64_t val = 0;
    switch(offset) {
        case 0x00: val = regs_.cfg_stock_id; break;
        case 0x08: val = regs_.slow_venue_bid; break;
        case 0x10: val = regs_.slow_venue_ask; break;
        case 0x18: val = regs_.cfg_threshold; break;
        case 0x20: val = regs_.cfg_max_pos; break;
        case 0x28: val = regs_.cfg_max_loss; break;
        case 0x30: val = regs_.hardware_kill_switch; break;
        case 0x38: val = regs_.risk_breached; break;
    }
    std::atomic_thread_fence(std::memory_order_acquire);
    return val;
}
