#pragma once
#include "pcie_dma.hpp"
#include <string>
#include <unordered_map>
struct SymbolConfig {
    uint32_t id; std::string symbol; uint64_t bid; uint64_t ask; uint32_t threshold;
};
class ControlPlane {
public:
    ControlPlane(PCIeDMA& pcie);
    void load_nightly_config(const std::string& filepath);
    void update_threshold(const std::string& symbol, uint32_t threshold);
private:
    PCIeDMA& pcie_;
    std::unordered_map<std::string, SymbolConfig> symbol_db_;
};
