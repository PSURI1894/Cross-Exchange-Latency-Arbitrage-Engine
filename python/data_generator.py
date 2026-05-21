import numpy as np
def generate_hft_market_data(num_ticks=1000):
    np.random.seed(1337)
    price_fast = 150.0 + np.cumsum(np.random.choice([-0.05, 0.0, 0.05], size=num_ticks))
    price_slow = np.zeros(num_ticks)
    for i in range(2, num_ticks): price_slow[i] = price_fast[i-2] + np.random.normal(0, 0.002)
    return price_fast, price_slow
if __name__ == '__main__':
    a, b = generate_hft_market_data(5)
    print('AAPL:', a)
