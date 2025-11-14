"""
FastAPI backend for Monte Carlo Options Pricer.
"""
import sys
sys.path.insert(0, '../src')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

from mc_pricer import (
    MonteCarloEngine,
    MarketParameters,
    SimulationParameters,
    EuropeanOption,
    OptionType,
    ModelType,
    VarianceReductionMethod,
)

app = FastAPI(
    title="Monte Carlo Options Pricer API",
    description="Professional-grade options pricing API with Monte Carlo simulation",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Models
class OptionTypeAPI(str, Enum):
    CALL = "call"
    PUT = "put"


class VarianceReductionAPI(str, Enum):
    NONE = "none"
    ANTITHETIC = "antithetic"
    CONTROL_VARIATE = "control_variate"
    QUASI_RANDOM = "quasi_random"


class PriceRequest(BaseModel):
    S0: float = Field(100.0, gt=0)
    K: float = Field(100.0, gt=0)
    T: float = Field(1.0, gt=0)
    r: float = Field(0.05)
    q: float = Field(0.0)
    sigma: float = Field(0.2, gt=0)
    option_type: OptionTypeAPI = OptionTypeAPI.CALL
    n_paths: int = Field(50000, gt=0, le=500000)
    n_steps: int = Field(252, gt=0)
    variance_reduction: VarianceReductionAPI = VarianceReductionAPI.NONE


class PriceResponse(BaseModel):
    mc_price: float
    analytical_price: float
    error: float
    relative_error_pct: float
    std_error: float
    confidence_interval: tuple[float, float]
    paths_used: int
    computation_time: float


@app.get("/")
async def root():
    """Serve the web interface."""
    return FileResponse("static/index.html")


@app.post("/price", response_model=PriceResponse)
async def price_option(request: PriceRequest):
    """Price a European option using Monte Carlo simulation."""
    try:
        market_params = MarketParameters(
            S0=request.S0,
            K=request.K,
            T=request.T,
            r=request.r,
            q=request.q,
            sigma=request.sigma
        )
        
        vr_map = {
            "none": VarianceReductionMethod.NONE,
            "antithetic": VarianceReductionMethod.ANTITHETIC,
            "control_variate": VarianceReductionMethod.CONTROL_VARIATE,
            "quasi_random": VarianceReductionMethod.QUASI_RANDOM,
        }
        
        sim_params = SimulationParameters(
            n_paths=request.n_paths,
            n_steps=request.n_steps,
            model=ModelType.BLACK_SCHOLES,
            variance_reduction=vr_map[request.variance_reduction.value],
            seed=42
        )
        
        engine = MonteCarloEngine(market_params, sim_params)
        
        option_type = OptionType.CALL if request.option_type == OptionTypeAPI.CALL else OptionType.PUT
        option = EuropeanOption(option_type, request.K)
        
        result = engine.price(option)
        
        analytical_price = EuropeanOption.black_scholes_price(
            S0=request.S0,
            K=request.K,
            T=request.T,
            r=request.r,
            sigma=request.sigma,
            option_type=option_type,
            q=request.q
        )
        
        error = result.price - analytical_price
        relative_error_pct = abs(error / analytical_price) * 100 if analytical_price != 0 else 0
        
        return PriceResponse(
            mc_price=result.price,
            analytical_price=analytical_price,
            error=error,
            relative_error_pct=relative_error_pct,
            std_error=result.std_error,
            confidence_interval=result.confidence_interval,
            paths_used=result.paths_used,
            computation_time=result.computation_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
