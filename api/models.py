"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class OptionTypeAPI(str, Enum):
    """Option type for API."""
    CALL = "call"
    PUT = "put"


class ModelTypeAPI(str, Enum):
    """Stochastic model type for API."""
    BLACK_SCHOLES = "black_scholes"
    HESTON = "heston"


class VarianceReductionAPI(str, Enum):
    """Variance reduction method for API."""
    NONE = "none"
    ANTITHETIC = "antithetic"
    CONTROL_VARIATE = "control_variate"
    QUASI_RANDOM = "quasi_random"


class MarketParametersRequest(BaseModel):
    """Market parameters for pricing request."""
    S0: float = Field(..., gt=0, description="Current spot price")
    K: float = Field(..., gt=0, description="Strike price")
    T: float = Field(..., gt=0, description="Time to maturity (years)")
    r: float = Field(..., description="Risk-free rate")
    q: float = Field(0.0, description="Dividend yield")
    sigma: Optional[float] = Field(None, gt=0, description="Volatility (for Black-Scholes)")


class SimulationParametersRequest(BaseModel):
    """Simulation configuration."""
    n_paths: int = Field(100000, gt=0, description="Number of simulation paths")
    n_steps: int = Field(252, gt=0, description="Number of time steps")
    model: ModelTypeAPI = Field(ModelTypeAPI.BLACK_SCHOLES, description="Stochastic model")
    variance_reduction: VarianceReductionAPI = Field(
        VarianceReductionAPI.NONE,
        description="Variance reduction method"
    )
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class EuropeanOptionRequest(BaseModel):
    """European option pricing request."""
    option_type: OptionTypeAPI
    market_params: MarketParametersRequest
    sim_params: SimulationParametersRequest


class PricingResponse(BaseModel):
    """Option pricing response."""
    price: float
    std_error: float
    confidence_interval: tuple[float, float]
    paths_used: int
    computation_time: float
    relative_error_pct: float
    analytical_price: Optional[float] = None
