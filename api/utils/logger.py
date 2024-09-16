import logging
from logging import Logger


class LoggerSingleton:
    _instance = None

    @staticmethod
    def get_logger() -> Logger:
        """Método estático para obtener la instancia del logger."""
        if LoggerSingleton._instance is None:
            LoggerSingleton()
        return LoggerSingleton._instance

    def __init__(self):
        """Inicializa el logger solo si no existe una instancia previa."""
        if LoggerSingleton._instance is not None:
            raise Exception("Esta clase es un singleton. Usa el método get_logger()")
        else:
            # Configuración del logger
            logger = logging.getLogger("production_plan_logger")
            logger.setLevel(logging.INFO)

            # Configuración del formato de los logs
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Guarda la instancia en la variable estática
            LoggerSingleton._instance = logger