import numpy as np
class RaceSimulator:
    def __init__(self, lambda_cancel=0.05, latency_gap_ns=200):
        self.lambda_cancel = lambda_cancel
        self.latency_gap = latency_gap_ns
    def capture_probability(self, rank):
        if rank <= 0: return 0.0
        delta = (rank - 1) * self.latency_gap
        return (1.0 / rank) * np.exp(-self.lambda_cancel * (delta / 100.0))
if __name__ == '__main__':
    sim = RaceSimulator()
    print('Capture Probabilities per Rank:')
    for r in range(1, 6):
        print(f'  Rank {r}: {sim.capture_probability(r)*100:.2f}%')
