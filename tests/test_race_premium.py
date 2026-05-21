import unittest
from python.race_simulator import RaceSimulator
class TestRacePremium(unittest.TestCase):
    def setUp(self):
        self.sim = RaceSimulator(lambda_cancel=0.01, latency_gap_ns=100)
    def test_rank_one(self):
        self.assertAlmostEqual(self.sim.capture_probability(1), 1.0)
if __name__ == '__main__':
    unittest.main()
