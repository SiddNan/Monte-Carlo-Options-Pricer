"""Variance reduction techniques."""

from .antithetic import AntitheticVariates
from .control_variate import ControlVariate
from .quasi_random import QuasiRandom

__all__ = [
    "AntitheticVariates",
    "ControlVariate",
    "QuasiRandom",
]
