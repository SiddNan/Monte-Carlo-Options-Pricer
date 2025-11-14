"""
Exotic option payoffs (Asian, Barrier, Lookback, Digital).
"""
import numpy as np
from typing import Optional
from .base import BasePayoff
from ..core.enums import OptionType, ExoticType


class AsianOption(BasePayoff):
    """
    Asian option with arithmetic or geometric averaging.

    Payoff depends on the average price over the option's life:
    - Call: max(Avg(S) - K, 0)
    - Put: max(K - Avg(S), 0)
    """

    def __init__(
        self,
        option_type: OptionType,
        strike: float,
        averaging: ExoticType = ExoticType.ASIAN_ARITHMETIC
    ):
        """
        Initialize Asian option.

        Args:
            option_type: Call or Put
            strike: Strike price
            averaging: Arithmetic or geometric averaging
        """
        super().__init__(option_type, strike)
        if averaging not in [ExoticType.ASIAN_ARITHMETIC, ExoticType.ASIAN_GEOMETRIC]:
            raise ValueError(f"Invalid averaging type for Asian option: {averaging}")
        self.averaging = averaging

    def payoff(self, paths: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Calculate Asian option payoff based on path average.

        Args:
            paths: Array of simulated price paths, shape (n_paths, n_steps)

        Returns:
            Array of payoffs, shape (n_paths,)
        """
        if self.averaging == ExoticType.ASIAN_ARITHMETIC:
            avg_price = np.mean(paths, axis=1)
        else:  # Geometric
            # Geometric mean: exp(mean(log(S)))
            avg_price = np.exp(np.mean(np.log(paths), axis=1))

        if self.option_type == OptionType.CALL:
            return np.maximum(avg_price - self.strike, 0)
        else:  # PUT
            return np.maximum(self.strike - avg_price, 0)


class BarrierOption(BasePayoff):
    """
    Barrier option (knock-out or knock-in).

    Option is activated or deactivated when price crosses barrier level.
    Types: Up-and-Out, Down-and-Out, Up-and-In, Down-and-In
    """

    def __init__(
        self,
        option_type: OptionType,
        strike: float,
        barrier: float,
        barrier_type: ExoticType,
        rebate: float = 0.0
    ):
        """
        Initialize barrier option.

        Args:
            option_type: Call or Put
            strike: Strike price
            barrier: Barrier level
            barrier_type: Type of barrier (up/down, in/out)
            rebate: Payment if barrier is breached (for knock-out)
        """
        super().__init__(option_type, strike)
        valid_barriers = [
            ExoticType.BARRIER_UP_OUT,
            ExoticType.BARRIER_DOWN_OUT,
            ExoticType.BARRIER_UP_IN,
            ExoticType.BARRIER_DOWN_IN
        ]
        if barrier_type not in valid_barriers:
            raise ValueError(f"Invalid barrier type: {barrier_type}")

        self.barrier = barrier
        self.barrier_type = barrier_type
        self.rebate = rebate

    def payoff(self, paths: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Calculate barrier option payoff.

        Args:
            paths: Array of simulated price paths, shape (n_paths, n_steps)

        Returns:
            Array of payoffs, shape (n_paths,)
        """
        terminal_prices = paths[:, -1]

        # Calculate standard European payoff
        if self.option_type == OptionType.CALL:
            european_payoff = np.maximum(terminal_prices - self.strike, 0)
        else:  # PUT
            european_payoff = np.maximum(self.strike - terminal_prices, 0)

        # Check barrier breach along each path
        if self.barrier_type == ExoticType.BARRIER_UP_OUT:
            # Knocked out if price goes above barrier
            barrier_breached = np.any(paths >= self.barrier, axis=1)
            payoff = np.where(barrier_breached, self.rebate, european_payoff)

        elif self.barrier_type == ExoticType.BARRIER_DOWN_OUT:
            # Knocked out if price goes below barrier
            barrier_breached = np.any(paths <= self.barrier, axis=1)
            payoff = np.where(barrier_breached, self.rebate, european_payoff)

        elif self.barrier_type == ExoticType.BARRIER_UP_IN:
            # Knocked in if price goes above barrier
            barrier_breached = np.any(paths >= self.barrier, axis=1)
            payoff = np.where(barrier_breached, european_payoff, self.rebate)

        elif self.barrier_type == ExoticType.BARRIER_DOWN_IN:
            # Knocked in if price goes below barrier
            barrier_breached = np.any(paths <= self.barrier, axis=1)
            payoff = np.where(barrier_breached, european_payoff, self.rebate)

        return payoff


class LookbackOption(BasePayoff):
    """
    Lookback option with payoff based on maximum or minimum price.

    - Lookback Call (floating strike): S_T - min(S)
    - Lookback Put (floating strike): max(S) - S_T
    - Lookback Call (fixed strike): max(max(S) - K, 0)
    - Lookback Put (fixed strike): max(K - min(S), 0)
    """

    def __init__(
        self,
        option_type: OptionType,
        strike: Optional[float] = None,
        lookback_type: ExoticType = ExoticType.LOOKBACK_FLOATING
    ):
        """
        Initialize lookback option.

        Args:
            option_type: Call or Put
            strike: Strike price (None for floating, value for fixed)
            lookback_type: Floating or fixed strike
        """
        # For floating strike, strike can be None
        super().__init__(option_type, strike if strike is not None else 0.0)

        if lookback_type not in [ExoticType.LOOKBACK_FIXED, ExoticType.LOOKBACK_FLOATING]:
            raise ValueError(f"Invalid lookback type: {lookback_type}")

        self.lookback_type = lookback_type

        if lookback_type == ExoticType.LOOKBACK_FIXED and strike is None:
            raise ValueError("Fixed strike lookback requires strike price")

    def payoff(self, paths: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Calculate lookback option payoff.

        Args:
            paths: Array of simulated price paths, shape (n_paths, n_steps)

        Returns:
            Array of payoffs, shape (n_paths,)
        """
        max_prices = np.max(paths, axis=1)
        min_prices = np.min(paths, axis=1)
        terminal_prices = paths[:, -1]

        if self.lookback_type == ExoticType.LOOKBACK_FLOATING:
            if self.option_type == OptionType.CALL:
                # Payoff: S_T - min(S)
                return terminal_prices - min_prices
            else:  # PUT
                # Payoff: max(S) - S_T
                return max_prices - terminal_prices

        else:  # FIXED strike
            if self.option_type == OptionType.CALL:
                # Payoff: max(max(S) - K, 0)
                return np.maximum(max_prices - self.strike, 0)
            else:  # PUT
                # Payoff: max(K - min(S), 0)
                return np.maximum(self.strike - min_prices, 0)


class DigitalOption(BasePayoff):
    """
    Digital (Binary) option with fixed payoff.

    - Cash-or-Nothing: Pays fixed amount if condition is met
    - Asset-or-Nothing: Pays asset price if condition is met
    """

    def __init__(
        self,
        option_type: OptionType,
        strike: float,
        digital_type: ExoticType = ExoticType.DIGITAL_CASH,
        cash_payoff: float = 1.0
    ):
        """
        Initialize digital option.

        Args:
            option_type: Call or Put
            strike: Strike price
            digital_type: Cash or Asset digital
            cash_payoff: Fixed payoff for cash-or-nothing
        """
        super().__init__(option_type, strike)

        if digital_type not in [ExoticType.DIGITAL_CASH, ExoticType.DIGITAL_ASSET]:
            raise ValueError(f"Invalid digital type: {digital_type}")

        self.digital_type = digital_type
        self.cash_payoff = cash_payoff

    def payoff(self, paths: np.ndarray, *args, **kwargs) -> np.ndarray:
        """
        Calculate digital option payoff.

        Args:
            paths: Array of simulated price paths, shape (n_paths, n_steps)

        Returns:
            Array of payoffs, shape (n_paths,)
        """
        terminal_prices = paths[:, -1]

        # Determine if option is in the money
        if self.option_type == OptionType.CALL:
            in_the_money = terminal_prices > self.strike
        else:  # PUT
            in_the_money = terminal_prices < self.strike

        # Calculate payoff based on type
        if self.digital_type == ExoticType.DIGITAL_CASH:
            # Pay fixed amount if ITM
            payoff = np.where(in_the_money, self.cash_payoff, 0.0)
        else:  # ASSET
            # Pay asset price if ITM
            payoff = np.where(in_the_money, terminal_prices, 0.0)

        return payoff
