from pydantic import BaseModel, Field
from typing import List

# Pydantic model for the Fuels input
class Fuels(BaseModel):
    gas_euro_per_mwh: float = Field(..., alias="gas(euro/MWh)")
    kerosine_euro_per_mwh: float = Field(..., alias="kerosine(euro/MWh)")
    co2_euro_per_ton: float = Field(..., alias="co2(euro/ton)")
    wind_percentage: float = Field(..., alias="wind(%)")

# Pydantic model for each Powerplant input
class Powerplant(BaseModel):
    name: str
    type: str
    efficiency: float
    pmin: float
    pmax: float

# Pydantic model for the main input (load, fuels, powerplants)
class ProductionPlanInput(BaseModel):
    load: float
    fuels: Fuels
    powerplants: List[Powerplant]

# Pydantic model for each Powerplant output
class PowerplantOutput(BaseModel):
    name: str
    p: float  # Se cambia 'power' por 'p'

# Pydantic model for the main output
class ProductionPlanOutput(BaseModel):
    powerplants: List[PowerplantOutput]
