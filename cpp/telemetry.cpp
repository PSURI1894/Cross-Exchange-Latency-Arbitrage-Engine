#include "telemetry.hpp"
#include <iostream>
double LatencyStats::get_avg_latency() const {
    if (total_trades == 0) return 0.0;
    return (double)total_nanoseconds / total_trades;
}
void LatencyTelemetry::record_trade(uint64_t latency_ns) {
    stats_.total_ticks++; stats_.total_trades++; stats_.total_nanoseconds += latency_ns;
}
void LatencyTelemetry::dump_report() const {
    std::cout << "Average: " << stats_.get_avg_latency() << " ns" << std::endl;
}
