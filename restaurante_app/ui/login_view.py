from pathlib import Path
import tkinter as tk
from tkinter import ttk

from servicios.restaurante_servicio import RestauranteServicio


class LoginView(ttk.Frame):
    """Vista de acceso a la aplicación."""

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio, al_iniciar_sesion):
        super().__init__(master, padding=24, style="App.TFrame")
        self.servicio = servicio
        self.al_iniciar_sesion = al_iniciar_sesion

        self.usuario_var = tk.StringVar()
        self.contrasena_var = tk.StringVar()
        self.mensaje_var = tk.StringVar()
        self._logo = None

        self._construir_interfaz()

    def _cargar_logo(self):
        ruta = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if ruta.exists():
            try:
                self._logo = tk.PhotoImage(file=str(ruta))
            except tk.TclError:
                self._logo = None
        return self._logo

    def _construir_interfaz(self) -> None:
        self.pack(fill="both", expand=True)

        contenedor = ttk.Frame(self, padding=34, style="Card.TFrame")
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        logo = self._cargar_logo()
        if logo is not None:
            ttk.Label(contenedor, image=logo, background="#FFFFFF").grid(
                row=0, column=0, columnspan=2, pady=(0, 16)
            )
        else:
            ttk.Label(contenedor, text="RESTAURANTE APP", style="Title.TLabel").grid(
                row=0, column=0, columnspan=2, pady=(0, 10)
            )

        ttk.Label(contenedor, text="Inicio de sesión", font=("Segoe UI", 13, "bold")).grid(
            row=1, column=0, columnspan=2, pady=(0, 22)
        )

        ttk.Label(contenedor, text="Usuario:").grid(
            row=2, column=0, sticky="w", padx=(0, 12), pady=8
        )
        usuario_entry = ttk.Entry(contenedor, textvariable=self.usuario_var, width=30)
        usuario_entry.grid(row=2, column=1, sticky="ew", pady=8)

        ttk.Label(contenedor, text="Contraseña:").grid(
            row=3, column=0, sticky="w", padx=(0, 12), pady=8
        )
        contrasena_entry = ttk.Entry(
            contenedor, textvariable=self.contrasena_var, show="*", width=30
        )
        contrasena_entry.grid(row=3, column=1, sticky="ew", pady=8)

        ttk.Button(
            contenedor,
            text="Ingresar",
            command=self._iniciar_sesion,
            style="Primary.TButton",
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(18, 8))

        ttk.Label(contenedor, textvariable=self.mensaje_var).grid(
            row=5, column=0, columnspan=2, pady=(6, 0)
        )

        contenedor.columnconfigure(1, weight=1)
        usuario_entry.bind("<Return>", lambda _event: contrasena_entry.focus_set())
        contrasena_entry.bind("<Return>", lambda _event: self._iniciar_sesion())
        usuario_entry.focus_set()

    def _iniciar_sesion(self) -> None:
        usuario = self.usuario_var.get().strip()
        contrasena = self.contrasena_var.get()
        if not usuario or not contrasena:
            self.mensaje_var.set("Ingrese usuario y contraseña.")
            return

        usuario_autenticado = self.servicio.autenticar_usuario(usuario, contrasena)
        if usuario_autenticado is not None:
            self.mensaje_var.set("")
            self.al_iniciar_sesion(usuario_autenticado)
            return

        self.mensaje_var.set("Usuario o contraseña incorrectos.")
        self.contrasena_var.set("")
