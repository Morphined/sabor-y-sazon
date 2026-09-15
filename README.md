# Sabor & Sazón — Control Gastronómico

Aplicación de escritorio desarrollada en **Python 3.12** con **Tkinter** para registrar clientes, seleccionar un servicio gastronómico y calcular automáticamente el valor total de acuerdo con el tipo de menú y el número de sesiones.

## Características

- Acceso mediante contraseña enmascarada.
- Registro de identificación, nombre, género y fecha automática.
- Selección de menú mediante lista desplegable.
- Costo por sesión asignado automáticamente.
- Cálculo del costo total por número de sesiones.
- Reporte emergente con el resumen completo del servicio.
- Validaciones de entrada y mensajes de confirmación.
- Interfaz adaptable a distintas resoluciones.
- Identidad visual propia con logo e icono de aplicación.
- Sin dependencias externas de interfaz.

## Menús disponibles

| Menú | Costo por sesión |
|---|---:|
| Ejecutivo | $35.000 COP |
| Vegetariano | $28.000 COP |
| Degustación | $75.000 COP |
| Infantil | $20.000 COP |
| Gourmet | $95.000 COP |

## Requisitos

- Python 3.12
- Tkinter

En Windows, Tkinter normalmente se instala junto con Python.

## Ejecución

```bash
python main.py
```

La contraseña de demostración configurada es `1793`.

## Estructura del proyecto

```text
.
├── main.py
├── modelo.py
├── configuracion.py
├── validaciones.py
├── assets/
│   ├── logo.png
│   ├── app_icon.png
│   └── app.ico
└── tests/
    └── test_modelo.py
```

## Arquitectura

- `main.py`: interfaz gráfica y flujo de navegación.
- `modelo.py`: modelo `GestionClientes` y cálculo del servicio.
- `configuracion.py`: precios, contraseña y paleta visual.
- `validaciones.py`: validaciones de los datos de entrada.
- `tests/test_modelo.py`: prueba automática del cálculo.

## Atajos

- `Ctrl+S`: guardar registro.
- `Ctrl+R`: calcular y mostrar reporte.
- `Esc`: cerrar el reporte.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Autor

Juan Fernando Capitani Giraldo
