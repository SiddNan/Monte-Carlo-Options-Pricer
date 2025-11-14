"""
European option payoffs with analytical pricing for benchmarking.
"""
import numpy as np
from scipy.stats import norm
from typing import Optional
from .base import BasePayoff
from ..core.enums import OptionType


class EuropeanOption(BasePayoff):
    """
    European call or put option.

    Payoff at maturity:
    - Call: max(S_T - K, 0)
    - Put: max(K - S_T, 0)
    """

    def payoff(self, paths: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Calculate European option payoff.

        Args:
            paths: Array of simulated price paths, shape (n_paths, n_steps)
                   Only the final price (paths[:, -1]) is used.

        Returns:
            Array of payoffs, shape (n_paths,)
        """
        # European option only depends on terminal price
        terminal_prices = paths[:, -1] if paths.ndim > 1 else paths

        if self.option_type == OptionType.CALL:
            return np.maximum(terminal_prices - self.strike, 0)
        else:  # PUT
            return np.maximum(self.strike - terminal_prices, 0)

    @staticmethod
    def black_scholes_price(
        S0: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: OptionType,
        q: float = 0.0
    ) -> float:
        """
        Analytical Black-Scholes price for European options.

        Args:
            S0: Initial spot price
            K: Strike price
            T: Time to maturity
            r: Risk-free rate
            sigma: Volatility
            option_type: Call or Put
            q: Dividend yield

        Returns:
            Analytical option price
        """
        d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == OptionType.CALL:
            price = S0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:  # PUT
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S0 * np.exp(-q * T) * norm.cdf(-d1)

        return price

    @staticmethod
    def black_scholes_delta(
        S0: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: OptionType,
        q: float = 0.0
    ) -> float:
        """
        Analytical delta for European options.

        Args:
            S0: Initial spot price
            K: Strike price
            T: Time to maturity
            r: Risk-free rate
            sigma: Volatility
            option_type: Call or Put
            q: Dividend yield

        Returns:
            Delta (dV/dS)
        """
        d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

        if option_type == OptionType.CALL:
            return np.exp(-q * T) * norm.cdf(d1)
        else:  # PUT
            return -np.exp(-q * T) * norm.cdf(-d1)

    @staticmethod
    def black_scholes_gamma(
        S0: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float = 0.0
    ) -> float:
        """
        Analytical gamma for European options (same for calls and puts).

        Args:
            S0: Initial spot price
            K: Strike price
            T: Time to maturity
            r: Risk-free rate
            sigma: Volatility
            q: Dividend yield

        Returns:
            Gamma (d2V/dS2)
        """
        d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        return np.exp(-q * T) * norm.pdf(d1) / (S0 * sigma * np.sqrt(T))

    @staticmethod
    def black_scholes_vega(
        S0: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float = 0.0
    ) -> float:
        """
        Analytical vega for European options (same for calls and puts).

        Args:
            S0: Initial spot price
            K: Strike price
            T: Time to maturity
            r: Risk-free rate
            sigma: Volatility
            q: Dividend yield

        Returns:
            Vega (dV/dsigma) / 100 (for 1% change in volatility)
        """
        d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        return S0 * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T) / 100

    @staticmethod
    def black_scholes_theta(
        S0: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: OptionType,
        q: float = 0.0
    ) -> float:
        """
        Analytical theta for European options.

        Args:
            S0: Initial spot price
            K: Strike price
            T: Time to maturity
            r: Risk-free rate
            sigma: Volatility
            option_type: Call or Put
            q: Dividend yield

        Returns:
            Theta (dV/dt) per day (divide by 365)
        """
        d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        term1 = -S0 * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T))

        if option_type == OptionType.CALL:
            term2 = q * S0 * np.exp(-q * T) * norm.cdf(d1)
            term3 = -r * K * np.exp(-r * T) * norm.cdf(d2)
        else:  # PUT
            term2 = -q * S0 * np.exp(-q * T) * norm.cdf(-d1)
            term3 = r * K * np.exp(-r * T) * norm.cdf(-d2)

        return (term1 + term2 + term3) / 365

    @staticmethod
    def black_scholes_rho(
        S0: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: OptionType,
        q: float = 0.0
    ) -> float:
        """
        Analytical rho for European options.

        Args:
            S0: Initial spot price
            K: Strike price
            T: Time to maturity
            r: Risk-free rate
            sigma: Volatility
            option_type: Call or Put
            q: Dividend yield

        Returns:
            Rho (dV/dr) / 100 (for 1% change in rate)
        """
        d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == OptionType.CALL:
            return K * T * np.exp(-r * T) * norm.cdf(d2) / 100
        else:  # PUT
            return -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
