#include "control_plane.hpp"
#include <iostream>
ControlPlane::ControlPlane(PCIeDMA& pcie) : pcie_(pcie) {}
void ControlPlane::load_nightly_config(const std::string& filepath) {
    std::cout << "[ControlPlane] Loading nightly symbol parameters..." << std::endl;
    SymbolConfig aapl{42, "AAPL", 1500000, 1501000, 10};
    symbol_db_["AAPL"] = aapl;
    pcie_.write_mmio_reg(0x00, aapl.id);
    pcie_.write_mmio_reg(0x08, aapl.bid);
    pcie_.write_mmio_reg(0x10, aapl.ask);
    pcie_.write_mmio_reg(0x18, aapl.threshold);
    pcie_.write_mmio_reg(0x20, 10000);
}
void ControlPlane::update_threshold(const std::string& symbol, uint32_t threshold) {
    auto it = symbol_db_.find(symbol);
    if (it != symbol_db_.end()) {
        it->second.threshold = threshold;
        pcie_.write_mmio_reg(0x18, threshold);
    }
}
