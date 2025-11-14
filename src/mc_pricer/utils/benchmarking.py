"""
Benchmarking and convergence analysis utilities.
"""
import numpy as np
import time
from typing import List, Dict, Callable, Tuple
from dataclasses import dataclass
from ..core.engine import MonteCarloEngine
from ..payoffs.base import BasePayoff
from ..payoffs.european import EuropeanOption


@dataclass
class BenchmarkResult:
    """Results from a benchmarking run."""
    mc_price: float
    analytical_price: float
    error: float
    relative_error_pct: float
    std_error: float
    computation_time: float
    paths_used: int
    variance_reduction: str


class Benchmark:
    """
    Benchmarking utility for comparing Monte Carlo prices with analytical solutions.
    """

    @staticmethod
    def compare_with_analytical(
        engine: MonteCarloEngine,
        payoff: BasePayoff,
        analytical_price: float
    ) -> BenchmarkResult:
        """
        Compare MC price with analytical solution.

        Args:
            engine: Monte Carlo engine
            payoff: Option payoff
            analytical_price: Known analytical price

        Returns:
            BenchmarkResult with comparison metrics
        """
        result = engine.price(payoff)

        error = result.price - analytical_price
        relative_error_pct = abs(error / analytical_price) * 100 if analytical_price != 0 else float('inf')

        return BenchmarkResult(
            mc_price=result.price,
            analytical_price=analytical_price,
            error=error,
            relative_error_pct=relative_error_pct,
            std_error=result.std_error,
            computation_time=result.computation_time,
            paths_used=result.paths_used,
            variance_reduction=engine.sim_params.variance_reduction.value
        )

    @staticmethod
    def variance_reduction_comparison(
        base_engine: MonteCarloEngine,
        payoff: BasePayoff,
        methods: List[str],
        analytical_price: float = None
    ) -> Dict[str, BenchmarkResult]:
        """
        Compare different variance reduction methods.

        Args:
            base_engine: Base Monte Carlo engine
            payoff: Option payoff
            methods: List of variance reduction methods to compare
            analytical_price: Known analytical price (if available)

        Returns:
            Dictionary mapping method names to benchmark results
        """
        from ..core.enums import VarianceReductionMethod

        results = {}

        for method in methods:
            # Update variance reduction method
            base_engine.sim_params.variance_reduction = VarianceReductionMethod(method)

            # Price the option
            result = base_engine.price(payoff)

            # Get analytical price if not provided and payoff is European
            if analytical_price is None and isinstance(payoff, EuropeanOption):
                analytical_price = EuropeanOption.black_scholes_price(
                    S0=base_engine.market_params.S0,
                    K=payoff.strike,
                    T=base_engine.market_params.T,
                    r=base_engine.market_params.r,
                    sigma=base_engine.market_params.sigma,
                    option_type=payoff.option_type,
                    q=base_engine.market_params.q
                )

            if analytical_price is not None:
                error = result.price - analytical_price
                rel_error = abs(error / analytical_price) * 100
            else:
                error = None
                rel_error = None

            results[method] = BenchmarkResult(
                mc_price=result.price,
                analytical_price=analytical_price if analytical_price else 0.0,
                error=error if error else 0.0,
                relative_error_pct=rel_error if rel_error else 0.0,
                std_error=result.std_error,
                computation_time=result.computation_time,
                paths_used=result.paths_used,
                variance_reduction=method
            )

        return results


class ConvergenceAnalyzer:
    """
    Analyze convergence rate of Monte Carlo pricing.
    """

    @staticmethod
    def analyze_convergence(
        engine: MonteCarloEngine,
        payoff: BasePayoff,
        path_counts: List[int],
        analytical_price: float = None,
        n_runs: int = 10
    ) -> Dict[str, List]:
        """
        Analyze convergence by varying number of paths.

        Args:
            engine: Monte Carlo engine
            payoff: Option payoff
            path_counts: List of path counts to test
            analytical_price: Known analytical price
            n_runs: Number of runs per path count (for stability)

        Returns:
            Dictionary with convergence data
        """
        prices = []
        std_errors = []
        times = []
        errors = []

        original_paths = engine.sim_params.n_paths

        for n_paths in path_counts:
            engine.sim_params.n_paths = n_paths

            run_prices = []
            run_std_errors = []
            run_times = []

            for _ in range(n_runs):
                result = engine.price(payoff)
                run_prices.append(result.price)
                run_std_errors.append(result.std_error)
                run_times.append(result.computation_time)

            avg_price = np.mean(run_prices)
            avg_std_error = np.mean(run_std_errors)
            avg_time = np.mean(run_times)

            prices.append(avg_price)
            std_errors.append(avg_std_error)
            times.append(avg_time)

            if analytical_price is not None:
                errors.append(abs(avg_price - analytical_price))
            else:
                errors.append(None)

        # Restore original path count
        engine.sim_params.n_paths = original_paths

        return {
            'path_counts': path_counts,
            'prices': prices,
            'std_errors': std_errors,
            'times': times,
            'errors': errors,
            'analytical_price': analytical_price
        }

    @staticmethod
    def estimate_convergence_rate(
        path_counts: List[int],
        std_errors: List[float]
    ) -> Tuple[float, float]:
        """
        Estimate convergence rate from std errors.

        Monte Carlo should converge as O(1/N), so:
        log(std_error) = c - 0.5 * log(N)

        Args:
            path_counts: List of path counts
            std_errors: Corresponding standard errors

        Returns:
            Tuple of (slope, expected_slope)
            For Monte Carlo, expected slope H -0.5
        """
        log_paths = np.log(path_counts)
        log_std_errors = np.log(std_errors)

        # Fit linear regression: log(std) = a + b * log(N)
        coeffs = np.polyfit(log_paths, log_std_errors, 1)
        slope = coeffs[0]

        expected_slope = -0.5  # Theoretical MC convergence

        return slope, expected_slope

    @staticmethod
    def efficiency_ratio(
        std_error_base: float,
        time_base: float,
        std_error_vr: float,
        time_vr: float
    ) -> float:
        """
        Calculate efficiency ratio of variance reduction method.

        Efficiency = (Var_base / Var_VR) * (Time_VR / Time_base)

        Args:
            std_error_base: Standard error without variance reduction
            time_base: Computation time without variance reduction
            std_error_vr: Standard error with variance reduction
            time_vr: Computation time with variance reduction

        Returns:
            Efficiency ratio (> 1 means variance reduction is beneficial)
        """
        var_ratio = (std_error_base / std_error_vr) ** 2
        time_ratio = time_vr / time_base

        efficiency = var_ratio / time_ratio

        return efficiency
