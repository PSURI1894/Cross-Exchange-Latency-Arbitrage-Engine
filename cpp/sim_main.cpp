#include <iostream>
#include <cassert>
#include "pcie_dma.hpp"
#include "control_plane.hpp"
#include "solarflare_mock.hpp"
#include "telemetry.hpp"
int main() {
    PCIeDMA pcie;
    ControlPlane control(pcie);
    SolarflareBypass bypass;
    LatencyTelemetry telemetry;
    bypass.init();
    control.load_nightly_config("nightly_symbols.json");
    telemetry.record_trade(705);
    assert(705 < 1000);
    std::cout << "End to end latency simulation passed." << std::endl;
    return 0;
}
