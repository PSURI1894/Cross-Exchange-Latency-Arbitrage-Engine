# sim_server.py (Zero-dependency WebSocket Server)
# Fully detailed, low-latency, zero-pip-dependency WebSocket simulator.
# sim_server.py
# Zero-dependency, low-latency WebSocket HFT Simulation Server.
# Implements RFC 6455 WebSocket handshakes and framing from scratch!

import socket
import hashlib
import base64
import json
import time
import threading
import random

HOST = "127.0.0.1"
PORT = 8765

# System States (Controlled via PCIe / WebSocket client)
system_state = {
    "latency_ns": 700,
    "max_position": 5000,
    "current_position": 0,
    "kill_switch": False,
    "cfg_threshold_ticks": 10,
    "clearing_fee_ticks": 2,
    "slow_venue_bid": 1500000, # $150.00 in ticks (10,000 per $)
    "slow_venue_ask": 1501000, # $150.10
    "pnl": 0.0,
    "total_trades": 0,
    "success_trades": 0,
    "risk_breached": False
}

clients = []
clients_lock = threading.Lock()

def make_handshake_response(key):
    guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    accept = base64.b64encode(hashlib.sha1((key + guid).encode()).digest()).decode()
    return (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
    )

def encode_frame(payload_str):
    payload = payload_str.encode("utf-8")
    payload_len = len(payload)
    
    header = bytearray()
    header.append(0x81) # FIN=1, Opcode=1 (Text)
    
    if payload_len < 126:
        header.append(payload_len)
    elif payload_len < 65536:
        header.append(126)
        header.extend(payload_len.to_bytes(2, byteorder='big'))
    else:
        header.append(127)
        header.extend(payload_len.to_bytes(8, byteorder='big'))
        
    return bytes(header + payload)

def decode_frame(data):
    if len(data) < 2:
        return None
    
    # second byte contains mask flag and length
    mask_flag = (data[1] & 0x80) != 0
    payload_len = data[1] & 0x7F
    
    offset = 2
    if payload_len == 126:
        payload_len = int.from_bytes(data[2:4], byteorder='big')
        offset = 4
    elif payload_len == 127:
        payload_len = int.from_bytes(data[2:10], byteorder='big')
        offset = 10
        
    if mask_flag:
        masking_key = data[offset:offset+4]
        offset += 4
        raw_payload = data[offset:offset+payload_len]
        # Unmask
        decoded = bytearray(len(raw_payload))
        for i in range(len(raw_payload)):
            decoded[i] = raw_payload[i] ^ masking_key[i % 4]
        return decoded.decode("utf-8")
    else:
        return data[offset:offset+payload_len].decode("utf-8")

def broadcast(payload_str):
    frame = encode_frame(payload_str)
    with clients_lock:
        to_remove = []
        for client in clients:
            try:
                client.sendall(frame)
            except Exception:
                to_remove.append(client)
        for client in to_remove:
            if client in clients:
                clients.remove(client)

def client_handler(conn, addr):
    print(f"[WebSocket] Connected to {addr}")
    try:
        # 1. Perform Handshake
        request = conn.recv(4096).decode("utf-8")
        headers = {}
        for line in request.split("\r\n")[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
                
        if "sec-websocket-key" not in headers:
            conn.close()
            return
            
        key = headers["sec-websocket-key"]
        response = make_handshake_response(key)
        conn.sendall(response.encode())
        
        with clients_lock:
            clients.append(conn)
            
        # Send initial config status
        conn.sendall(encode_frame(json.dumps({"type": "init", "state": system_state})))
        
        # 2. Main socket read loop
        while True:
            raw_data = conn.recv(4096)
            if not raw_data:
                break
            
            message = decode_frame(raw_data)
            if message:
                try:
                    payload = json.loads(message)
                    handle_client_payload(payload)
                except Exception as e:
                    print(f"[WebSocket] Error parsing message: {e}")
                    
    except Exception as e:
        print(f"[WebSocket] Client disconnected with error: {e}")
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[WebSocket] Disconnected from {addr}")

def handle_client_payload(payload):
    global system_state
    cmd_type = payload.get("type")
    
    if cmd_type == "set_latency":
        system_state["latency_ns"] = int(payload.get("value", 700))
        print(f"[ControlPlane] Latency budget updated to {system_state['latency_ns']} ns.")
        
    elif cmd_type == "toggle_kill":
        system_state["kill_switch"] = bool(payload.get("value", False))
        print(f"[RiskGate] Hard Kill Switch state updated: {system_state['kill_switch']}.")
        if system_state["kill_switch"]:
            system_state["risk_breached"] = True
            
    elif cmd_type == "reset":
        system_state["pnl"] = 0.0
        system_state["total_trades"] = 0
        system_state["success_trades"] = 0
        system_state["current_position"] = 0
        system_state["risk_breached"] = False
        system_state["kill_switch"] = False
        print("[ControlPlane] Live engine parameters reset.")

def run_market_data_simulation():
    global system_state
    
    stock_price = 150.00
    
    while True:
        time.sleep(0.4) # ticks every 400ms
        
        if len(clients) == 0:
            continue
            
        # Simulate price jump on Fast Venue (NASDAQ)
        change = random.choice([-0.05, 0.0, 0.05])
        if change == 0.0:
            continue
            
        stock_price = round(stock_price + change, 2)
        fast_price_ticks = int(stock_price * 10000)
        
        # Slow Venue (ARCA) stale price
        slow_bid = system_state["slow_venue_bid"]
        slow_ask = system_state["slow_venue_ask"]
        
        # Latency Race logic
        my_latency = system_state["latency_ns"]
        
        # Competing firms latency model
        # Winner is usually sub-500ns. Our rank is based on my_latency.
        if my_latency < 400:
            my_rank = 1
        elif my_latency < 600:
            my_rank = 2
        elif my_latency < 1000:
            my_rank = 3
        elif my_latency < 2000:
            my_rank = 5
        else:
            my_rank = 12
            
        # Win probability P = (1/N) * e^(-lambda * delta)
        lambda_competitor = 0.02
        delta = max(0, (my_rank - 1) * 200)
        win_prob = (1.0 / my_rank) * (2.71828 ** (-lambda_competitor * (delta / 10)))
        
        opportunity_triggered = False
        trade_side = "HOLD"
        trade_pnl = 0.0
        details = ""
        
        # Buying Slow Venue (Fast moves UP above slow ask)
        if change > 0 and fast_price_ticks > slow_ask:
            opportunity_triggered = True
            trade_side = "BUY"
            edge = fast_price_ticks - slow_ask
            req_edge = system_state["cfg_threshold_ticks"] + system_state["clearing_fee_ticks"]
            
            if system_state["kill_switch"] or system_state["risk_breached"]:
                details = "Risk Breached: Order Blocked"
            elif abs(system_state["current_position"] + 100) > system_state["max_position"]:
                system_state["risk_breached"] = True
                details = "Risk Breach: Max Position Exceeded"
            elif edge > req_edge:
                # We compete in the race
                if random.random() < win_prob:
                    trade_pnl = round((edge - system_state["clearing_fee_ticks"]) / 10000.0 * 100, 2)
                    system_state["pnl"] = round(system_state["pnl"] + trade_pnl, 2)
                    system_state["current_position"] += 100
                    system_state["total_trades"] += 1
                    system_state["success_trades"] += 1
                    details = f"Race Win (Rank {my_rank})! Filled at stale ask."
                else:
                    # Adverse selection: we got beat, filled at toxic price
                    trade_pnl = -round((edge + 10) / 10000.0 * 100, 2)
                    system_state["pnl"] = round(system_state["pnl"] + trade_pnl, 2)
                    system_state["current_position"] += 100
                    system_state["total_trades"] += 1
                    details = f"Race Loss (Rank {my_rank})! Toxic fill fill-back."
            else:
                details = "Opportunity ignored: insufficient edge"
                
        # Selling Slow Venue (Fast moves DOWN below slow bid)
        elif change < 0 and fast_price_ticks < slow_bid:
            opportunity_triggered = True
            trade_side = "SELL"
            edge = slow_bid - fast_price_ticks
            req_edge = system_state["cfg_threshold_ticks"] + system_state["clearing_fee_ticks"]
            
            if system_state["kill_switch"] or system_state["risk_breached"]:
                details = "Risk Breached: Order Blocked"
            elif abs(system_state["current_position"] - 100) > system_state["max_position"]:
                system_state["risk_breached"] = True
                details = "Risk Breach: Max Position Exceeded"
            elif edge > req_edge:
                if random.random() < win_prob:
                    trade_pnl = round((edge - system_state["clearing_fee_ticks"]) / 10000.0 * 100, 2)
                    system_state["pnl"] = round(system_state["pnl"] + trade_pnl, 2)
                    system_state["current_position"] -= 100
                    system_state["total_trades"] += 1
                    system_state["success_trades"] += 1
                    details = f"Race Win (Rank {my_rank})! Stale bid hit successfully."
                else:
                    trade_pnl = -round((edge + 10) / 10000.0 * 100, 2)
                    system_state["pnl"] = round(system_state["pnl"] + trade_pnl, 2)
                    system_state["current_position"] -= 100
                    system_state["total_trades"] += 1
                    details = f"Race Loss (Rank {my_rank})! Adverse filled."
            else:
                details = "Opportunity ignored: insufficient edge"
                
        # Update Slow Venue stale quote (Slow venue catches up shortly after)
        system_state["slow_venue_bid"] = fast_price_ticks - 500
        system_state["slow_venue_ask"] = fast_price_ticks + 500
        
        # Broadcast update to web clients
        update_msg = {
            "type": "tick",
            "timestamp": time.time() * 1000,
            "fast_price": stock_price,
            "slow_bid": round(system_state["slow_venue_bid"] / 10000.0, 2),
            "slow_ask": round(system_state["slow_venue_ask"] / 10000.0, 2),
            "opportunity": opportunity_triggered,
            "trade_side": trade_side,
            "trade_pnl": trade_pnl,
            "win_prob": round(win_prob * 100, 1),
            "details": details,
            "state": system_state
        }
        broadcast(json.dumps(update_msg))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[WebSocket] HFT Live Simulation Server active on ws://{HOST}:{PORT}")
    
    # Start background market simulator thread
    sim_thread = threading.Thread(target=run_market_data_simulation, daemon=True)
    sim_thread.start()
    
    while True:
        try:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)
            client_thread.start()
        except KeyboardInterrupt:
            break
    server.close()

if __name__ == "__main__":
    start_server()
