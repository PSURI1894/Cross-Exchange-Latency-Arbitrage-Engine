# Mathematical Framework & Engineering Specs

## Mathematical Formulation
For two venues $A$ (fast) and $B$ (slow), latency arbitrage opportunities exist when:
$$|P^A_t - P^B_t| > spread^B + cost + race\_premium$$

Where:
- $P^A_t$: Fast-venue quote.
- $P^B_t$: Slow-venue quote.
- $spread^B$: Bid-Ask spread on the slow venue.
- $cost$: Clearing, exchange fees, and borrow costs.
- $race\_premium$: Probability-weighted penalty for competing in the HFT race.

### Race Premium and Rank Decay
The probability of capturing a race for the $N$-th fastest participant is modeled by:
$$P_{capture}(N) \approx \frac{1}{N} e^{-\lambda_{competitor} \Delta_N}$$

Where:
- $\Delta_N$ is the latency gap between rank $N$ and the winner.
- $\lambda_{competitor}$ is the arrival rate of competing cancels and orders.
