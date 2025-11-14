"""
Tests for Monte Carlo pricing engine.
"""
import pytest
import numpy as np
from mc_pricer import (
    MonteCarloEngine,
    MarketParameters,
    SimulationParameters,
    EuropeanOption,
    OptionType,
    ModelType,
    VarianceReductionMethod,
)


class TestMonteCarloEngine:
    """Test suite for Monte Carlo engine."""

    @pytest.fixture
    def market_params(self):
        """Standard market parameters for testing."""
        return MarketParameters(
            S0=100.0,
            K=100.0,
            T=1.0,
            r=0.05,
            q=0.02,
            sigma=0.2
        )

    @pytest.fixture
    def sim_params(self):
        """Standard simulation parameters for testing."""
        return SimulationParameters(
            n_paths=10000,
            n_steps=100,
            model=ModelType.BLACK_SCHOLES,
            variance_reduction=VarianceReductionMethod.NONE,
            seed=42
        )

    def test_engine_initialization(self, market_params, sim_params):
        """Test engine initializes correctly."""
        engine = MonteCarloEngine(market_params, sim_params)
        assert engine.market_params == market_params
        assert engine.sim_params == sim_params

    def test_european_call_pricing(self, market_params, sim_params):
        """Test European call option pricing."""
        engine = MonteCarloEngine(market_params, sim_params)
        call = EuropeanOption(OptionType.CALL, market_params.K)

        result = engine.price(call)

        # Get analytical price
        analytical_price = EuropeanOption.black_scholes_price(
            S0=market_params.S0,
            K=market_params.K,
            T=market_params.T,
            r=market_params.r,
            sigma=market_params.sigma,
            option_type=OptionType.CALL,
            q=market_params.q
        )

        # MC price should be close to analytical (within 3 std errors)
        assert abs(result.price - analytical_price) <= 3 * result.std_error

        # Basic sanity checks
        assert result.price > 0
        assert result.std_error > 0
        assert result.paths_used == sim_params.n_paths

    def test_european_put_pricing(self, market_params, sim_params):
        """Test European put option pricing."""
        engine = MonteCarloEngine(market_params, sim_params)
        put = EuropeanOption(OptionType.PUT, market_params.K)

        result = engine.price(put)

        analytical_price = EuropeanOption.black_scholes_price(
            S0=market_params.S0,
            K=market_params.K,
            T=market_params.T,
            r=market_params.r,
            sigma=market_params.sigma,
            option_type=OptionType.PUT,
            q=market_params.q
        )

        assert abs(result.price - analytical_price) <= 3 * result.std_error
        assert result.price > 0

    def test_put_call_parity(self, market_params, sim_params):
        """Test put-call parity holds approximately."""
        engine = MonteCarloEngine(market_params, sim_params)

        call = EuropeanOption(OptionType.CALL, market_params.K)
        put = EuropeanOption(OptionType.PUT, market_params.K)

        call_result = engine.price(call)
        put_result = engine.price(put)

        # Put-Call Parity: C - P = S0*exp(-qT) - K*exp(-rT)
        lhs = call_result.price - put_result.price
        rhs = (market_params.S0 * np.exp(-market_params.q * market_params.T) -
               market_params.K * np.exp(-market_params.r * market_params.T))

        # Allow for MC error
        combined_error = np.sqrt(call_result.std_error**2 + put_result.std_error**2)
        assert abs(lhs - rhs) <= 3 * combined_error

    def test_antithetic_variance_reduction(self, market_params, sim_params):
        """Test antithetic variates reduces variance."""
        call = EuropeanOption(OptionType.CALL, market_params.K)

        # Price without variance reduction
        sim_params.variance_reduction = VarianceReductionMethod.NONE
        engine = MonteCarloEngine(market_params, sim_params)
        result_base = engine.price(call)

        # Price with antithetic variates
        sim_params.variance_reduction = VarianceReductionMethod.ANTITHETIC
        engine = MonteCarloEngine(market_params, sim_params)
        result_antithetic = engine.price(call)

        # Variance should be reduced
        assert result_antithetic.std_error < result_base.std_error

    def test_seed_reproducibility(self, market_params, sim_params):
        """Test that seed produces reproducible results."""
        call = EuropeanOption(OptionType.CALL, market_params.K)

        engine1 = MonteCarloEngine(market_params, sim_params)
        result1 = engine1.price(call)

        engine2 = MonteCarloEngine(market_params, sim_params)
        result2 = engine2.price(call)

        # Results should be identical with same seed
        assert result1.price == result2.price

    def test_otm_option_pricing(self, market_params, sim_params):
        """Test pricing of out-of-the-money options."""
        # Deep OTM call (K >> S0)
        otm_call = EuropeanOption(OptionType.CALL, strike=150.0)
        engine = MonteCarloEngine(market_params, sim_params)
        result = engine.price(otm_call)

        # OTM option should have low but positive price
        assert 0 < result.price < 5.0

    def test_itm_option_pricing(self, market_params, sim_params):
        """Test pricing of in-the-money options."""
        # Deep ITM call (K << S0)
        itm_call = EuropeanOption(OptionType.CALL, strike=80.0)
        engine = MonteCarloEngine(market_params, sim_params)
        result = engine.price(itm_call)

        # ITM option should have significant intrinsic value
        intrinsic_value = market_params.S0 - 80.0
        assert result.price > intrinsic_value * 0.8

    def test_zero_volatility(self, market_params, sim_params):
        """Test pricing with zero volatility."""
        market_params.sigma = 0.001  # Near-zero volatility

        # ATM call with zero vol should be worth approximately intrinsic value
        call = EuropeanOption(OptionType.CALL, market_params.K)
        engine = MonteCarloEngine(market_params, sim_params)
        result = engine.price(call)

        # With very low vol, ATM call has small value
        assert result.price < 10.0

    def test_confidence_interval(self, market_params, sim_params):
        """Test that confidence interval is properly formed."""
        call = EuropeanOption(OptionType.CALL, market_params.K)
        engine = MonteCarloEngine(market_params, sim_params)
        result = engine.price(call)

        lower, upper = result.confidence_interval

        # CI should bracket the price
        assert lower < result.price < upper

        # CI width should be approximately 2 * 1.96 * std_error
        expected_width = 2 * 1.96 * result.std_error
        actual_width = upper - lower
        assert abs(actual_width - expected_width) < 0.01


class TestVarianceReduction:
    """Test variance reduction methods."""

    @pytest.fixture
    def setup(self):
        """Setup for variance reduction tests."""
        market_params = MarketParameters(
            S0=100.0, K=100.0, T=1.0, r=0.05, q=0.0, sigma=0.2
        )
        sim_params = SimulationParameters(
            n_paths=10000, n_steps=100, seed=42
        )
        return market_params, sim_params

    def test_quasi_random_sequences(self, setup):
        """Test Sobol sequences for variance reduction."""
        market_params, sim_params = setup
        call = EuropeanOption(OptionType.CALL, market_params.K)

        # Standard MC
        sim_params.variance_reduction = VarianceReductionMethod.NONE
        engine = MonteCarloEngine(market_params, sim_params)
        result_standard = engine.price(call)

        # Quasi-random MC
        sim_params.variance_reduction = VarianceReductionMethod.QUASI_RANDOM
        engine = MonteCarloEngine(market_params, sim_params)
        result_qmc = engine.price(call)

        # Both should give similar prices
        analytical = EuropeanOption.black_scholes_price(
            market_params.S0, market_params.K, market_params.T,
            market_params.r, market_params.sigma, OptionType.CALL
        )

        assert abs(result_standard.price - analytical) < 0.5
        assert abs(result_qmc.price - analytical) < 0.5
