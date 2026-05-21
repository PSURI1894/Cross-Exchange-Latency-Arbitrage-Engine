# HFT Operational Deployment Runbook

## Emergency Kill-switch Procedure
Write 0x1 to MMIO register 0x30 to trigger FPGA hardware execution lock.

---

## Interactive Visual Simulation Suite (Phase 2)

### 1. Launch WebSocket Server
```bash
python python/sim_server.py
```
### 2. Launch UI Dashboard
Open `web/index.html` in any browser.
