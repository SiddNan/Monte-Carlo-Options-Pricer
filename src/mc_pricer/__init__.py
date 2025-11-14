"""
Monte Carlo Options Pricer

A professional-grade library for pricing options using Monte Carlo simulation
with advanced variance reduction techniques.
"""

__version__ = "0.1.0"

from .core.engine import MonteCarloEngine
from .core.parameters import (
    MarketParameters,
    SimulationParameters,
    HestonParameters,
    BarrierParameters,
    PricingResult,
)
from .core.enums import (
    OptionType,
    ExoticType,
    ModelType,
    VarianceReductionMethod,
    GreekType,
)
from .payoffs.european import EuropeanOption
from .payoffs.exotic import (
    AsianOption,
    BarrierOption,
    LookbackOption,
    DigitalOption,
)
from .models.black_scholes import BlackScholesModel
from .models.heston import HestonModel

__all__ = [
    # Core
    "MonteCarloEngine",
    # Parameters
    "MarketParameters",
    "SimulationParameters",
    "HestonParameters",
    "BarrierParameters",
    "PricingResult",
    # Enums
    "OptionType",
    "ExoticType",
    "ModelType",
    "VarianceReductionMethod",
    "GreekType",
    # Payoffs
    "EuropeanOption",
    "AsianOption",
    "BarrierOption",
    "LookbackOption",
    "DigitalOption",
    # Models
    "BlackScholesModel",
    "HestonModel",
]
