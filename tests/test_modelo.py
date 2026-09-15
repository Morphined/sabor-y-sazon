import unittest
from datetime import datetime

from modelo import GestionClientes


class TestGestionClientes(unittest.TestCase):
    def test_calculo_servicio(self):
        cliente = GestionClientes(
            identificacion="1020793006",
            nombre_completo="Juan Fernando Capitani Giraldo",
            genero="Masculino",
            tipo_menu="Menú vegetariano",
            numero_sesiones=4,
            fecha_registro=datetime.now(),
            costo_por_sesion=28000,
        )
        self.assertEqual(cliente.calcular_costo_total(4, 28000), 112000)
        self.assertEqual(cliente.costo_total, 112000)


if __name__ == "__main__":
    unittest.main()
