"""
Base abstract class for option payoffs.
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from ..core.enums import OptionType


class BasePayoff(ABC):
    """
    Abstract base class for option payoff structures.

    All payoff classes should inherit from this and implement the payoff method.
    """

    def __init__(self, option_type: OptionType, strike: float):
        """
        Initialize base payoff.

        Args:
            option_type: Call or Put
            strike: Strike price
        """
        self.option_type = option_type
        self.strike = strike

    @abstractmethod
    def payoff(self, paths: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Calculate payoff for given price paths.

        Args:
            paths: Array of simulated price paths, shape (n_paths, n_steps)
            *args, **kwargs: Additional arguments for specific payoff types

        Returns:
            Array of payoffs, shape (n_paths,)
        """
        pass

    def discounted_payoff(
        self,
        paths: np.ndarray,
        r: float,
        T: float,
        *args,
        **kwargs
    ) -> np.ndarray:
        """
        Calculate discounted payoff.

        Args:
            paths: Array of simulated price paths
            r: Risk-free rate
            T: Time to maturity
            *args, **kwargs: Additional arguments for specific payoff types

        Returns:
            Array of discounted payoffs
        """
        payoffs = self.payoff(paths, *args, **kwargs)
        return np.exp(-r * T) * payoffs

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.option_type.value}, strike={self.strike})"
