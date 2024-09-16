import logging
from typing import List
from utils.dto import ProductionPlanInput, Powerplant, Fuels
from utils.logger import LoggerSingleton  # Importa el singleton

# Obtén la instancia del logger
logger = LoggerSingleton.get_logger()


def assign_power_to_plant(plant: Powerplant, load_remaining: float, wind_percentage: float = None) -> tuple:
    """
    Asigna la energía a una planta específica según el tipo y la carga restante.
    Devuelve la energía generada, la planta actualizada con la energía asignada, y la carga restante.
    """
    if plant.type == 'windturbine':
        generated_power = plant.pmax * (wind_percentage / 100)
    else:
        generated_power = plant.pmax

    generated_power = min(generated_power, load_remaining)  # No generar más de lo necesario
    plant_info = {
        "name": plant.name,
        "type": plant.type,
        "p": round(generated_power, 1),
        "pmin": plant.pmin if hasattr(plant, 'pmin') else None,
        "pmax": plant.pmax
    }

    load_remaining -= generated_power  # Reducimos la carga restante

    return plant_info, generated_power, load_remaining


def calculate_production_plan_logic(payload: ProductionPlanInput) -> dict:
    load_remaining = payload.load
    production_plan = []
    total_produced_power = 0  # Mantiene el total de energía producida

    logger.info("Inicio del cálculo del plan de producción. Carga solicitada: %d", payload.load)

    # Primero asignamos la energía generada por los parques eólicos (viento)
    for plant in payload.powerplants:
        if plant.type == 'windturbine':
            plant_info, generated_power, load_remaining = assign_power_to_plant(plant, load_remaining,
                                                                                payload.fuels.wind_percentage)
            production_plan.append(plant_info)
            total_produced_power += generated_power
            logger.info("Planta %s generó %.1f MWh de energía eólica. Carga restante: %.1f", plant.name,
                        generated_power, load_remaining)

    # Luego asignamos la energía generada por las plantas de gasfired
    for plant in payload.powerplants:
        if plant.type == 'gasfired':
            plant_info, generated_power, load_remaining = assign_power_to_plant(plant, load_remaining)
            production_plan.append(plant_info)
            total_produced_power += generated_power
            logger.info("Planta %s generó %.1f MWh de energía gasfired. Carga restante: %.1f", plant.name,
                        generated_power, load_remaining)

    # Finalmente asignamos la energía generada por las plantas de turbojet
    for plant in payload.powerplants:
        if plant.type == 'turbojet':
            plant_info, generated_power, load_remaining = assign_power_to_plant(plant, load_remaining)
            production_plan.append(plant_info)
            total_produced_power += generated_power
            logger.info("Planta %s generó %.1f MWh de energía turbojet. Carga restante: %.1f", plant.name,
                        generated_power, load_remaining)

    # Realizamos la fase de ajustes para garantizar que se cumplen los pmin
    final_plan, fail, excess_units = adjust_power_to_meet_min(production_plan)

    if fail:
        logger.warning("Se detectó un exceso de %.1f MWh. Desactivando plantas hasta eliminar el exceso.", excess_units)
        # Desactivamos plantas hasta eliminar el exceso
        excess_units = reduce_excess_power(final_plan, excess_units)

    return {"powerplants": final_plan}

def reduce_excess_power(production_plan: List[dict], excess_units: float) -> float:
    """
    Reduce la potencia de las plantas a 0.0 MWh hasta eliminar el exceso de energía.
    Las plantas se desactivan de menor a mayor eficiencia y capacidad.
    """
    # Definimos un criterio de eficiencia basado en el tipo de planta
    efficiency_order = {
        'windturbine': 1,  # Asumimos que las turbinas de viento son las más eficientes
        'gasfired': 2,     # Las plantas de gas son menos eficientes que las eólicas
        'turbojet': 3      # Las turbojets son las menos eficientes
    }

    # Ordenamos las plantas primero por eficiencia (tipo) y luego por capacidad (pmax)
    sorted_plan = sorted(
        production_plan,
        key=lambda plant: (efficiency_order.get(plant['type'], 4), plant['pmax'])
    )

    # Desactivamos plantas hasta eliminar el exceso
    for plant in sorted_plan:
        if plant["p"] > 0:  # Solo desactivamos plantas que están generando
            logger.info("Desactivando planta %s para reducir el exceso de energía. Generaba %.1f MWh.", plant["name"], plant["p"])
            excess_units -= plant["p"]
            plant["p"] = 0.0  # Desactivamos la planta

            if excess_units <= 0:
                logger.info("Exceso de energía eliminado.")
                break  # Salimos si el exceso ha sido completamente eliminado

    if excess_units > 0:
        logger.warning("No se pudo eliminar completamente el exceso. Exceso restante: %.1f MWh.", excess_units)

    return excess_units

def adjust_power_to_meet_min(production_plan: List[dict]) -> (List[dict], bool, float):
    """
    Ajusta las plantas para cumplir con los pmin. Devuelve el plan ajustado, un indicador de fallo y el exceso.
    """
    for i, plant in enumerate(production_plan):
        if plant["p"] > 0 and plant["p"] < plant["pmin"]:
            deficit = plant["pmin"] - plant["p"]
            logger.info("Se detectó la necesidad de un reajuste en la planta %s. Déficit de %.1f MWh.", plant["name"], deficit)
            fail, new_deficit = adjust_power_to_meet_min_backward(production_plan, i - 1, deficit)
            if fail:
                logger.warning("Reajuste falló. No se pudo cubrir el déficit de %.1f MWh.", new_deficit)
                return production_plan, True, new_deficit
            plant["p"] = plant["pmin"]
            logger.info("Reajuste completo en planta %s. Potencia ajustada a %.1f MWh.", plant["name"], plant["p"])

    # Después del ajuste, revisamos si alguna planta tiene un exceso de energía
    for plant in production_plan:
        if plant["p"] > plant["pmax"]:
            excess_units = plant["p"] - plant["pmax"]
            logger.error("Exceso de energía en la planta %s. Exceso de %.1f MWh.", plant["name"], excess_units)
            return production_plan, True, excess_units

    return production_plan, False, 0.0

def adjust_power_to_meet_min_backward(production_plan: List[dict], idx: int, deficit: float) -> (bool, float):
    """
    Ajusta la generación de las plantas de forma recursiva o iterativa hacia atrás para cubrir el déficit de energía.
    Devuelve un indicador de fallo si no se puede ajustar más, junto con el déficit restante.
    """
    # Si llegamos al principio de la lista y aún tenemos un déficit, no se puede ajustar más
    if idx < 0:
        logger.warning("No se puede ajustar más potencia hacia atrás. Déficit restante: %.1f MWh.", deficit)
        return True, deficit

    # Obtenemos la planta en el índice actual
    current_plant = production_plan[idx]
    logger.info("Reajustando planta %s en la cadena de reajuste. Potencia actual: %.1f MWh.", current_plant["name"], current_plant["p"])

    # Si la planta no tiene `pmin` o no genera nada, pasamos al siguiente
    if 'pmin' not in current_plant or current_plant["p"] == 0:
        logger.info("La planta %s no tiene pmin o genera 0 MWh, continuando con la siguiente en la cadena de reajuste.", current_plant["name"])
        return adjust_power_to_meet_min_backward(production_plan, idx - 1, deficit)

    # Verificamos cuánta energía puede reducirse sin bajar del pmin
    available_reduction = current_plant["p"] - current_plant["pmin"]

    # Si la planta puede reducirse lo suficiente para cubrir el déficit
    if available_reduction >= deficit:
        current_plant["p"] -= deficit
        logger.info("La planta %s ha sido ajustada. Nueva potencia: %.1f MWh.", current_plant["name"], current_plant["p"])
        return False, 0.0  # No hay fallo, el déficit ha sido cubierto
    else:
        # Reducimos lo máximo posible y pasamos el resto hacia atrás
        current_plant["p"] -= available_reduction
        new_deficit = deficit - available_reduction
        logger.info("Reajuste en cadena para la planta %s. Nuevo déficit a corregir: %.1f MWh.", current_plant["name"], new_deficit)
        return adjust_power_to_meet_min_backward(production_plan, idx - 1, new_deficit)

    current_plant["p"] = round(current_plant["p"], 1)


