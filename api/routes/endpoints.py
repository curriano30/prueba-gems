from fastapi import APIRouter, HTTPException
from utils.dto import ProductionPlanInput, ProductionPlanOutput
from service.app_service import calculate_production_plan_logic
from utils.logger import LoggerSingleton  # Importa el singleton

# Obtén la instancia del logger
logger = LoggerSingleton.get_logger()

# Crea un APIRouter en lugar de FastAPI
router = APIRouter()


# Endpoint que recibe el POST en /productionplan
@router.post("/productionplan", response_model=ProductionPlanOutput)
def calculate_production_plan(payload: ProductionPlanInput):
    logger.info("Recibido payload para /productionplan: %s", payload)

    try:
        # Llamamos a la función que contiene la lógica en el archivo de servicio
        production_plan_dict = calculate_production_plan_logic(payload)

        logger.info("Producción calculada con éxito para el payload: %s", payload)

        # Convertimos el diccionario de la lógica al formato de salida usando el modelo Pydantic
        return ProductionPlanOutput(powerplants=production_plan_dict["powerplants"])

    except Exception as e:
        logger.error("Error al calcular el plan de producción: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
