// app.js
// Client-side execution engine for the HFT Latency Arbitrage Terminal.

let ws;
const wsUrl = "ws://127.0.0.1:8765";

// DOM References
const wsStatus = document.getElementById("wsStatus");
const statPnl = document.getElementById("statPnl");
const statTrades = document.getElementById("statTrades");
const statWinRate = document.getElementById("statWinRate");
const statPosition = document.getElementById("statPosition");

const fastPrice = document.getElementById("fastPrice");
const slowBid = document.getElementById("slowBid");
const slowAsk = document.getElementById("slowAsk");

const latencySlider = document.getElementById("latencySlider");
const lblLatency = document.getElementById("lblLatency");
const btnKill = document.getElementById("btnKill");
const btnReset = document.getElementById("btnReset");

const nodeNic = document.getElementById("nodeNic");
const nodeParser = document.getElementById("nodeParser");
const nodeComparator = document.getElementById("nodeComparator");
const nodeRisk = document.getElementById("nodeRisk");
const nodeOuch = document.getElementById("nodeOuch");
const pipelineStatus = document.getElementById("pipelineStatus");

const terminalLog = document.getElementById("terminalLog");

// Connect to WebSocket Server
function connect() {
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        wsStatus.textContent = "SERVER CONNECTED";
        wsStatus.className = "net-status connected";
        addLog("system", "Connected to simulated PCIe control plane.");
    };
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "init") {
            updateSystemState(msg.state);
        } else if (msg.type === "tick") {
            handleTickUpdate(msg);
        }
    };
    
    ws.onclose = () => {
        wsStatus.textContent = "SERVER DISCONNECTED";
        wsStatus.className = "net-status";
        addLog("warn", "WebSocket connection lost. Retrying in 2 seconds...");
        setTimeout(connect, 2000);
    };
}

// Update state configurations
function updateSystemState(state) {
    // P&L
    statPnl.textContent = (state.pnl >= 0 ? "+" : "") + "$" + state.pnl.toFixed(2);
    if (state.pnl > 0) {
        statPnl.className = "stat-val positive";
    } else if (state.pnl < 0) {
        statPnl.className = "stat-val negative";
    } else {
        statPnl.className = "stat-val";
    }
    
    // Trades
    statTrades.textContent = state.total_trades;
    
    // Win Rate
    const rate = state.total_trades > 0 ? (state.success_trades / state.total_trades * 100) : 0.0;
    statWinRate.textContent = rate.toFixed(1) + "%";
    
    // Position
    statPosition.textContent = state.current_position;
    if (state.current_position > 0) {
        statPosition.style.color = "var(--neon-green)";
    } else if (state.current_position < 0) {
        statPosition.style.color = "var(--neon-red)";
    } else {
        statPosition.style.color = "var(--text-primary)";
    }
    
    // Slider
    latencySlider.value = state.latency_ns;
    lblLatency.textContent = state.latency_ns + " ns";
    
    // Kill Switch
    if (state.kill_switch) {
        btnKill.textContent = "KILL SWITCH DETONATED";
        btnKill.classList.add("triggered");
    } else {
        btnKill.textContent = "ARM HARD KILL SWITCH";
        btnKill.classList.remove("triggered");
    }
}

// Handle tick payload update
function handleTickUpdate(tick) {
    // Update live quotes
    fastPrice.textContent = "$" + tick.fast_price.toFixed(2);
    slowBid.textContent = "$" + tick.slow_bid.toFixed(2);
    slowAsk.textContent = "$" + tick.slow_ask.toFixed(2);
    
    // Check if opportunity triggered
    if (tick.opportunity) {
        animatePipeline(tick);
    } else {
        pipelineStatus.textContent = "PIPELINE ACTIVE - WAITING FOR STALE QUOTE CROSS AT $" + tick.slow_ask.toFixed(2);
    }
    
    updateSystemState(tick.state);
}

// Sub-microsecond visual pipeline track animation
function animatePipeline(tick) {
    // Reset classes
    const nodes = [nodeNic, nodeParser, nodeComparator, nodeRisk, nodeOuch];
    nodes.forEach(n => {
        n.className = "pipeline-node";
    });
    
    // 1. NIC Ingestion
    nodeNic.className = "pipeline-node active";
    pipelineStatus.textContent = "NIC packet ingested. Handing off to ITCH Parser...";
    
    // 2. Parser
    setTimeout(() => {
        nodeParser.className = "pipeline-node active";
        pipelineStatus.textContent = `ITCH Parser decoded Stock ID AAPL (Price: $${tick.fast_price.toFixed(2)})`;
    }, 100);
    
    // 3. NBBO Comparator
    setTimeout(() => {
        nodeComparator.className = "pipeline-node active";
        pipelineStatus.textContent = `NBBO Comparator triggered: Fast Venue price crossed Slow ${tick.trade_side === "BUY" ? "Ask" : "Bid"}`;
    }, 200);
    
    // 4. Hardware Risk Gate check
    setTimeout(() => {
        if (tick.state.risk_breached || tick.state.kill_switch) {
            nodeRisk.className = "pipeline-node active error";
            pipelineStatus.textContent = `RISK REJECTED: ${tick.details}`;
            addLog("warn", `[RiskGate] Execution Blocked: ${tick.details}`);
        } else {
            nodeRisk.className = "pipeline-node active success";
            pipelineStatus.textContent = "Risk validation complete. Dispatching OUCH Constructor...";
        }
    }, 300);
    
    // 5. OUCH Constructor & wire out
    setTimeout(() => {
        if (tick.state.risk_breached || tick.state.kill_switch) {
            return;
        }
        
        if (tick.details.includes("Win")) {
            nodeOuch.className = "pipeline-node active success";
            pipelineStatus.textContent = `OUCH Order Sent! SUCCESSFUL ARB opportunity filled (+${tick.trade_pnl >= 0 ? "" : ""}$${tick.trade_pnl.toFixed(2)})`;
            addLog("buy", `[Pipeline] SUCCESS: Bought slow venue stale quote. Filled edge +$${tick.trade_pnl.toFixed(2)}`);
        } else if (tick.details.includes("Loss")) {
            nodeOuch.className = "pipeline-node active error";
            pipelineStatus.textContent = `OUCH Order Sent! TOXIC adverse fill fill-back (-$${Math.abs(tick.trade_pnl).toFixed(2)})`;
            addLog("sell", `[Pipeline] SLIPPAGE: Beaten in race! Filled at toxic price. Loss: -$${Math.abs(tick.trade_pnl).toFixed(2)}`);
        } else {
            pipelineStatus.textContent = `Opportunity ignored: ${tick.details}`;
            addLog("system", `[Pipeline] Ignored: ${tick.details}`);
        }
    }, 400);
}

// Print entries to HFT terminal
function addLog(type, text) {
    const line = document.createElement("div");
    line.className = `log-line ${type}`;
    
    const timeStr = new Date().toLocaleTimeString("en-US", { hour12: false });
    line.textContent = `[${timeStr}] ${text}`;
    
    terminalLog.appendChild(line);
    terminalLog.scrollTop = terminalLog.scrollHeight;
    
    // Cap log lines to 30
    if (terminalLog.children.length > 30) {
        terminalLog.removeChild(terminalLog.firstChild);
    }
}

// Slider event listeners
latencySlider.addEventListener("input", (e) => {
    const val = e.target.value;
    lblLatency.textContent = val + " ns";
});

latencySlider.addEventListener("change", (e) => {
    const val = e.target.value;
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "set_latency", value: parseInt(val) }));
    }
});

// Kill Switch detonator
btnKill.addEventListener("click", () => {
    const isDetonated = btnKill.classList.contains("triggered");
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "toggle_kill", value: !isDetonated }));
    }
});

// Reset event
btnReset.addEventListener("click", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "reset" }));
    }
});

// Initialize
connect();
