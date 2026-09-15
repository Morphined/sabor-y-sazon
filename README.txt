PROYECTO INDIVIDUAL – FASE 2 (VERSIÓN V3 VISUAL)
Curso: Estructura de Datos (301305)
Estudiante: Juan Fernando Capitani Giraldo
Grupo: 229
Aplicación: Sabor & Sazón - Control Gastronómico

REQUISITOS
- Python 3.12 (versión verificada para la entrega).
- Tkinter, incluido normalmente con Python para Windows.
- Visual Studio Code recomendado por la guía.
- No requiere paquetes externos.

EJECUCIÓN
1. Abra la carpeta en Visual Studio Code.
2. Seleccione Python 3.12.
3. Ejecute main.py.
4. Contraseña: 1793.

ESTRUCTURA
- main.py: controlador e interfaces gráficas adaptativas.
- modelo.py: clase pública GestionClientes.
- configuracion.py: constantes, precios y paleta visual.
- validaciones.py: reglas de validación de datos.
- assets/logo.png: logo de alta resolución.
- assets/app_icon.png y assets/app.ico: iconos de la aplicación y barra de tareas.
- tests/test_modelo.py: prueba del cálculo.

MEJORAS V3
- Ventanas centradas y dimensionadas automáticamente según la resolución disponible.
- Ajustes compactos para pantallas con menor altura o ancho.
- Compatibilidad con escalado DPI de Windows para mejorar nitidez.
- Icono propio en ventana y barra de tareas.
- Logo de mayor resolución y coherente con la identidad visual.
- Jerarquía visual por secciones: datos del cliente y servicio gastronómico.
- Identidad gráfica consistente en acceso, registro y reporte.
- Atajos Ctrl+S para guardar y Ctrl+R para abrir el reporte.
- Esc cierra el reporte.

FUNCIONALIDADES
- Acceso con contraseña enmascarada, sin usuario.
- Registro de identificación, nombre, género, menú y número de sesiones.
- Fecha automática.
- Costo por sesión automático y no editable.
- Gestión de datos mediante GestionClientes.
- Cálculo del costo total.
- Reporte emergente con la información completa.
- Validaciones y mensajes emergentes.
- Confirmación antes de salir.
- Diseño personalizado sin imagen de fondo.

PRUEBAS
Desde la terminal:
    python -m unittest discover -s tests -v


Revisión V3.1: se ajustaron las anotaciones de tipos para compatibilidad con Pylance en VS Code, sin modificar la lógica funcional.
