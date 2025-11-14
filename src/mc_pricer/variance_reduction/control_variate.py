"""
Control variate variance reduction technique.
"""
import numpy as np
from typing import Tuple
from ..payoffs.base import BasePayoff


class ControlVariate:
    """
    Control variate variance reduction method.

    Uses a correlated variable with known expectation to reduce variance.
    """

    def __init__(self, control_payoff: BasePayoff, control_price: float):
        """
        Initialize control variate.

        Args:
            control_payoff: Payoff with known analytical price
            control_price: Known analytical price of control
        """
        self.control_payoff = control_payoff
        self.control_price = control_price

    def apply(
        self,
        payoff: BasePayoff,
        paths: np.ndarray,
        r: float,
        T: float
    ) -> Tuple[float, float]:
        """
        Apply control variate variance reduction.

        Args:
            payoff: Target option payoff
            paths: Simulated price paths
            r: Risk-free rate
            T: Time to maturity

        Returns:
            Tuple of (adjusted_price, adjusted_std_error)
        """
        # Calculate payoffs
        target_payoffs = payoff.discounted_payoff(paths, r, T)
        control_payoffs = self.control_payoff.discounted_payoff(paths, r, T)

        # MC price for control
        control_mc_price = np.mean(control_payoffs)

        # Calculate optimal coefficient
        cov = np.cov(target_payoffs, control_payoffs)[0, 1]
        var_control = np.var(control_payoffs)

        if var_control > 0:
            c = -cov / var_control
        else:
            c = 0

        # Apply adjustment
        adjusted_payoffs = target_payoffs + c * (self.control_price - control_payoffs)

        adjusted_price = np.mean(adjusted_payoffs)
        adjusted_std_error = np.std(adjusted_payoffs) / np.sqrt(len(adjusted_payoffs))

        return adjusted_price, adjusted_std_error

    def __repr__(self) -> str:
        return f"ControlVariate(control={self.control_payoff}, price={self.control_price:.4f})"
