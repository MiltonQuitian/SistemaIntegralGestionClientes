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


# ------------------------- Listas internas y operaciones -------------------------
# Listas donde se guardan los datos del sistema (no se usa base de datos)
clientes = []
servicios = []
reservas = []


# Función para registrar un cliente nuevo
def registrar_cliente(nombre, documento, correo, telefono):
    # Se crea el cliente; si algún dato está mal, la clase Cliente lanza el error
    cliente = Cliente(nombre, documento, correo, telefono)
    # Se recorre la lista para revisar que el documento no esté repetido
    for c in clientes:
        # Si ya hay un cliente con el mismo documento, no se deja registrar
        if c.get_documento() == cliente.get_documento():
            raise ClienteInvalidoError("Ya existe un cliente con ese documento")
    # Si todo está bien, se agrega el cliente a la lista
    clientes.append(cliente)
    # Se deja registrado en el log que el cliente se creó
    logging.info("Cliente registrado: " + cliente.describir())
    # Se devuelve el cliente para poder usarlo después
    return cliente


# Función para agregar un servicio a la lista
def agregar_servicio(servicio):
    # Se guarda el servicio en la lista de servicios
    servicios.append(servicio)
    # Se deja registrado en el log que el servicio se creó
    logging.info("Servicio creado: " + servicio.describir())
    # Se devuelve el servicio
    return servicio


# Función para crear una reserva, el descuento es opcional
def crear_reserva(cliente, servicio, horas, descuento=0):
    # Se crea la reserva con el cliente, el servicio y las horas
    reserva = Reserva(cliente, servicio, horas)
    # Se guarda en la lista, así queda aunque luego falle (para ver el historial)
    reservas.append(reserva)
    # Se procesa la reserva: aquí se confirma y se calcula el costo
    reserva.procesar(descuento)
    # Se devuelve la reserva
    return reserva


# ------------------------- Interfaz tkinter -------------------------
def abrir_ventana():
    import tkinter as tk
    from tkinter import ttk, messagebox

    ventana = tk.Tk()
    ventana.title("Software FJ")
    pestanas = ttk.Notebook(ventana)
    pestanas.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- Pestaña Clientes ----------
    tab_clientes = ttk.Frame(pestanas)
    pestanas.add(tab_clientes, text="Clientes")
    entradas = {}
    fila = 0
    for campo in ["Nombre", "Documento", "Correo", "Teléfono"]:
        ttk.Label(tab_clientes, text=campo).grid(row=fila, column=0, sticky="w", padx=5, pady=3)
        entradas[campo] = ttk.Entry(tab_clientes, width=35)
        entradas[campo].grid(row=fila, column=1, padx=5)
        fila += 1
    lista_clientes = tk.Listbox(tab_clientes, width=80, height=8)
    lista_clientes.grid(row=6, column=0, columnspan=2, padx=5, pady=8)

    def boton_registrar_cliente():
        try:
            registrar_cliente(entradas["Nombre"].get(), entradas["Documento"].get(),
                              entradas["Correo"].get(), entradas["Teléfono"].get())
        except ErrorFJ as e:
            logging.error(f"Interfaz - {type(e).__name__}: {e}")
            messagebox.showerror("Error", str(e))
        else:
            for entrada in entradas.values():
                entrada.delete(0, "end")
            messagebox.showinfo("Listo", "Cliente registrado")
        finally:
            actualizar()

    ttk.Button(tab_clientes, text="Registrar cliente", command=boton_registrar_cliente).grid(row=4, column=1, sticky="e", padx=5, pady=5)


    # ---------- Pestaña Servicios ----------
    # Se crea la pestaña de servicios y se agrega a la ventana
    tab_servicios = ttk.Frame(pestanas)
    pestanas.add(tab_servicios, text="Servicios")
    # Lista desplegable para escoger el tipo de servicio
    ttk.Label(tab_servicios, text="Tipo").grid(row=0, column=0, sticky="w", padx=5, pady=3)
    tipo = ttk.Combobox(tab_servicios, values=["Sala", "Equipo", "Asesoría"], state="readonly", width=32)
    # Por defecto queda seleccionada la primera opción (Sala)
    tipo.current(0)
    tipo.grid(row=0, column=1, padx=5)
    # Campo para escribir el nombre del servicio
    ttk.Label(tab_servicios, text="Nombre").grid(row=1, column=0, sticky="w", padx=5, pady=3)
    entrada_nombre = ttk.Entry(tab_servicios, width=35)
    entrada_nombre.grid(row=1, column=1, padx=5)
    # Campo para escribir la tarifa por hora
    ttk.Label(tab_servicios, text="Tarifa por hora").grid(row=2, column=0, sticky="w", padx=5, pady=3)
    entrada_tarifa = ttk.Entry(tab_servicios, width=35)
    entrada_tarifa.grid(row=2, column=1, padx=5)
    # Campo extra: cambia según el tipo (capacidad, unidades o nivel)
    etiqueta_extra = ttk.Label(tab_servicios, text="Capacidad (número)")
    etiqueta_extra.grid(row=3, column=0, sticky="w", padx=5, pady=3)
    entrada_extra = ttk.Entry(tab_servicios, width=35)
    entrada_extra.grid(row=3, column=1, padx=5)
    # Casilla para marcar si el servicio está disponible o no
    disponible = tk.BooleanVar(value=True)
    ttk.Checkbutton(tab_servicios, text="Disponible", variable=disponible).grid(row=4, column=1, sticky="w", padx=5)
    # Lista donde se muestran los servicios creados
    lista_servicios = tk.Listbox(tab_servicios, width=80, height=8)
    lista_servicios.grid(row=6, column=0, columnspan=2, padx=5, pady=8)

    # Cambia el texto del campo extra cuando se escoge otro tipo de servicio
    def cambiar_tipo(evento):
        if tipo.get() == "Sala":
            etiqueta_extra.config(text="Capacidad (número)")
        elif tipo.get() == "Equipo":
            etiqueta_extra.config(text="Unidades (número)")
        else:
            etiqueta_extra.config(text="Nivel (junior/senior/experto)")

    # Cada vez que se cambia la opción de la lista se llama a cambiar_tipo
    tipo.bind("<<ComboboxSelected>>", cambiar_tipo)

    # Lo que pasa al presionar el botón "Crear servicio"
    def boton_crear_servicio():
        try:
            # Se leen los datos que escribió el usuario
            nombre = entrada_nombre.get()
            # La tarifa se pasa a número; si no es número da ValueError
            tarifa = float(entrada_tarifa.get())
            extra = entrada_extra.get().strip().lower()
            # Según el tipo se crea la clase de servicio que corresponde
            if tipo.get() == "Sala":
                servicio = ReservaSala(nombre, tarifa, int(extra), disponible.get())
            elif tipo.get() == "Equipo":
                servicio = AlquilerEquipo(nombre, tarifa, int(extra), disponible.get())
            else:
                servicio = AsesoriaEspecializada(nombre, tarifa, extra, disponible.get())
            # Si no hubo errores se guarda el servicio en la lista
            agregar_servicio(servicio)
        except (ErrorFJ, ValueError) as e:
            # Si algo falla se registra en el log y se muestra el error, sin cerrar el programa
            logging.error(f"Interfaz - error al crear servicio: {e}")
            messagebox.showerror("Error", "Datos inválidos: " + str(e))
        else:
            # Si todo salió bien se limpian los campos y se avisa
            entrada_nombre.delete(0, "end")
            entrada_tarifa.delete(0, "end")
            entrada_extra.delete(0, "end")
            messagebox.showinfo("Listo", "Servicio creado")
        finally:
            # Pase lo que pase se actualizan las listas en pantalla
            actualizar()

    # Botón que crea el servicio
    ttk.Button(tab_servicios, text="Crear servicio", command=boton_crear_servicio).grid(row=5, column=1, sticky="e", padx=5, pady=5)
     
 

if __name__ == "__main__":
    abrir_ventana()


