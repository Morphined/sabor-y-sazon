from __future__ import annotations

import ctypes
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Literal, TypeAlias

from configuracion import (
    ACENTO,
    ACENTO_SUAVE,
    AUTOR,
    BORDE,
    CLAVE_ACCESO,
    ERROR,
    EXITO,
    FONDO,
    GRUPO,
    NOMBRE_APLICACION,
    PANEL,
    PRECIOS_MENU,
    PRIMARIO,
    PRIMARIO_OSCURO,
    TEXTO,
    TEXTO_SUAVE,
)
from modelo import GestionClientes
from validaciones import ValidadorCliente

VentanaTk: TypeAlias = tk.Tk | tk.Toplevel
PadreTk: TypeAlias = tk.Misc | tk.Tk | tk.Toplevel
EstadoEntry: TypeAlias = Literal["normal", "disabled", "readonly"]

SOMBRA_TARJETA = "#D0DEDA"
DESPLAZAMIENTO_SOMBRA = 3



def moneda_cop(valor: int) -> str:
    return f"$ {valor:,.0f}".replace(",", ".")



def configurar_dpi_windows() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "UNAD.EstructuraDatos.Grupo229.SaborSazon.V4"
        )
    except Exception:
        pass


class AplicacionSaborSazon:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.raiz.title(NOMBRE_APLICACION)
        self.raiz.configure(bg=FONDO)
        self.raiz.protocol("WM_DELETE_WINDOW", self.confirmar_salida)

        self.cliente_actual: GestionClientes | None = None
        self.ancho_pantalla = self.raiz.winfo_screenwidth()
        self.alto_pantalla = self.raiz.winfo_screenheight()
        self.modo_compacto = self.ancho_pantalla < 1280 or self.alto_pantalla < 780

        self.logo_grande = self._cargar_imagen("logo.png")
        self.logo_mediano = self.logo_grande.subsample(3, 3) if self.logo_grande else None
        self.logo_pequeno = self.logo_grande.subsample(4, 4) if self.logo_grande else None
        self.icono_app = self._cargar_imagen("app_icon.png")
        self._aplicar_icono(self.raiz)
        self._configurar_estilos()
        self.mostrar_acceso()

    # -------------------- Infraestructura visual --------------------
    def _cargar_imagen(self, nombre: str) -> tk.PhotoImage | None:
        ruta = os.path.join(self.base_dir, "assets", nombre)
        try:
            return tk.PhotoImage(file=ruta)
        except tk.TclError:
            return None

    def _aplicar_icono(self, ventana: VentanaTk) -> None:
        if self.icono_app is not None:
            try:
                ventana.iconphoto(True, self.icono_app)
            except tk.TclError:
                pass
        if sys.platform == "win32":
            ruta_ico = os.path.join(self.base_dir, "assets", "app.ico")
            try:
                ventana.iconbitmap(ruta_ico)
            except tk.TclError:
                pass

    def _dimensionar_ventana(
        self,
        ventana: VentanaTk,
        ancho_objetivo: int,
        alto_objetivo: int,
        ancho_minimo: int,
        alto_minimo: int,
    ) -> None:
        ventana.update_idletasks()
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()

        max_ancho = max(620, ancho_pantalla - 60)
        max_alto = max(500, alto_pantalla - 100)
        ancho = min(ancho_objetivo, max_ancho)
        alto = min(alto_objetivo, max_alto)

        try:
            ventana.minsize(min(ancho_minimo, ancho), min(alto_minimo, alto))
        except tk.TclError:
            pass

        x = max(0, (ancho_pantalla - ancho) // 2)
        y = max(0, (alto_pantalla - alto) // 2 - 12)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Accion.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(22, 11),
            foreground="white",
            background=PRIMARIO,
            borderwidth=0,
        )
        estilo.map("Accion.TButton", background=[("active", PRIMARIO_OSCURO)])

        estilo.configure(
            "Suave.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(22, 11),
            foreground=PRIMARIO,
            background=ACENTO,
            borderwidth=0,
        )
        estilo.map("Suave.TButton", background=[("active", BORDE)])

        estilo.configure(
            "Salir.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(22, 11),
            foreground="white",
            background=ERROR,
            borderwidth=0,
        )
        estilo.map("Salir.TButton", background=[("active", "#702323")])

        # Estilos exclusivos de la vista de acceso para reforzar la jerarquía.
        estilo.configure(
            "AccesoPrincipal.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(28, 12),
            foreground="white",
            background=PRIMARIO,
            borderwidth=0,
        )
        estilo.map("AccesoPrincipal.TButton", background=[("active", PRIMARIO_OSCURO)])

        estilo.configure(
            "AccesoSuave.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 12),
            foreground=PRIMARIO,
            background=ACENTO,
            borderwidth=0,
        )
        estilo.map("AccesoSuave.TButton", background=[("active", BORDE)])

        estilo.configure(
            "TCombobox",
            padding=7,
            arrowsize=15,
            fieldbackground="white",
        )

    def _vaciar_raiz(self) -> None:
        for evento in ("<Control-s>", "<Control-r>", "<Escape>"):
            self.raiz.unbind(evento)
        for elemento in self.raiz.winfo_children():
            elemento.destroy()

    def _cabecera(self, padre: PadreTk, titulo: str, descripcion: str) -> tk.Frame:
        altura = 96 if self.modo_compacto else 112
        cabecera = tk.Frame(padre, bg=PANEL, height=altura, highlightbackground=BORDE, highlightthickness=0)
        cabecera.grid(row=0, column=0, sticky="ew")
        cabecera.grid_propagate(False)
        cabecera.columnconfigure(1, weight=1)

        marca = tk.Frame(cabecera, bg=PANEL)
        marca.grid(row=0, column=0, rowspan=2, sticky="w", padx=(24, 10), pady=12)
        if self.logo_mediano is not None:
            tk.Label(marca, image=self.logo_mediano, bg=PANEL).pack(side="left")
        else:
            tk.Label(
                marca,
                text="S&S",
                font=("Georgia", 18, "bold"),
                bg=PANEL,
                fg=PRIMARIO,
            ).pack(side="left")

        tk.Label(
            cabecera,
            text=titulo,
            font=("Segoe UI Semibold", 18 if self.modo_compacto else 21),
            bg=PANEL,
            fg=TEXTO,
        ).grid(row=0, column=1, sticky="sw", pady=(16, 0))

        tk.Label(
            cabecera,
            text=descripcion,
            font=("Segoe UI", 9 if self.modo_compacto else 10),
            bg=PANEL,
            fg=TEXTO_SUAVE,
        ).grid(row=1, column=1, sticky="nw", pady=(3, 16))

        insignia = tk.Frame(cabecera, bg=ACENTO, highlightbackground=BORDE, highlightthickness=1)
        insignia.grid(row=0, column=2, rowspan=2, padx=(12, 24), pady=18, sticky="e")
        tk.Label(
            insignia,
            text=f"GRUPO {GRUPO}",
            font=("Segoe UI", 9, "bold"),
            bg=ACENTO,
            fg=PRIMARIO,
            padx=12,
            pady=5,
        ).pack()

        # Línea divisora para reforzar la jerarquía entre cabecera y contenido.
        tk.Frame(cabecera, bg=PRIMARIO, height=3).place(
            relx=0, rely=1, relwidth=1, height=3, anchor="sw"
        )
        return cabecera

    def _pie(self, padre: PadreTk, texto: str) -> tk.Frame:
        pie = tk.Frame(padre, bg=FONDO)
        tk.Label(
            pie,
            text=texto,
            font=("Segoe UI", 8),
            bg=FONDO,
            fg=PRIMARIO,
        ).pack(side="left")
        tk.Label(
            pie,
            text="Python 3.12",
            font=("Segoe UI", 8, "bold"),
            bg=FONDO,
            fg=PRIMARIO,
        ).pack(side="right")
        return pie

    def _tarjeta(self, padre: PadreTk, bg: str = PANEL, padx: int = 22, pady: int = 20) -> tk.Frame:
        """Crea una tarjeta con una sombra suave simulada desplazada 3 px."""
        sombra = tk.Frame(padre, bg=SOMBRA_TARJETA, bd=0, highlightthickness=0)
        tarjeta = tk.Frame(padre, bg=bg, highlightbackground=BORDE, highlightthickness=1)
        tarjeta.configure(padx=padx, pady=pady)

        def sincronizar_sombra(_event=None) -> None:
            if not tarjeta.winfo_exists():
                return
            ancho = tarjeta.winfo_width()
            alto = tarjeta.winfo_height()
            if ancho <= 1 or alto <= 1:
                return
            sombra.place(
                x=tarjeta.winfo_x() + DESPLAZAMIENTO_SOMBRA,
                y=tarjeta.winfo_y() + DESPLAZAMIENTO_SOMBRA,
                width=ancho,
                height=alto,
            )
            sombra.lower(tarjeta)

        def destruir_sombra(_event=None) -> None:
            if sombra.winfo_exists():
                sombra.destroy()

        tarjeta.bind("<Configure>", sincronizar_sombra, add="+")
        tarjeta.bind("<Destroy>", destruir_sombra, add="+")
        return tarjeta

    def _titulo_seccion(self, padre: PadreTk, texto: str, subtitulo: str | None = None) -> None:
        tk.Label(
            padre,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg=padre.cget("bg"),
            fg=PRIMARIO,
        ).pack(anchor="w")
        if subtitulo:
            tk.Label(
                padre,
                text=subtitulo,
                font=("Segoe UI", 8 if self.modo_compacto else 9),
                bg=padre.cget("bg"),
                fg=TEXTO_SUAVE,
            ).pack(anchor="w", pady=(2, 0))
        tk.Frame(padre, bg=BORDE, height=1).pack(fill="x", pady=(9, 0))

    # -------------------- Vista 1: Acceso --------------------
    def mostrar_acceso(self) -> None:
        self._vaciar_raiz()
        self._dimensionar_ventana(self.raiz, 860, 560, 740, 520)
        self.raiz.rowconfigure(1, weight=1)
        self.raiz.columnconfigure(0, weight=1)

        self._cabecera(
            self.raiz,
            NOMBRE_APLICACION,
            f"Autor: {AUTOR}",
        )

        marco = tk.Frame(self.raiz, bg=FONDO)
        marco.grid(row=1, column=0, sticky="nsew", padx=28, pady=(18, 10))
        marco.columnconfigure(0, weight=1)
        marco.columnconfigure(1, weight=1)
        marco.rowconfigure(0, weight=1)

        bienvenida = self._tarjeta(marco, bg=PANEL, padx=28, pady=28)
        bienvenida.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        bienvenida.columnconfigure(0, weight=1)

        if self.logo_grande is not None:
            tk.Label(bienvenida, image=self.logo_grande, bg=PANEL).grid(row=0, column=0, sticky="w")
        tk.Label(
            bienvenida,
            text="Bienvenido",
            font=("Segoe UI Semibold", 22),
            bg=PANEL,
            fg=TEXTO,
        ).grid(row=1, column=0, sticky="w", pady=(14, 2))
        tk.Label(
            bienvenida,
            text="Sistema de registro gastronómico del restaurante Sabor & Sazón.",
            font=("Segoe UI", 10),
            bg=PANEL,
            fg=TEXTO_SUAVE,
            wraplength=300,
            justify="left",
        ).grid(row=2, column=0, sticky="w")

        info = tk.Frame(bienvenida, bg=ACENTO_SUAVE, highlightbackground=BORDE, highlightthickness=1)
        info.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        tk.Label(
            info,
            text="La aplicación valida el acceso y luego permite registrar al cliente, calcular el costo total y visualizar el reporte.",
            font=("Segoe UI", 9),
            bg=ACENTO_SUAVE,
            fg=TEXTO,
            wraplength=300,
            justify="left",
            padx=14,
            pady=14,
        ).pack(fill="x")

        acceso = self._tarjeta(marco, bg=PANEL, padx=28, pady=28)
        acceso.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        acceso.columnconfigure(0, weight=1)
        tk.Label(
            acceso,
            text="Acceso seguro",
            font=("Segoe UI", 18, "bold"),
            bg=PANEL,
            fg=TEXTO,
        ).grid(row=0, column=0, pady=(0, 6))
        tk.Label(
            acceso,
            text="Digite la contraseña genérica para habilitar el formulario de registro.",
            font=("Segoe UI", 10),
            bg=PANEL,
            fg=TEXTO_SUAVE,
            wraplength=300,
            justify="center",
        ).grid(row=1, column=0, pady=(0, 18))

        self.clave = tk.StringVar()
        entrada = tk.Entry(
            acceso,
            textvariable=self.clave,
            show="•",
            justify="center",
            font=("Segoe UI", 16),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDE,
            highlightcolor=PRIMARIO,
        )
        entrada.grid(row=2, column=0, sticky="ew", ipady=14)
        entrada.focus_set()
        entrada.bind("<Return>", lambda _e: self.validar_acceso())

        tk.Label(
            acceso,
            text="La clave se muestra enmascarada por seguridad.",
            font=("Segoe UI", 8, "italic"),
            bg=PANEL,
            fg=TEXTO_SUAVE,
        ).grid(row=3, column=0, pady=(10, 0))

        acciones = tk.Frame(acceso, bg=PANEL)
        acciones.grid(row=4, column=0, pady=(22, 0))
        ttk.Button(
            acciones,
            text="Ingresar",
            style="AccesoPrincipal.TButton",
            command=self.validar_acceso,
        ).pack(side="left", padx=6)
        ttk.Button(
            acciones,
            text="Cerrar",
            style="AccesoSuave.TButton",
            command=self.confirmar_salida,
        ).pack(side="left", padx=6)

        pie = self._pie(self.raiz, "Fase 2 · Fundamentos de Abstracción y Modelado de Datos")
        pie.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 10))

    def validar_acceso(self) -> None:
        if self.clave.get() == CLAVE_ACCESO:
            messagebox.showinfo(
                "Acceso autorizado",
                "Contraseña correcta. Puede continuar con el registro.",
                parent=self.raiz,
            )
            self.mostrar_registro()
        else:
            messagebox.showerror(
                "Acceso no autorizado",
                "La contraseña ingresada no es válida.",
                parent=self.raiz,
            )
            self.clave.set("")

    # -------------------- Vista 2: Registro --------------------
    def mostrar_registro(self) -> None:
        self._vaciar_raiz()
        self._dimensionar_ventana(self.raiz, 1180, 760, 940, 640)
        self.raiz.rowconfigure(1, weight=1)
        self.raiz.columnconfigure(0, weight=1)
        self._cabecera(
            self.raiz,
            "Registro gastronómico",
            "Ingrese los datos del cliente y seleccione el servicio gastronómico.",
        )

        self.identificacion = tk.StringVar()
        self.nombre = tk.StringVar()
        self.genero = tk.StringVar(value="Masculino")
        self.menu = tk.StringVar()
        self.sesiones = tk.StringVar()
        self.fecha = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.costo = tk.StringVar(value="Seleccione un menú")

        contenedor = tk.Frame(self.raiz, bg=FONDO)
        contenedor.grid(row=1, column=0, sticky="nsew", padx=28, pady=(16, 8))
        contenedor.rowconfigure(0, weight=1)

        if self.modo_compacto:
            contenedor.columnconfigure(0, weight=1)
            form_col, side_col = 0, 0
            form_padx = 0
            side_padx = 0
            side_pady = (14, 0)
        else:
            contenedor.columnconfigure(0, weight=3)
            contenedor.columnconfigure(1, weight=2)
            form_col, side_col = 0, 1
            form_padx = (0, 12)
            side_padx = (12, 0)
            side_pady = 0

        tarjeta_form = self._tarjeta(contenedor, bg=PANEL, padx=24, pady=20)
        tarjeta_form.grid(row=0, column=form_col, sticky="nsew", padx=form_padx, pady=0)
        tarjeta_form.columnconfigure(1, weight=1)
        tarjeta_form.columnconfigure(3, weight=1)

        validar_id = (self.raiz.register(ValidadorCliente.solo_digitos), "%P")
        validar_nombre = (self.raiz.register(ValidadorCliente.nombre_parcial_valido), "%P")

        self._subtitulo_en_grid(tarjeta_form, "Datos del cliente", "Información principal del participante.", 0)
        self._label(tarjeta_form, "Identificación", 2, 0)
        self.entrada_identificacion = self._entry(tarjeta_form, self.identificacion, 2, 1, validar=validar_id)
        self._label(tarjeta_form, "Nombre completo", 2, 2)
        self._entry(tarjeta_form, self.nombre, 2, 3, validar=validar_nombre)

        self._label(tarjeta_form, "Género", 3, 0)
        zona_genero = tk.Frame(tarjeta_form, bg=PANEL)
        zona_genero.grid(row=3, column=1, sticky="w", padx=10, pady=self._pady_campo())
        self._toggle_genero(zona_genero)

        self._label(tarjeta_form, "Fecha de registro", 3, 2)
        entrada_fecha = self._entry(tarjeta_form, self.fecha, 3, 3, estado="readonly")
        entrada_fecha.configure(
            readonlybackground=ACENTO_SUAVE,
            fg=TEXTO_SUAVE,
            disabledforeground=TEXTO_SUAVE,
        )

        self._subtitulo_en_grid(tarjeta_form, "Servicio gastronómico", "Seleccione el menú y la cantidad de sesiones.", 4)
        self._label(tarjeta_form, "Tipo de menú", 6, 0)
        selector = ttk.Combobox(
            tarjeta_form,
            textvariable=self.menu,
            values=list(PRECIOS_MENU),
            state="readonly",
            font=("Segoe UI", 10),
        )
        selector.grid(row=6, column=1, sticky="ew", padx=(8, 24), pady=self._pady_campo())
        selector.bind("<<ComboboxSelected>>", self.actualizar_precio)
        selector.bind("<<ComboboxSelected>>", self.actualizar_resumen, add="+")

        self._label(tarjeta_form, "Número de sesiones", 6, 2)
        entrada_sesiones = self._entry(tarjeta_form, self.sesiones, 6, 3, validar=validar_id)
        entrada_sesiones.bind("<KeyRelease>", self.actualizar_resumen)

        self._label(tarjeta_form, "Costo por sesión", 7, 0)
        entrada_costo = self._entry(tarjeta_form, self.costo, 7, 1, estado="readonly")
        entrada_costo.configure(readonlybackground="#FAF7F4", fg=PRIMARIO)
        tk.Label(
            tarjeta_form,
            text="Se asigna automáticamente de acuerdo con el menú seleccionado.",
            font=("Segoe UI", 9, "italic"),
            bg=PANEL,
            fg=TEXTO_SUAVE,
        ).grid(row=7, column=2, columnspan=2, sticky="w", padx=12)

        acciones = tk.Frame(tarjeta_form, bg=PANEL)
        acciones.grid(row=8, column=0, columnspan=4, pady=(20, 4))
        ttk.Button(acciones, text="Guardar registro", style="Accion.TButton", command=self.guardar_registro).pack(side="left", padx=5)
        ttk.Button(acciones, text="Calcular / Mostrar reporte", style="Suave.TButton", command=self.mostrar_reporte).pack(side="left", padx=5)
        ttk.Button(acciones, text="Salir", style="Salir.TButton", command=self.confirmar_salida).pack(
            side="left", padx=(20, 5)
        )

        # Panel lateral de resumen
        lateral = tk.Frame(contenedor, bg=FONDO)
        lateral.grid(row=0 if not self.modo_compacto else 1, column=side_col, sticky="nsew", padx=side_padx, pady=side_pady)
        lateral.columnconfigure(0, weight=1)
        lateral.rowconfigure(1, weight=1)

        tarjeta_marca = self._tarjeta(lateral, bg=PRIMARIO, padx=22, pady=20)
        tarjeta_marca.grid(row=0, column=0, sticky="ew")
        tarjeta_marca.columnconfigure(1, weight=1)
        if self.logo_mediano is not None:
            tk.Label(tarjeta_marca, image=self.logo_mediano, bg=PRIMARIO).grid(row=0, column=0, rowspan=2, padx=(0, 14))
        tk.Label(
            tarjeta_marca,
            text="Sabor & Sazón",
            font=("Segoe UI Semibold", 16),
            bg=PRIMARIO,
            fg="white",
        ).grid(row=0, column=1, sticky="w")
        tk.Label(
            tarjeta_marca,
            text="Control gastronómico del servicio al cliente.",
            font=("Segoe UI", 9),
            bg=PRIMARIO,
            fg="#F8EEE8",
            wraplength=250,
            justify="left",
        ).grid(row=1, column=1, sticky="w", pady=(4, 0))

        tarjeta_resumen = self._tarjeta(lateral, bg=PANEL, padx=22, pady=20)
        tarjeta_resumen.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        self._titulo_seccion(tarjeta_resumen, "Resumen del servicio", "Vista rápida del cálculo actual.")

        cuerpo = tk.Frame(tarjeta_resumen, bg=PANEL)
        cuerpo.pack(fill="both", expand=True, pady=(16, 0))
        cuerpo.columnconfigure(1, weight=1)

        self.resumen_menu = tk.StringVar(value="Sin selección")
        self.resumen_sesiones = tk.StringVar(value="0")
        self.resumen_costo = tk.StringVar(value="$ 0")
        self.resumen_total = tk.StringVar(value="$ 0")

        self._fila_resumen(cuerpo, 0, "Menú", self.resumen_menu)
        self._fila_resumen(cuerpo, 1, "Sesiones", self.resumen_sesiones)
        self._fila_resumen(cuerpo, 2, "Costo por sesión", self.resumen_costo)
        self._fila_resumen(cuerpo, 3, "Total estimado", self.resumen_total, destacado=True)

        ayuda = tk.Frame(tarjeta_resumen, bg=ACENTO_SUAVE, highlightbackground=BORDE, highlightthickness=1)
        ayuda.pack(fill="x", pady=(18, 0))
        tk.Label(
            ayuda,
            text="Un registro corresponde a un solo tipo de menú. El total se calcula multiplicando el número de sesiones por el costo de la sesión seleccionada.",
            font=("Segoe UI", 8 if self.modo_compacto else 9),
            bg=ACENTO_SUAVE,
            fg=TEXTO,
            wraplength=280,
            justify="left",
            padx=12,
            pady=12,
        ).pack(fill="x")

        pie = self._pie(self.raiz, "Ctrl+S: guardar · Ctrl+R: reporte")
        pie.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 8))

        self.raiz.bind("<Control-s>", lambda _e: self.guardar_registro())
        self.raiz.bind("<Control-r>", lambda _e: self.mostrar_reporte())
        self.entrada_identificacion.focus_set()
        self.actualizar_resumen()

    def _subtitulo_en_grid(self, padre: PadreTk, titulo: str, subtitulo: str, fila: int) -> None:
        barra = tk.Frame(padre, bg=ACENTO_SUAVE, highlightthickness=0)
        barra.grid(
            row=fila,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=4,
            pady=(5, 8),
        )
        barra.columnconfigure(1, weight=1)

        # Borde izquierdo de 3 px para marcar visualmente cada sección.
        tk.Frame(barra, bg=PRIMARIO, width=3).grid(row=0, column=0, rowspan=2, sticky="ns")

        contenido = tk.Frame(barra, bg=ACENTO_SUAVE, padx=10, pady=8)
        contenido.grid(row=0, column=1, rowspan=2, sticky="ew")
        tk.Label(
            contenido,
            text=titulo.upper(),
            font=("Segoe UI", 9, "bold"),
            bg=ACENTO_SUAVE,
            fg=PRIMARIO,
        ).pack(anchor="w")
        tk.Label(
            contenido,
            text=subtitulo,
            font=("Segoe UI", 8 if self.modo_compacto else 9),
            bg=ACENTO_SUAVE,
            fg=TEXTO_SUAVE,
        ).pack(anchor="w", pady=(2, 0))

    def _toggle_genero(self, zona: tk.Frame) -> None:
        opciones = ("Masculino", "Femenino")
        self._btns_genero: dict[str, tk.Label] = {}
        for opcion in opciones:
            btn = tk.Label(
                zona,
                text=opcion,
                font=("Segoe UI", 10),
                padx=14,
                pady=6,
                cursor="hand2",
                relief="solid",
                bd=1,
            )
            btn.pack(side="left", padx=(0, 8))
            btn.bind("<Button-1>", lambda _e, op=opcion: self._seleccionar_genero(op))
            self._btns_genero[opcion] = btn
        self._seleccionar_genero("Masculino")

    def _seleccionar_genero(self, opcion: str) -> None:
        self.genero.set(opcion)
        for op, btn in self._btns_genero.items():
            if op == opcion:
                btn.configure(
                    bg=PRIMARIO,
                    fg="white",
                    highlightbackground=PRIMARIO,
                    highlightthickness=1,
                )
            else:
                btn.configure(
                    bg=PANEL,
                    fg=TEXTO,
                    highlightbackground=BORDE,
                    highlightthickness=1,
                )

    def _pady_campo(self) -> int:
        return 7 if self.modo_compacto else 10

    def _label(self, padre: PadreTk, texto: str, fila: int, columna: int) -> None:
        tk.Label(
            padre,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg=PANEL,
            fg=TEXTO,
        ).grid(
            row=fila,
            column=columna,
            sticky="w",
            padx=(4 if columna == 0 else 14, 6),
            pady=self._pady_campo(),
        )

    def _entry(
        self,
        padre: PadreTk,
        variable: tk.StringVar,
        fila: int,
        columna: int,
        estado: EstadoEntry = "normal",
        validar=None,
    ) -> tk.Entry:
        entrada = tk.Entry(
            padre,
            textvariable=variable,
            state=estado,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDE,
            highlightcolor=PRIMARIO,
        )
        if validar is not None:
            entrada.configure(validate="key", validatecommand=validar)
        entrada.grid(
            row=fila,
            column=columna,
            sticky="ew",
            padx=(8, 24),
            pady=self._pady_campo(),
            ipady=5 if self.modo_compacto else 6,
        )
        return entrada

    def _fila_resumen(
        self,
        padre: PadreTk,
        fila: int,
        nombre: str,
        variable: tk.StringVar,
        destacado: bool = False,
    ) -> None:
        # Cada fila usa dos renglones del grid: contenido + separador.
        fila_contenido = fila * 2
        fila_separador = fila_contenido + 1

        if destacado:
            tk.Frame(padre, bg=ACENTO, height=2).grid(
                row=fila_contenido,
                column=0,
                columnspan=2,
                sticky="ew",
                pady=(8, 8),
            )
            fila_contenido += 1
            fila_separador += 1

        tk.Label(
            padre,
            text=nombre,
            font=("Segoe UI", 9, "bold"),
            bg=PANEL,
            fg=TEXTO_SUAVE,
        ).grid(row=fila_contenido, column=0, sticky="w", pady=7)
        tk.Label(
            padre,
            textvariable=variable,
            font=("Segoe UI", 10 if not destacado else 14, "bold" if destacado else "normal"),
            bg=PANEL,
            fg=PRIMARIO_OSCURO if destacado else TEXTO,
        ).grid(row=fila_contenido, column=1, sticky="e", pady=7)

        if not destacado:
            tk.Frame(padre, bg=BORDE, height=1).grid(
                row=fila_separador,
                column=0,
                columnspan=2,
                sticky="ew",
                pady=(0, 0),
            )

    def actualizar_precio(self, _event=None) -> None:
        precio = PRECIOS_MENU.get(self.menu.get())
        self.costo.set(moneda_cop(precio) if precio is not None else "Seleccione un menú")

    def actualizar_resumen(self, _event=None) -> None:
        menu = self.menu.get().strip() or "Sin selección"
        sesiones_txt = self.sesiones.get().strip() or "0"
        try:
            sesiones_num = int(sesiones_txt)
        except ValueError:
            sesiones_num = 0
        precio = PRECIOS_MENU.get(self.menu.get(), 0)
        total = sesiones_num * precio

        self.resumen_menu.set(menu)
        self.resumen_sesiones.set(str(sesiones_num))
        self.resumen_costo.set(moneda_cop(precio))
        self.resumen_total.set(moneda_cop(total))

    def construir_cliente(self) -> GestionClientes | None:
        valido, mensaje = ValidadorCliente.validar(
            self.identificacion.get(),
            self.nombre.get(),
            self.menu.get(),
            self.sesiones.get(),
        )
        if not valido:
            messagebox.showwarning("Verifique los datos", mensaje, parent=self.raiz)
            return None

        menu = self.menu.get()
        cliente = GestionClientes(
            identificacion=self.identificacion.get().strip(),
            nombre_completo=" ".join(self.nombre.get().split()),
            genero=self.genero.get(),
            tipo_menu=menu,
            numero_sesiones=int(self.sesiones.get()),
            fecha_registro=datetime.now(),
            costo_por_sesion=PRECIOS_MENU[menu],
        )
        cliente.calcular_costo_total(cliente.numero_sesiones, cliente.costo_por_sesion)
        return cliente

    def guardar_registro(self) -> None:
        cliente = self.construir_cliente()
        if cliente is None:
            return
        self.cliente_actual = cliente
        self.fecha.set(cliente.fecha_registro.strftime("%d/%m/%Y %H:%M"))
        self.actualizar_resumen()
        messagebox.showinfo(
            "Registro almacenado",
            "La información fue guardada correctamente en GestionClientes.",
            parent=self.raiz,
        )

    # -------------------- Vista 3: Reporte --------------------
    def mostrar_reporte(self) -> None:
        cliente = self.construir_cliente()
        if cliente is None:
            return
        self.cliente_actual = cliente
        self.fecha.set(cliente.fecha_registro.strftime("%d/%m/%Y %H:%M"))
        self.actualizar_resumen()

        reporte = tk.Toplevel(self.raiz)
        reporte.title("Reporte del servicio")
        reporte.configure(bg=FONDO)
        reporte.transient(self.raiz)
        reporte.grab_set()
        reporte.columnconfigure(0, weight=1)
        reporte.rowconfigure(1, weight=1)
        self._aplicar_icono(reporte)
        self._dimensionar_ventana(reporte, 760, 720, 620, 620)

        self._cabecera(reporte, "Reporte del servicio", "Resumen del cliente y valor total a pagar.")

        panel = self._tarjeta(reporte, bg=PANEL, padx=24, pady=22)
        panel.grid(row=1, column=0, sticky="nsew", padx=28, pady=(16, 10))
        panel.columnconfigure(1, weight=1)

        if self.logo_pequeno is not None:
            tk.Label(panel, image=self.logo_pequeno, bg=PANEL).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        datos = [
            ("Identificación", cliente.identificacion),
            ("Nombre completo", cliente.nombre_completo),
            ("Género", cliente.genero),
            ("Tipo de menú", cliente.tipo_menu),
            ("Número de sesiones", str(cliente.numero_sesiones)),
            ("Fecha de registro", cliente.fecha_registro.strftime("%d/%m/%Y %H:%M")),
            ("Costo por sesión", moneda_cop(cliente.costo_por_sesion)),
        ]

        inicio = 1
        for indice, (nombre, valor) in enumerate(datos):
            fila = inicio + (indice * 2)
            tk.Label(
                panel,
                text=nombre,
                font=("Segoe UI", 10, "bold"),
                bg=PANEL,
                fg=TEXTO_SUAVE,
            ).grid(row=fila, column=0, sticky="w", padx=(6, 18), pady=(10, 2))
            tk.Label(
                panel,
                text=valor,
                font=("Segoe UI", 10),
                bg=PANEL,
                fg=TEXTO,
            ).grid(row=fila, column=1, sticky="w", padx=(0, 6), pady=(10, 2))

            if indice < len(datos) - 1:
                tk.Frame(panel, bg=BORDE, height=1).grid(
                    row=fila + 1,
                    column=0,
                    columnspan=2,
                    sticky="ew",
                    padx=6,
                    pady=(0, 0),
                )

        fila_total = inicio + (len(datos) * 2) - 1
        total_card = tk.Frame(
            panel,
            bg=PRIMARIO,
            highlightbackground=PRIMARIO,
            highlightthickness=1,
        )
        total_card.grid(
            row=fila_total,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(16, 10),
        )
        tk.Label(
            total_card,
            text="COSTO TOTAL DEL SERVICIO",
            font=("Segoe UI", 11, "bold"),
            bg=PRIMARIO,
            fg="white",
        ).pack(pady=(22, 4))
        tk.Label(
            total_card,
            text=moneda_cop(cliente.costo_total),
            font=("Segoe UI", 30, "bold"),
            bg=PRIMARIO,
            fg="white",
        ).pack(pady=(0, 4))
        tk.Label(
            total_card,
            text=f"{cliente.numero_sesiones} × {moneda_cop(cliente.costo_por_sesion)}",
            font=("Segoe UI", 9),
            bg=PRIMARIO,
            fg="#A8C8BF",
        ).pack(pady=(0, 22))

        acciones = tk.Frame(panel, bg=PANEL)
        acciones.grid(row=fila_total + 1, column=0, columnspan=2, pady=(6, 0))
        ttk.Button(
            acciones,
            text="Cerrar reporte",
            style="Suave.TButton",
            command=reporte.destroy,
        ).pack(side="left")

        reporte.bind("<Escape>", lambda _e: reporte.destroy())
        reporte.focus_force()

    def confirmar_salida(self) -> None:
        if messagebox.askyesno(
            "Confirmar salida",
            "¿Desea cerrar la aplicación?",
            parent=self.raiz,
        ):
            self.raiz.destroy()



def ejecutar_aplicacion() -> None:
    configurar_dpi_windows()
    raiz = tk.Tk()
    AplicacionSaborSazon(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    ejecutar_aplicacion()


# -----------------------------------------------------------------------------
# RESUMEN DE CAMBIOS VISUALES
# - _configurar_estilos: estilos especiales para botones de acceso y jerarquía.
# - _subtitulo_en_grid: secciones convertidas en barras con ACENTO_SUAVE y borde PRIMARIO.
# - mostrar_registro: género como toggles, fecha readonly diferenciada y separación del botón Salir.
# - _fila_resumen: separadores entre filas y acento superior para "Total estimado".
# - mostrar_reporte: filas separadas, bloque total en PRIMARIO, monto ampliado y cierre secundario.
# - mostrar_acceso: mantiene campo de contraseña prominente y botones con jerarquía diferenciada.
# - No se modificó la lógica de negocio, validaciones, modelo ni paleta definida en configuracion.py.
# -----------------------------------------------------------------------------
