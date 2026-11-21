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


# Clase ReservaSala: es un tipo de servicio, por eso hereda de Servicio
class ReservaSala(Servicio):
    # Constructor: además del nombre y la tarifa, la sala necesita su capacidad
    def __init__(self, nombre, tarifa, capacidad, disponible=True):
        # Se llama al constructor de Servicio para que valide el nombre y la tarifa
        super().__init__(nombre, tarifa, disponible)
        # La capacidad tiene que ser un número entero mayor a 0
        if not isinstance(capacidad, int) or capacidad <= 0:
            # Si no cumple se lanza la excepción personalizada de servicio
            raise ServicioInvalidoError("La capacidad debe ser un entero mayor a 0")
        # Se guarda cuántas personas caben en la sala
        self.capacidad = capacidad

    # Se revisa que las horas tengan sentido para una sala
    def validar_horas(self, horas):
        # Las horas deben ser un número, mayor a 0 y máximo 12
        if not isinstance(horas, (int, float)) or horas <= 0 or horas > 12:
            raise ServicioInvalidoError("Una sala se reserva entre 1 y 12 horas")

    # Costo de la sala: cada servicio lo calcula a su manera (polimorfismo)
    def costo_base(self, horas):
        # Si la sala es para más de 20 personas se cobra un 15% más
        if self.capacidad > 20:  # recargo por sala grande
            return self.tarifa * horas * 1.15
        # Si no, se cobra la tarifa normal por las horas
        return self.tarifa * horas

    # Se implementa el método describir() para mostrar los datos de la sala
    def describir(self):
        # Devuelve un texto con el nombre, la capacidad y la tarifa por hora
        return f"Sala '{self.nombre}' (capacidad {self.capacidad}, ${self.tarifa}/h)"


# Clase AlquilerEquipo: otro tipo de servicio, también hereda de Servicio
class AlquilerEquipo(Servicio):
    # Valor fijo de fianza que se cobra en cada alquiler
    FIANZA = 20000

    # Constructor: aquí se necesita saber cuántas unidades del equipo se alquilan
    def __init__(self, nombre, tarifa, unidades, disponible=True):
        # Se llama al constructor de Servicio para que valide el nombre y la tarifa
        super().__init__(nombre, tarifa, disponible)
        # Las unidades deben ser un número entero mayor a 0
        if not isinstance(unidades, int) or unidades <= 0:
            # Si no cumple se lanza la excepción personalizada de servicio
            raise ServicioInvalidoError("Las unidades deben ser un entero mayor a 0")
        # Se guarda la cantidad de equipos
        self.unidades = unidades

    # Un equipo se puede alquilar máximo 72 horas (3 días)
    def validar_horas(self, horas):
        # Las horas deben ser un número, mayor a 0 y máximo 72
        if not isinstance(horas, (int, float)) or horas <= 0 or horas > 72:
            raise ServicioInvalidoError("Un equipo se alquila entre 1 y 72 horas")

    # Costo del alquiler: tarifa por horas por unidades, más la fianza
    def costo_base(self, horas):
        return self.tarifa * horas * self.unidades + self.FIANZA

    # Se implementa describir() para mostrar los datos del equipo
    def describir(self):
        # Devuelve el nombre del equipo, cuántas unidades son y la tarifa
        return f"Equipo '{self.nombre}' x{self.unidades} (${self.tarifa}/h c/u)"


# Clase AsesoriaEspecializada: el tercer tipo de servicio, hereda de Servicio
class AsesoriaEspecializada(Servicio):
    # Niveles del asesor y por cuánto se multiplica la tarifa en cada uno
    NIVELES = {"junior": 1, "senior": 1.5, "experto": 2}

    # Constructor: la asesoría necesita el nivel del asesor
    def __init__(self, nombre, tarifa, nivel, disponible=True):
        # Se llama al constructor de Servicio para que valide el nombre y la tarifa
        super().__init__(nombre, tarifa, disponible)
        # El nivel tiene que ser uno de los que están en NIVELES
        if nivel not in self.NIVELES:
            # Si no está se lanza la excepción personalizada de servicio
            raise ServicioInvalidoError("Nivel inválido (junior, senior o experto)")
        # Se guarda el nivel del asesor
        self.nivel = nivel

    # Una asesoría puede durar máximo 8 horas (una jornada)
    def validar_horas(self, horas):
        # Las horas deben ser un número, mayor a 0 y máximo 8
        if not isinstance(horas, (int, float)) or horas <= 0 or horas > 8:
            raise ServicioInvalidoError("Una asesoría dura entre 1 y 8 horas")

    # Costo de la asesoría: tarifa por horas, multiplicado según el nivel
    def costo_base(self, horas):
        return self.tarifa * horas * self.NIVELES[self.nivel]

    # Se implementa describir() para mostrar los datos de la asesoría
    def describir(self):
        # Devuelve el nombre, el nivel y la tarifa por hora
        return f"Asesoría '{self.nombre}' nivel {self.nivel} (${self.tarifa}/h)"
class Reserva(Entidad):
  def __init__(self, cliente, servicio, horas):
      super().__init__()
      if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
          raise ReservaInvalidaError("La reserva necesita un cliente y un servicio válidos")
      self.cliente = cliente
      self.servicio = servicio
      self.horas = horas
      self.estado = "PENDIENTE"
      self.total = 0

  def confirmar(self, descuento=0):
      if self.estado != "PENDIENTE":
          raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self.estado}")
      if not self.servicio.disponible:
          raise ServicioNoDisponibleError(f"'{self.servicio.nombre}' no está disponible")
      self.total = self.servicio.calcular_costo(self.horas, descuento)
      self.estado = "CONFIRMADA"

  def cancelar(self):
      if self.estado == "CANCELADA":
          raise OperacionNoPermitidaError("La reserva ya estaba cancelada")
      self.estado = "CANCELADA"

  def procesar(self, descuento=0):
      try:
          self.confirmar(descuento)
      except ErrorFJ as e:
          # encadenamiento de excepciones: se conserva el error original
          raise ReservaInvalidaError(f"Reserva #{self.id} fallida: {e}") from e
      else:
          logging.info(f"Reserva #{self.id} confirmada, total ${self.total}")
      finally:
          logging.info(f"Fin del procesamiento de la reserva #{self.id} ({self.estado})")

  def describir(self):
      return (f"Reserva #{self.id} [{self.estado}] {self.cliente.get_nombre()} -> "
              f"{self.servicio.nombre}, {self.horas} h, total ${self.total}")
class Reserva(Entidad):
    def __init__(self, cliente, servicio, horas):
        super().__init__()
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva necesita un cliente y un servicio válidos")
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "PENDIENTE"
        self.total = 0

    def confirmar(self, descuento=0):
        if self.estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva {self.estado}")
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(f"'{self.servicio.nombre}' no está disponible")
        self.total = self.servicio.calcular_costo(self.horas, descuento)
        self.estado = "CONFIRMADA"

    def cancelar(self):
        if self.estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya estaba cancelada")
        self.estado = "CANCELADA"

    def procesar(self, descuento=0):
        try:
            self.confirmar(descuento)
        except ErrorFJ as e:
            # encadenamiento de excepciones: se conserva el error original
            raise ReservaInvalidaError(f"Reserva #{self.id} fallida: {e}") from e
        else:
            logging.info(f"Reserva #{self.id} confirmada, total ${self.total}")
        finally:
            logging.info(f"Fin del procesamiento de la reserva #{self.id} ({self.estado})")

    def describir(self):
        return (f"Reserva #{self.id} [{self.estado}] {self.cliente.get_nombre()} -> "
                f"{self.servicio.nombre}, {self.horas} h, total ${self.total}")


