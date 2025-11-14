"""
Core Monte Carlo pricing engine.
"""
import numpy as np
import time
from typing import Optional, Union
from ..core.parameters import (
    MarketParameters,
    SimulationParameters,
    HestonParameters,
    PricingResult
)
from ..core.enums import ModelType, VarianceReductionMethod
from ..payoffs.base import BasePayoff
from ..models.black_scholes import BlackScholesModel


class MonteCarloEngine:
    """
    Main Monte Carlo engine for option pricing.

    This engine coordinates path generation, payoff calculation,
    and variance reduction techniques.
    """

    def __init__(
        self,
        market_params: MarketParameters,
        sim_params: SimulationParameters,
        heston_params: Optional[HestonParameters] = None
    ):
        """
        Initialize Monte Carlo engine.

        Args:
            market_params: Market and option parameters
            sim_params: Simulation configuration
            heston_params: Heston model parameters (required if using Heston model)
        """
        self.market_params = market_params
        self.sim_params = sim_params
        self.heston_params = heston_params

        # Validate configuration
        if sim_params.model == ModelType.HESTON and heston_params is None:
            raise ValueError("Heston parameters required when using Heston model")

        if sim_params.model == ModelType.BLACK_SCHOLES and market_params.sigma is None:
            raise ValueError("Volatility required for Black-Scholes model")

    def price(self, payoff: BasePayoff) -> PricingResult:
        """
        Price an option using Monte Carlo simulation.

        Args:
            payoff: Option payoff structure

        Returns:
            PricingResult with price, standard error, and confidence interval
        """
        start_time = time.time()

        # Generate paths using specified stochastic model
        paths = self._generate_paths()

        # Apply control variate if specified, otherwise use standard MC estimator
        if self.sim_params.variance_reduction == VarianceReductionMethod.CONTROL_VARIATE:
            price, std_error = self._price_with_control_variate(payoff, paths)
        else:
            # Standard Monte Carlo: E[e^(-rT) * Payoff(S_T)]
            discounted_payoffs = payoff.discounted_payoff(
                paths,
                self.market_params.r,
                self.market_params.T
            )
            # Unbiased estimator: sample mean
            price = np.mean(discounted_payoffs)
            # Standard error: sigma / sqrt(n) by CLT
            std_error = np.std(discounted_payoffs) / np.sqrt(len(discounted_payoffs))

        # 95% confidence interval using normal approximation (valid for large n)
        z_score = 1.96  # Critical value for 95% CI
        confidence_interval = (
            price - z_score * std_error,
            price + z_score * std_error
        )

        computation_time = time.time() - start_time

        return PricingResult(
            price=price,
            std_error=std_error,
            confidence_interval=confidence_interval,
            paths_used=self.sim_params.n_paths,
            computation_time=computation_time
        )

    def _generate_paths(self) -> np.ndarray:
        """
        Generate price paths based on the selected model.

        Returns:
            Array of simulated price paths
        """
        if self.sim_params.model == ModelType.BLACK_SCHOLES:
            return self._generate_bs_paths()
        elif self.sim_params.model == ModelType.HESTON:
            return self._generate_heston_paths()
        else:
            raise NotImplementedError(f"Model {self.sim_params.model} not implemented")

    def _generate_bs_paths(self) -> np.ndarray:
        """Generate paths using Black-Scholes model."""
        model = BlackScholesModel(
            S0=self.market_params.S0,
            r=self.market_params.r,
            sigma=self.market_params.sigma,
            T=self.market_params.T,
            q=self.market_params.q
        )

        # Check if we should use antithetic or quasi-random
        use_antithetic = (
            self.sim_params.variance_reduction == VarianceReductionMethod.ANTITHETIC
        )
        use_sobol = (
            self.sim_params.variance_reduction == VarianceReductionMethod.QUASI_RANDOM
        )

        return model.generate_paths(
            n_paths=self.sim_params.n_paths,
            n_steps=self.sim_params.n_steps,
            seed=self.sim_params.seed,
            antithetic=use_antithetic,
            use_sobol=use_sobol
        )

    def _generate_heston_paths(self) -> np.ndarray:
        """Generate paths using Heston model."""
        # Import here to avoid circular dependency
        from ..models.heston import HestonModel

        model = HestonModel(
            S0=self.market_params.S0,
            r=self.market_params.r,
            T=self.market_params.T,
            q=self.market_params.q,
            v0=self.heston_params.v0,
            kappa=self.heston_params.kappa,
            theta=self.heston_params.theta,
            sigma_v=self.heston_params.sigma_v,
            rho=self.heston_params.rho
        )

        return model.generate_paths(
            n_paths=self.sim_params.n_paths,
            n_steps=self.sim_params.n_steps,
            seed=self.sim_params.seed
        )

    def _price_with_control_variate(
        self,
        payoff: BasePayoff,
        paths: np.ndarray
    ) -> tuple[float, float]:
        """
        Price using control variate variance reduction.

        Uses a European option with analytical price as control.

        Args:
            payoff: Option payoff structure
            paths: Simulated price paths

        Returns:
            Tuple of (price, standard_error)
        """
        from ..payoffs.european import EuropeanOption
        from ..variance_reduction.control_variate import ControlVariate

        # Create control (European option with same strike)
        control = EuropeanOption(payoff.option_type, payoff.strike)

        # Get analytical price for control
        if self.sim_params.model == ModelType.BLACK_SCHOLES:
            control_price = EuropeanOption.black_scholes_price(
                S0=self.market_params.S0,
                K=payoff.strike,
                T=self.market_params.T,
                r=self.market_params.r,
                sigma=self.market_params.sigma,
                option_type=payoff.option_type,
                q=self.market_params.q
            )
        else:
            # For Heston, we'd need semi-analytical formula or fallback to standard MC
            # For now, fallback to standard MC
            discounted_payoffs = payoff.discounted_payoff(
                paths,
                self.market_params.r,
                self.market_params.T
            )
            price = np.mean(discounted_payoffs)
            std_error = np.std(discounted_payoffs) / np.sqrt(len(discounted_payoffs))
            return price, std_error

        # Apply control variate method
        cv = ControlVariate(control, control_price)
        return cv.apply(
            payoff=payoff,
            paths=paths,
            r=self.market_params.r,
            T=self.market_params.T
        )

    def calculate_greeks(
        self,
        payoff: BasePayoff,
        greek_type: str = 'delta',
        bump_size: float = 0.01
    ) -> float:
        """
        Calculate option Greeks using finite differences.

        Args:
            payoff: Option payoff structure
            greek_type: Type of Greek ('delta', 'gamma', 'vega', 'theta', 'rho')
            bump_size: Size of bump for finite difference

        Returns:
            Greek value
        """
        base_price = self.price(payoff).price

        if greek_type.lower() == 'delta':
            # Bump spot price
            original_S0 = self.market_params.S0
            self.market_params.S0 = original_S0 * (1 + bump_size)
            up_price = self.price(payoff).price
            self.market_params.S0 = original_S0
            return (up_price - base_price) / (original_S0 * bump_size)

        elif greek_type.lower() == 'gamma':
            # Second derivative w.r.t. spot
            original_S0 = self.market_params.S0
            self.market_params.S0 = original_S0 * (1 + bump_size)
            up_price = self.price(payoff).price
            self.market_params.S0 = original_S0 * (1 - bump_size)
            down_price = self.price(payoff).price
            self.market_params.S0 = original_S0
            return (up_price - 2 * base_price + down_price) / ((original_S0 * bump_size) ** 2)

        elif greek_type.lower() == 'vega':
            # Bump volatility
            if self.market_params.sigma is None:
                raise ValueError("Vega requires volatility parameter")
            original_sigma = self.market_params.sigma
            self.market_params.sigma = original_sigma * (1 + bump_size)
            up_price = self.price(payoff).price
            self.market_params.sigma = original_sigma
            return (up_price - base_price) / (original_sigma * bump_size)

        elif greek_type.lower() == 'theta':
            # Bump time to maturity
            original_T = self.market_params.T
            dt = 1 / 365  # One day
            self.market_params.T = original_T - dt
            future_price = self.price(payoff).price
            self.market_params.T = original_T
            return (future_price - base_price) / dt

        elif greek_type.lower() == 'rho':
            # Bump interest rate
            original_r = self.market_params.r
            self.market_params.r = original_r + bump_size
            up_price = self.price(payoff).price
            self.market_params.r = original_r
            return (up_price - base_price) / bump_size

        else:
            raise ValueError(f"Unknown Greek type: {greek_type}")
