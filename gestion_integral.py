import logging
import os
from abc import ABC, abstractmethod

os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/software_fj.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

IVA = 0.19


# ------------------------- Excepciones personalizadas -------------------------
class ErrorFJ(Exception):
    """Error general del sistema, las demás excepciones heredan de esta."""

class ClienteInvalidoError(ErrorFJ): pass
class ServicioInvalidoError(ErrorFJ): pass
class ServicioNoDisponibleError(ErrorFJ): pass
class ReservaInvalidaError(ErrorFJ): pass
class OperacionNoPermitidaError(ErrorFJ): pass
class CalculoInconsistenteError(ErrorFJ): pass


# ------------------------- Clase abstracta general -------------------------
class Entidad(ABC):
    contador = 0

    def __init__(self):
        Entidad.contador += 1
        self.id = Entidad.contador

    @abstractmethod
    def describir(self):
        pass
