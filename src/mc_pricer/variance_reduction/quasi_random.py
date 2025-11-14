"""
Quasi-random (low discrepancy) sequences for variance reduction.
"""
import numpy as np
from scipy.stats import qmc
from typing import Literal


class QuasiRandom:
    """
    Quasi-random sequences (Sobol, Halton) for variance reduction.

    Low-discrepancy sequences provide better coverage of the sample space
    than pseudo-random numbers, leading to faster convergence.

    Convergence rate:
    - Monte Carlo: O(1/N)
    - Quasi Monte Carlo: O((log N)^d / N) for d dimensions
    """

    def __init__(
        self,
        sequence_type: Literal['sobol', 'halton'] = 'sobol',
        scramble: bool = True
    ):
        """
        Initialize quasi-random sequence generator.

        Args:
            sequence_type: Type of sequence ('sobol' or 'halton')
            scramble: Apply random scrambling (recommended)
        """
        self.sequence_type = sequence_type
        self.scramble = scramble

    def generate_normal_samples(
        self,
        n_samples: int,
        dimension: int,
        seed: int = None
    ) -> np.ndarray:
        """
        Generate quasi-random normal samples.

        Args:
            n_samples: Number of samples
            dimension: Number of dimensions
            seed: Random seed for scrambling

        Returns:
            Array of shape (n_samples, dimension) with standard normal samples
        """
        # Generate uniform samples on [0, 1]^d
        uniform_samples = self._generate_uniform(n_samples, dimension, seed)

        # Transform to standard normal using inverse CDF
        from scipy.stats import norm
        normal_samples = norm.ppf(uniform_samples)

        return normal_samples

    def _generate_uniform(
        self,
        n_samples: int,
        dimension: int,
        seed: int = None
    ) -> np.ndarray:
        """
        Generate quasi-random uniform samples on [0, 1]^d.

        Args:
            n_samples: Number of samples
            dimension: Number of dimensions
            seed: Random seed for scrambling

        Returns:
            Array of shape (n_samples, dimension) with uniform samples
        """
        if self.sequence_type == 'sobol':
            sampler = qmc.Sobol(d=dimension, scramble=self.scramble, seed=seed)
        elif self.sequence_type == 'halton':
            sampler = qmc.Halton(d=dimension, scramble=self.scramble, seed=seed)
        else:
            raise ValueError(f"Unknown sequence type: {self.sequence_type}")

        # Generate samples
        samples = sampler.random(n_samples)

        return samples

    @staticmethod
    def estimate_discrepancy(samples: np.ndarray) -> float:
        """
        Estimate star discrepancy of samples (measure of uniformity).

        Lower discrepancy indicates better coverage of the space.

        Args:
            samples: Array of samples in [0, 1]^d

        Returns:
            Discrepancy measure
        """
        try:
            discrepancy = qmc.discrepancy(samples)
            return discrepancy
        except Exception:
            # Fallback if discrepancy calculation fails
            return -1.0

    def __repr__(self) -> str:
        return f"QuasiRandom(type='{self.sequence_type}', scramble={self.scramble})"
