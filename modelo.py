from dataclasses import dataclass
from datetime import datetime


@dataclass
class GestionClientes:
    """Modelo público solicitado para almacenar y procesar los datos del cliente."""

    identificacion: str
    nombre_completo: str
    genero: str
    tipo_menu: str
    numero_sesiones: int
    fecha_registro: datetime
    costo_por_sesion: int
    costo_total: int = 0

    def calcular_costo_total(self, numero_sesiones: int, costo_por_sesion: int) -> int:
        self.costo_total = numero_sesiones * costo_por_sesion
        return self.costo_total
