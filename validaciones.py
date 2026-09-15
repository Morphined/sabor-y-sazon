class ValidadorCliente:
    """Agrupa las reglas de validación para mantener la interfaz separada de la lógica."""

    @staticmethod
    def solo_digitos(valor: str) -> bool:
        return valor == "" or valor.isdigit()

    @staticmethod
    def nombre_parcial_valido(valor: str) -> bool:
        if valor == "":
            return True
        permitidos = " áéíóúÁÉÍÓÚñÑ'-"
        return all(c.isalpha() or c in permitidos for c in valor)

    @staticmethod
    def validar(identificacion: str, nombre: str, menu: str, sesiones: str) -> tuple[bool, str]:
        identificacion = identificacion.strip()
        nombre = " ".join(nombre.split())
        sesiones = sesiones.strip()

        if not identificacion:
            return False, "Ingrese la identificación del cliente."
        if not identificacion.isdigit():
            return False, "La identificación debe contener únicamente números."
        if len(identificacion) < 5:
            return False, "La identificación debe tener al menos 5 dígitos."
        if not nombre:
            return False, "Ingrese el nombre completo del cliente."
        if len(nombre.split()) < 2:
            return False, "Ingrese por lo menos nombre y apellido."
        if not menu:
            return False, "Seleccione un tipo de menú."
        if not sesiones:
            return False, "Ingrese el número de sesiones gastronómicas."
        if not sesiones.isdigit() or int(sesiones) <= 0:
            return False, "El número de sesiones debe ser un entero positivo."
        if int(sesiones) > 999:
            return False, "El número de sesiones no puede superar 999."
        return True, ""
