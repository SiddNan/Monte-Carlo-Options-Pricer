"""
Parameter dataclasses for market data and simulation configuration.
"""
from dataclasses import dataclass, field
from typing import Optional
from .enums import ModelType, VarianceReductionMethod


@dataclass
class MarketParameters:
    """
    Market and option contract parameters.

    Attributes:
        S0: Initial spot price
        K: Strike price
        T: Time to maturity (years)
        r: Risk-free interest rate (continuous compounding)
        q: Dividend yield (continuous compounding)
        sigma: Volatility (for Black-Scholes)
    """
    S0: float
    K: float
    T: float
    r: float
    q: float = 0.0
    sigma: Optional[float] = None

    def __post_init__(self):
        """Validate parameters."""
        if self.S0 <= 0:
            raise ValueError("Spot price must be positive")
        if self.K <= 0:
            raise ValueError("Strike price must be positive")
        if self.T <= 0:
            raise ValueError("Time to maturity must be positive")
        if self.sigma is not None and self.sigma <= 0:
            raise ValueError("Volatility must be positive")


@dataclass
class HestonParameters:
    """
    Parameters for Heston stochastic volatility model.

    dS_t = r*S_t*dt + sqrt(v_t)*S_t*dW^S_t
    dv_t = kappa*(theta - v_t)*dt + sigma_v*sqrt(v_t)*dW^v_t

    Attributes:
        v0: Initial variance
        kappa: Mean reversion speed
        theta: Long-run variance
        sigma_v: Volatility of volatility
        rho: Correlation between asset and variance
    """
    v0: float
    kappa: float
    theta: float
    sigma_v: float
    rho: float

    def __post_init__(self):
        """Validate Feller condition and parameters."""
        if self.v0 <= 0:
            raise ValueError("Initial variance must be positive")
        if self.kappa <= 0:
            raise ValueError("Mean reversion speed must be positive")
        if self.theta <= 0:
            raise ValueError("Long-run variance must be positive")
        if self.sigma_v <= 0:
            raise ValueError("Vol of vol must be positive")
        if not -1 <= self.rho <= 1:
            raise ValueError("Correlation must be in [-1, 1]")

        # Feller condition: ensures variance stays positive
        if 2 * self.kappa * self.theta <= self.sigma_v ** 2:
            import warnings
            warnings.warn(
                f"Feller condition violated: 2*kappa*theta = {2*self.kappa*self.theta:.4f} "
                f"<= sigma_v^2 = {self.sigma_v**2:.4f}. Variance may reach zero."
            )


@dataclass
class SimulationParameters:
    """
    Monte Carlo simulation configuration.

    Attributes:
        n_paths: Number of simulation paths
        n_steps: Number of time steps per path
        model: Stochastic model to use
        variance_reduction: Variance reduction method
        seed: Random seed for reproducibility
        antithetic: Whether to use antithetic variates (deprecated, use variance_reduction)
        use_sobol: Whether to use Sobol sequences (deprecated, use variance_reduction)
    """
    n_paths: int = 100000
    n_steps: int = 252
    model: ModelType = ModelType.BLACK_SCHOLES
    variance_reduction: VarianceReductionMethod = VarianceReductionMethod.NONE
    seed: Optional[int] = None
    antithetic: bool = False
    use_sobol: bool = False

    def __post_init__(self):
        """Validate simulation parameters."""
        if self.n_paths <= 0:
            raise ValueError("Number of paths must be positive")
        if self.n_steps <= 0:
            raise ValueError("Number of steps must be positive")

        # Handle deprecated parameters
        if self.antithetic and self.variance_reduction == VarianceReductionMethod.NONE:
            self.variance_reduction = VarianceReductionMethod.ANTITHETIC
        if self.use_sobol and self.variance_reduction == VarianceReductionMethod.NONE:
            self.variance_reduction = VarianceReductionMethod.QUASI_RANDOM


@dataclass
class BarrierParameters:
    """
    Additional parameters for barrier options.

    Attributes:
        barrier: Barrier level
        rebate: Rebate paid if barrier is breached (default 0)
    """
    barrier: float
    rebate: float = 0.0

    def __post_init__(self):
        """Validate barrier parameters."""
        if self.barrier <= 0:
            raise ValueError("Barrier level must be positive")
        if self.rebate < 0:
            raise ValueError("Rebate cannot be negative")


@dataclass
class PricingResult:
    """
    Results from Monte Carlo pricing.

    Attributes:
        price: Option price estimate
        std_error: Standard error of the estimate
        confidence_interval: 95% confidence interval (lower, upper)
        paths_used: Number of paths used in simulation
        computation_time: Time taken for computation (seconds)
    """
    price: float
    std_error: float
    confidence_interval: tuple[float, float]
    paths_used: int
    computation_time: float

    @property
    def relative_error(self) -> float:
        """Relative standard error as percentage."""
        if self.price == 0:
            return float('inf')
        return (self.std_error / abs(self.price)) * 100
