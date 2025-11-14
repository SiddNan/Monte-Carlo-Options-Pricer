"""
Heston stochastic volatility model for asset price simulation.
"""
import numpy as np
from typing import Optional


class HestonModel:
    """
    Heston stochastic volatility model.

    Asset price and variance follow coupled SDEs:
    dS_t = r*S_t*dt + sqrt(v_t)*S_t*dW_S_t
    dv_t = kappa*(theta - v_t)*dt + sigma_v*sqrt(v_t)*dW_v_t

    where correlation(dW_S, dW_v) = rho
    """

    def __init__(
        self,
        S0: float,
        r: float,
        T: float,
        q: float,
        v0: float,
        kappa: float,
        theta: float,
        sigma_v: float,
        rho: float
    ):
        """
        Initialize Heston model.

        Args:
            S0: Initial spot price
            r: Risk-free rate
            T: Time to maturity
            q: Dividend yield
            v0: Initial variance
            kappa: Mean reversion speed
            theta: Long-run variance
            sigma_v: Vol of vol
            rho: Correlation between asset and variance
        """
        self.S0 = S0
        self.r = r
        self.T = T
        self.q = q
        self.v0 = v0
        self.kappa = kappa
        self.theta = theta
        self.sigma_v = sigma_v
        self.rho = rho

    def generate_paths(
        self,
        n_paths: int,
        n_steps: int,
        seed: Optional[int] = None,
        scheme: str = 'euler'
    ) -> np.ndarray:
        """
        Generate asset price paths using Heston model.

        Args:
            n_paths: Number of paths to simulate
            n_steps: Number of time steps
            seed: Random seed for reproducibility
            scheme: Discretization scheme ('euler' or 'milstein')

        Returns:
            Array of paths, shape (n_paths, n_steps + 1)
        """
        if seed is not None:
            np.random.seed(seed)

        dt = self.T / n_steps

        # Initialize arrays
        S = np.zeros((n_paths, n_steps + 1))
        v = np.zeros((n_paths, n_steps + 1))

        S[:, 0] = self.S0
        v[:, 0] = self.v0

        # Generate correlated Brownian motions
        for t in range(n_steps):
            Z1 = np.random.standard_normal(n_paths)
            Z2 = np.random.standard_normal(n_paths)

            # Create correlated normals
            W_S = Z1
            W_v = self.rho * Z1 + np.sqrt(1 - self.rho**2) * Z2

            S_t = S[:, t]
            v_t = np.maximum(v[:, t], 0)

            if scheme == 'euler':
                # Euler-Maruyama
                v[:, t + 1] = (
                    v_t +
                    self.kappa * (self.theta - v_t) * dt +
                    self.sigma_v * np.sqrt(v_t * dt) * W_v
                )

                S[:, t + 1] = (
                    S_t * (
                        1 +
                        (self.r - self.q) * dt +
                        np.sqrt(v_t * dt) * W_S
                    )
                )

            elif scheme == 'milstein':
                # Milstein scheme
                v[:, t + 1] = (
                    v_t +
                    self.kappa * (self.theta - v_t) * dt +
                    self.sigma_v * np.sqrt(v_t * dt) * W_v +
                    0.25 * self.sigma_v**2 * dt * (W_v**2 - 1)
                )

                log_S_next = (
                    np.log(S_t) +
                    (self.r - self.q - 0.5 * v_t) * dt +
                    np.sqrt(v_t * dt) * W_S
                )
                S[:, t + 1] = np.exp(log_S_next)

            # Keep variance positive
            v[:, t + 1] = np.abs(v[:, t + 1])

        return S

    def __repr__(self) -> str:
        return (
            f"HestonModel(S0={self.S0}, r={self.r}, T={self.T}, "
            f"v0={self.v0}, kappa={self.kappa}, theta={self.theta})"
        )
