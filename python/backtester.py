import numpy as np
class LatencyArbBacktester:
    def __init__(self, latency_gap_ns=700, spread_b=0.01, clearing_fee=0.001):
        self.latency_gap = latency_gap_ns
        self.spread_b = spread_b
        self.clearing_fee = clearing_fee
    def run(self, price_series_a, price_series_b):
        pnl = 0.0
        trades = []
        for idx in range(1, len(price_series_a)):
            price_a = price_series_a[idx]
            price_b = price_series_b[idx]
            diff = abs(price_a - price_b)
            req_diff = self.spread_b + self.clearing_fee
            if diff > req_diff:
                if price_a > price_b:
                    pnl += (price_a - price_b) - req_diff
                    trades.append(("BUY_B_SELL_A", price_b, price_a))
                else:
                    pnl += (price_b - price_a) - req_diff
                    trades.append(("BUY_A_SELL_B", price_a, price_b))
        return pnl, trades
