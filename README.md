# Cross-Exchange Latency Arbitrage Engine

An ultra-low-latency, sub-microsecond cross-venue latency arbitrage trading engine.

Features a hybrid **FPGA (hot path)** Verilog pipeline and a **C++ (control plane)** co-simulated with **Verilator**, backed by a **Python research suite** and a live **interactive visual dashboard**.

## Target Latency Budget (< 1μs)
- NIC PHY in: 50ns
- Kernel Bypass (Solarflare EF_VI): 200ns
- FPGA Parser & NBBO Decoder: 100ns
- FPGA Decision Threshold Logic: 200ns
- FPGA OUCH Order Constructor: 100ns
- NIC PHY out: 50ns
- Total Tick-to-Trade Path: 700ns
