"""
Exotic options pricing example.

This example demonstrates pricing of:
1. Asian options (arithmetic and geometric averaging)
2. Barrier options (knock-out and knock-in)
3. Lookback options (fixed and floating strike)
4. Digital options (cash-or-nothing and asset-or-nothing)
"""

import sys
sys.path.insert(0, '../src')

from mc_pricer import (
    MonteCarloEngine,
    MarketParameters,
    SimulationParameters,
    AsianOption,
    BarrierOption,
    LookbackOption,
    DigitalOption,
    OptionType,
    ExoticType,
    ModelType,
    VarianceReductionMethod,
)


def main():
    print("=" * 70)
    print("Monte Carlo Options Pricer - Exotic Options Example")
    print("=" * 70)

    # Market parameters
    market_params = MarketParameters(
        S0=100.0,
        K=100.0,
        T=1.0,
        r=0.05,
        q=0.02,
        sigma=0.25
    )

    # Simulation with variance reduction for better accuracy
    sim_params = SimulationParameters(
        n_paths=50000,
        n_steps=252,
        model=ModelType.BLACK_SCHOLES,
        variance_reduction=VarianceReductionMethod.ANTITHETIC,
        seed=42
    )

    engine = MonteCarloEngine(market_params, sim_params)

    print(f"\nMarket: S0=${market_params.S0}, K=${market_params.K}, "
          f"T={market_params.T}y, Ã={market_params.sigma*100}%")
    print(f"Simulation: {sim_params.n_paths:,} paths, {sim_params.n_steps} steps\n")

    # 1. Asian Options
    print("=" * 70)
    print("ASIAN OPTIONS")
    print("=" * 70)

    # Arithmetic Asian Call
    asian_arith_call = AsianOption(
        option_type=OptionType.CALL,
        strike=market_params.K,
        averaging=ExoticType.ASIAN_ARITHMETIC
    )

    result = engine.price(asian_arith_call)
    print(f"\nArithmetic Asian Call:")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # Geometric Asian Call
    asian_geom_call = AsianOption(
        option_type=OptionType.CALL,
        strike=market_params.K,
        averaging=ExoticType.ASIAN_GEOMETRIC
    )

    result = engine.price(asian_geom_call)
    print(f"\nGeometric Asian Call:")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # 2. Barrier Options
    print("\n" + "=" * 70)
    print("BARRIER OPTIONS")
    print("=" * 70)

    # Up-and-Out Call
    barrier_up_out = BarrierOption(
        option_type=OptionType.CALL,
        strike=market_params.K,
        barrier=120.0,  # Barrier at 120
        barrier_type=ExoticType.BARRIER_UP_OUT,
        rebate=0.0
    )

    result = engine.price(barrier_up_out)
    print(f"\nUp-and-Out Call (Barrier=$120):")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # Down-and-Out Put
    barrier_down_out = BarrierOption(
        option_type=OptionType.PUT,
        strike=market_params.K,
        barrier=80.0,  # Barrier at 80
        barrier_type=ExoticType.BARRIER_DOWN_OUT,
        rebate=0.0
    )

    result = engine.price(barrier_down_out)
    print(f"\nDown-and-Out Put (Barrier=$80):")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # Up-and-In Call
    barrier_up_in = BarrierOption(
        option_type=OptionType.CALL,
        strike=market_params.K,
        barrier=120.0,
        barrier_type=ExoticType.BARRIER_UP_IN,
        rebate=0.0
    )

    result = engine.price(barrier_up_in)
    print(f"\nUp-and-In Call (Barrier=$120):")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # 3. Lookback Options
    print("\n" + "=" * 70)
    print("LOOKBACK OPTIONS")
    print("=" * 70)

    # Floating Strike Lookback Call
    lookback_float_call = LookbackOption(
        option_type=OptionType.CALL,
        strike=None,  # Floating strike
        lookback_type=ExoticType.LOOKBACK_FLOATING
    )

    result = engine.price(lookback_float_call)
    print(f"\nFloating Strike Lookback Call:")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # Fixed Strike Lookback Call
    lookback_fixed_call = LookbackOption(
        option_type=OptionType.CALL,
        strike=market_params.K,
        lookback_type=ExoticType.LOOKBACK_FIXED
    )

    result = engine.price(lookback_fixed_call)
    print(f"\nFixed Strike Lookback Call (K=${market_params.K}):")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # 4. Digital Options
    print("\n" + "=" * 70)
    print("DIGITAL OPTIONS")
    print("=" * 70)

    # Cash-or-Nothing Call
    digital_cash = DigitalOption(
        option_type=OptionType.CALL,
        strike=market_params.K,
        digital_type=ExoticType.DIGITAL_CASH,
        cash_payoff=10.0  # Pays $10 if S_T > K
    )

    result = engine.price(digital_cash)
    print(f"\nCash-or-Nothing Call (Payoff=$10):")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    # Asset-or-Nothing Call
    digital_asset = DigitalOption(
        option_type=OptionType.CALL,
        strike=market_params.K,
        digital_type=ExoticType.DIGITAL_ASSET,
        cash_payoff=1.0  # Not used for asset digital
    )

    result = engine.price(digital_asset)
    print(f"\nAsset-or-Nothing Call:")
    print(f"  Price:     ${result.price:.4f}")
    print(f"  Std Error: ${result.std_error:.4f}")
    print(f"  Time:      {result.computation_time:.3f}s")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
