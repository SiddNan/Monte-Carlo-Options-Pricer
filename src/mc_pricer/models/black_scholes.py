"""
Black-Scholes (Geometric Brownian Motion) model for asset price simulation.
"""
import numpy as np
from typing import Optional
from scipy.stats import qmc


class BlackScholesModel:
    """
    Geometric Brownian Motion model for asset price paths.

    dS_t = (r - q)*S_t*dt + sigma*S_t*dW_t

    where:
    - r: risk-free rate
    - q: dividend yield
    - sigma: volatility
    - W_t: Wiener process
    """

    def __init__(
        self,
        S0: float,
        r: float,
        sigma: float,
        T: float,
        q: float = 0.0
    ):
        """
        Initialize Black-Scholes model.

        Args:
            S0: Initial spot price
            r: Risk-free rate
            sigma: Volatility
            T: Time to maturity
            q: Dividend yield
        """
        self.S0 = S0
        self.r = r
        self.sigma = sigma
        self.T = T
        self.q = q

    def generate_paths(
        self,
        n_paths: int,
        n_steps: int,
        seed: Optional[int] = None,
        antithetic: bool = False,
        use_sobol: bool = False
    ) -> np.ndarray:
        """
        Generate asset price paths using geometric Brownian motion.

        Args:
            n_paths: Number of paths to simulate
            n_steps: Number of time steps
            seed: Random seed for reproducibility
            antithetic: Use antithetic variates
            use_sobol: Use Sobol quasi-random sequences

        Returns:
            Array of paths, shape (n_paths, n_steps + 1)
        """
        if seed is not None:
            np.random.seed(seed)

        dt = self.T / n_steps

        # Generate random numbers
        if use_sobol:
            paths_to_generate = n_paths // 2 if antithetic else n_paths
            Z = self._generate_sobol(paths_to_generate, n_steps)
        else:
            paths_to_generate = n_paths // 2 if antithetic else n_paths
            Z = np.random.standard_normal((paths_to_generate, n_steps))

        # Apply antithetic variates
        if antithetic:
            Z = np.vstack([Z, -Z])

        # Pre-compute drift and diffusion terms for GBM
        # Drift includes Ito correction: mu - 0.5*sigma^2
        drift = (self.r - self.q - 0.5 * self.sigma ** 2) * dt
        diffusion = self.sigma * np.sqrt(dt)

        # Generate log returns: dlog(S) = drift*dt + sigma*dW
        log_returns = drift + diffusion * Z

        # Cumulative sum gives log(S_t/S_0) for vectorized efficiency
        log_prices = np.cumsum(log_returns, axis=1)

        # Initialize paths
        paths = np.zeros((n_paths, n_steps + 1))
        paths[:, 0] = self.S0
        paths[:, 1:] = self.S0 * np.exp(log_prices)

        return paths

    def _generate_sobol(self, n_paths: int, n_steps: int) -> np.ndarray:
        """
        Generate Sobol quasi-random sequences.

        Args:
            n_paths: Number of paths
            n_steps: Number of time steps

        Returns:
            Array of shape (n_paths, n_steps) with standard normal samples
        """
        sampler = qmc.Sobol(d=n_steps, scramble=True)
        uniform_samples = sampler.random(n_paths)

        from scipy.stats import norm
        Z = norm.ppf(uniform_samples)

        return Z

    def __repr__(self) -> str:
        return (
            f"BlackScholesModel(S0={self.S0}, r={self.r}, "
            f"sigma={self.sigma}, T={self.T}, q={self.q})"
        )
