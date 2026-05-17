#include <iostream>
#include "pcie_dma.hpp"
#include "control_plane.hpp"
#include "solarflare_mock.hpp"
int main() {
    std::cout << "============= LATENCY ARBITRAGE SIMULATION ============\" << std::endl;
    PCIeDMA pcie;
    ControlPlane control(pcie);
    SolarflareBypass bypass;
    bypass.init();
    control.load_nightly_config("nightly_symbols.json");
    std::cout << "[SIM] Co-simulation complete." << std::endl;
    return 0;
}
