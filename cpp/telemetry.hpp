#pragma once
#include <cstdint>
struct LatencyStats {
    uint64_t total_ticks; uint64_t total_trades; uint64_t total_nanoseconds;
    double get_avg_latency() const;
};
class LatencyTelemetry {
public:
    void record_trade(uint64_t latency_ns);
    void dump_report() const;
private:
    LatencyStats stats_ = {0, 0, 0};
};
