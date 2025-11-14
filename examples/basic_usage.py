"""
Basic usage example: Pricing European options with Monte Carlo.

This example demonstrates:
1. Setting up market parameters
2. Configuring simulation parameters
3. Pricing European call and put options
4. Comparing with Black-Scholes analytical solution
5. Using different variance reduction methods
"""

import sys
sys.path.insert(0, '../src')

from mc_pricer import (
    MonteCarloEngine,
    MarketParameters,
    SimulationParameters,
    EuropeanOption,
    OptionType,
    ModelType,
    VarianceReductionMethod,
)


def main():
    print("=" * 70)
    print("Monte Carlo Options Pricer - Basic Usage Example")
    print("=" * 70)

    # 1. Define market parameters
    market_params = MarketParameters(
        S0=100.0,        # Current stock price
        K=100.0,         # Strike price (ATM option)
        T=1.0,           # 1 year to maturity
        r=0.05,          # 5% risk-free rate
        q=0.02,          # 2% dividend yield
        sigma=0.2        # 20% volatility
    )

    print(f"\nMarket Parameters:")
    print(f"  Spot Price (S0): ${market_params.S0}")
    print(f"  Strike (K): ${market_params.K}")
    print(f"  Time to Maturity (T): {market_params.T} years")
    print(f"  Risk-free Rate (r): {market_params.r * 100}%")
    print(f"  Dividend Yield (q): {market_params.q * 100}%")
    print(f"  Volatility (Ã): {market_params.sigma * 100}%")

    # 2. Configure simulation
    sim_params = SimulationParameters(
        n_paths=100000,
        n_steps=252,    # Daily steps
        model=ModelType.BLACK_SCHOLES,
        variance_reduction=VarianceReductionMethod.NONE,
        seed=42
    )

    print(f"\nSimulation Parameters:")
    print(f"  Number of Paths: {sim_params.n_paths:,}")
    print(f"  Time Steps: {sim_params.n_steps}")
    print(f"  Model: {sim_params.model.value}")

    # 3. Create pricing engine
    engine = MonteCarloEngine(market_params, sim_params)

    # 4. Price European Call
    print("\n" + "=" * 70)
    print("EUROPEAN CALL OPTION")
    print("=" * 70)

    call_option = EuropeanOption(OptionType.CALL, market_params.K)

    # Get analytical (Black-Scholes) price
    bs_call_price = EuropeanOption.black_scholes_price(
        S0=market_params.S0,
        K=market_params.K,
        T=market_params.T,
        r=market_params.r,
        sigma=market_params.sigma,
        option_type=OptionType.CALL,
        q=market_params.q
    )

    # Monte Carlo price
    mc_result = engine.price(call_option)

    print(f"\nBlack-Scholes Price: ${bs_call_price:.4f}")
    print(f"Monte Carlo Price:   ${mc_result.price:.4f}")
    print(f"Error:               ${abs(mc_result.price - bs_call_price):.4f}")
    print(f"Relative Error:      {abs((mc_result.price - bs_call_price) / bs_call_price) * 100:.2f}%")
    print(f"Standard Error:      ${mc_result.std_error:.4f}")
    print(f"95% Confidence Int:  [${mc_result.confidence_interval[0]:.4f}, ${mc_result.confidence_interval[1]:.4f}]")
    print(f"Computation Time:    {mc_result.computation_time:.3f}s")

    # 5. Price European Put
    print("\n" + "=" * 70)
    print("EUROPEAN PUT OPTION")
    print("=" * 70)

    put_option = EuropeanOption(OptionType.PUT, market_params.K)

    bs_put_price = EuropeanOption.black_scholes_price(
        S0=market_params.S0,
        K=market_params.K,
        T=market_params.T,
        r=market_params.r,
        sigma=market_params.sigma,
        option_type=OptionType.PUT,
        q=market_params.q
    )

    mc_result = engine.price(put_option)

    print(f"\nBlack-Scholes Price: ${bs_put_price:.4f}")
    print(f"Monte Carlo Price:   ${mc_result.price:.4f}")
    print(f"Error:               ${abs(mc_result.price - bs_put_price):.4f}")
    print(f"Relative Error:      {abs((mc_result.price - bs_put_price) / bs_put_price) * 100:.2f}%")
    print(f"Standard Error:      ${mc_result.std_error:.4f}")
    print(f"95% Confidence Int:  [${mc_result.confidence_interval[0]:.4f}, ${mc_result.confidence_interval[1]:.4f}]")
    print(f"Computation Time:    {mc_result.computation_time:.3f}s")

    # 6. Compare variance reduction methods
    print("\n" + "=" * 70)
    print("VARIANCE REDUCTION COMPARISON (Call Option)")
    print("=" * 70)

    methods = [
        VarianceReductionMethod.NONE,
        VarianceReductionMethod.ANTITHETIC,
        VarianceReductionMethod.QUASI_RANDOM,
        VarianceReductionMethod.CONTROL_VARIATE,
    ]

    print(f"\n{'Method':<20} {'Price':<12} {'Std Error':<12} {'Time (s)':<10} {'Variance Reduction'}")
    print("-" * 80)

    baseline_variance = None

    for method in methods:
        engine.sim_params.variance_reduction = method
        result = engine.price(call_option)

        if baseline_variance is None:
            baseline_variance = result.std_error ** 2
            var_reduction = 0.0
        else:
            var_reduction = (1 - (result.std_error ** 2) / baseline_variance) * 100

        print(f"{method.value:<20} ${result.price:<11.4f} ${result.std_error:<11.4f} "
              f"{result.computation_time:<10.3f} {var_reduction:>5.1f}%")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
