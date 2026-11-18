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

# ------------------------- Cliente -------------------------
# Clase Cliente: hereda de Entidad, así cada cliente recibe un id automático
class Cliente(Entidad):
    # Constructor: recibe los datos personales del cliente
    def __init__(self, nombre, documento, correo, telefono):
        # Se llama al constructor de Entidad para asignar el id
        super().__init__()
        # El nombre es obligatorio y debe tener mínimo 3 letras (sin contar espacios)
        if nombre is None or len(nombre.strip()) < 3:
            # Si no cumple se lanza la excepción personalizada de cliente
            raise ClienteInvalidoError("El nombre es obligatorio (mínimo 3 letras)")
        # El documento solo puede tener números y debe ser de 6 a 12 dígitos
        if documento is None or not str(documento).isdigit() or not 6 <= len(str(documento)) <= 12:
            raise ClienteInvalidoError("El documento debe tener entre 6 y 12 números")
        # Validación básica del correo: debe tener @ y punto
        if correo is None or "@" not in correo or "." not in correo:
            raise ClienteInvalidoError("El correo no es válido")
        # El teléfono debe ser numérico y de 10 dígitos (como un celular)
        if telefono is None or not str(telefono).isdigit() or len(str(telefono)) != 10:
            raise ClienteInvalidoError("El teléfono debe tener 10 dígitos")
        # Atributos privados con doble guion bajo (encapsulación):
        # no se pueden cambiar directamente desde fuera de la clase
        self.__nombre = nombre.strip()          # se guarda sin espacios al inicio y al final
        self.__documento = str(documento)       # se guarda como texto
        self.__correo = correo.strip().lower()  # se guarda en minúsculas
        self.__telefono = str(telefono)         # se guarda como texto

    # Getter para poder leer el nombre desde fuera de la clase
    def get_nombre(self):
        return self.__nombre

    # Getter del documento, sirve para revisar que no se repitan clientes
    def get_documento(self):
        return self.__documento

    # Se implementa el método abstracto describir() de Entidad (polimorfismo)
    def describir(self):
        # Devuelve un texto con los datos principales del cliente
        return f"Cliente #{self.id}: {self.__nombre} (doc {self.__documento}, {self.__correo})"

class Servicio(Entidad, ABC):
    def __init__(self, nombre, tarifa, disponible=True):
        super().__init__()
        if nombre is None or nombre.strip() == "":
            raise ServicioInvalidoError("El servicio necesita un nombre")
        if not isinstance(tarifa, (int, float)) or tarifa <= 0:
            raise ServicioInvalidoError("La tarifa debe ser un número mayor a 0")
        self.nombre = nombre.strip()
        self.tarifa = tarifa
        self.disponible = disponible

    @abstractmethod
    def costo_base(self, horas):
        pass

    @abstractmethod
    def validar_horas(self, horas):
        pass

    # Método sobrecargado (parámetros opcionales):
    #   calcular_costo(2) | calcular_costo(2, 0.10) | calcular_costo(2, 0.10, 0)
    def calcular_costo(self, horas, descuento=0, impuesto=IVA):
        self.validar_horas(horas)
        if descuento < 0 or descuento >= 1 or impuesto < 0:
            raise CalculoInconsistenteError("Descuento o impuesto fuera de rango")
        total = self.costo_base(horas) * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError("El costo calculado no es válido")
        return round(total, 2)
