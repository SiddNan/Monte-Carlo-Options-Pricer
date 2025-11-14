"""
Antithetic variates variance reduction technique.
"""
import numpy as np
from typing import Tuple


class AntitheticVariates:
    """
    Antithetic variates variance reduction method.

    For each random sample Z, we also use -Z. This creates negative correlation
    between paired samples, reducing variance for symmetric payoffs.

    Theoretical variance reduction: Up to 50% for symmetric payoffs
    """

    @staticmethod
    def generate_normal_variates(n_samples: int, dimension: int = 1) -> np.ndarray:
        """
        Generate antithetic normal random variates.

        Args:
            n_samples: Total number of samples (must be even)
            dimension: Dimensionality of each sample

        Returns:
            Array of shape (n_samples, dimension) with antithetic pairs
        """
        if n_samples % 2 != 0:
            raise ValueError("n_samples must be even for antithetic variates")

        # Generate half the samples
        half_n = n_samples // 2
        Z_half = np.random.standard_normal((half_n, dimension))

        # Create antithetic pairs
        Z = np.vstack([Z_half, -Z_half])

        return Z

    @staticmethod
    def estimate_variance_reduction(
        original_payoffs: np.ndarray,
        antithetic_payoffs: np.ndarray
    ) -> Tuple[float, float]:
        """
        Estimate variance reduction achieved.

        Args:
            original_payoffs: Payoffs without variance reduction
            antithetic_payoffs: Payoffs with antithetic variates

        Returns:
            Tuple of (variance_reduction_ratio, variance_reduction_percentage)
        """
        var_original = np.var(original_payoffs)
        var_antithetic = np.var(antithetic_payoffs)

        if var_original == 0:
            return 1.0, 0.0

        reduction_ratio = var_antithetic / var_original
        reduction_pct = (1 - reduction_ratio) * 100

        return reduction_ratio, reduction_pct

    def __repr__(self) -> str:
        return "AntitheticVariates(variance_reduction='symmetric_payoffs')"
