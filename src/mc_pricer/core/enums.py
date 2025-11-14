"""
Enumerations for option types, models, and variance reduction methods.
"""
from enum import Enum


class OptionType(Enum):
    """Type of option contract."""
    CALL = "call"
    PUT = "put"


class ExoticType(Enum):
    """Type of exotic option."""
    ASIAN_ARITHMETIC = "asian_arithmetic"
    ASIAN_GEOMETRIC = "asian_geometric"
    BARRIER_UP_OUT = "barrier_up_out"
    BARRIER_DOWN_OUT = "barrier_down_out"
    BARRIER_UP_IN = "barrier_up_in"
    BARRIER_DOWN_IN = "barrier_down_in"
    LOOKBACK_FIXED = "lookback_fixed"
    LOOKBACK_FLOATING = "lookback_floating"
    DIGITAL_CASH = "digital_cash"
    DIGITAL_ASSET = "digital_asset"


class ModelType(Enum):
    """Stochastic model for asset price simulation."""
    BLACK_SCHOLES = "black_scholes"
    HESTON = "heston"
    MERTON_JUMP = "merton_jump"


class VarianceReductionMethod(Enum):
    """Variance reduction technique."""
    NONE = "none"
    ANTITHETIC = "antithetic"
    CONTROL_VARIATE = "control_variate"
    IMPORTANCE_SAMPLING = "importance_sampling"
    STRATIFIED = "stratified"
    QUASI_RANDOM = "quasi_random"


class GreekType(Enum):
    """Types of option Greeks."""
    DELTA = "delta"
    GAMMA = "gamma"
    VEGA = "vega"
    THETA = "theta"
    RHO = "rho"
