import tkinter as tk
from tkinter import ttk

from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView


class RestauranteApp:
    """Orquesta el servicio y las vistas de la aplicación."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurante App - Semana 16")
        self.root.geometry("1120x720")
        self.root.minsize(980, 640)
        self.root.configure(background="#F4F7FB")

        self.servicio = RestauranteServicio()
        self.vista_actual = None
        self.usuario_actual = None

        self._configurar_estilos()
        self._centrar_ventana()
        self.mostrar_login()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.root)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")

        estilo.configure("App.TFrame", background="#F4F7FB")
        estilo.configure("Header.TFrame", background="#17324D")
        estilo.configure("Nav.TFrame", background="#E8EEF5")
        estilo.configure("Card.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)

        estilo.configure(
            "Title.TLabel",
            background="#F4F7FB",
            foreground="#17324D",
            font=("Segoe UI", 20, "bold"),
        )
        estilo.configure(
            "HeaderTitle.TLabel",
            background="#17324D",
            foreground="#FFFFFF",
            font=("Segoe UI", 18, "bold"),
        )
        estilo.configure(
            "HeaderInfo.TLabel",
            background="#17324D",
            foreground="#DDEAF5",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Subtitle.TLabel",
            background="#F4F7FB",
            foreground="#566573",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Section.TLabel",
            background="#F4F7FB",
            foreground="#17324D",
            font=("Segoe UI", 16, "bold"),
        )
        estilo.configure(
            "Status.TLabel",
            background="#F4F7FB",
            foreground="#35526D",
            font=("Segoe UI", 10),
        )
        estilo.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))
        estilo.configure("Nav.TButton", font=("Segoe UI", 10), padding=(10, 8))
        estilo.configure("Danger.TButton", font=("Segoe UI", 10), padding=(10, 7))
        estilo.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    def _centrar_ventana(self) -> None:
        self.root.update_idletasks()
        ancho, alto = 1120, 720
        x = max((self.root.winfo_screenwidth() - ancho) // 2, 0)
        y = max((self.root.winfo_screenheight() - alto) // 2, 0)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _cambiar_vista(self, nueva_vista) -> None:
        if self.vista_actual is not None:
            self.vista_actual.destroy()
        self.vista_actual = nueva_vista

    def mostrar_login(self) -> None:
        self.usuario_actual = None
        self._cambiar_vista(LoginView(self.root, self.servicio, self.mostrar_principal))

    def mostrar_principal(self, usuario_autenticado) -> None:
        self.usuario_actual = usuario_autenticado
        self._cambiar_vista(
            MainView(
                self.root,
                self.servicio,
                usuario_autenticado,
                self.mostrar_login,
            )
        )

    def ejecutar(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    RestauranteApp().ejecutar()
