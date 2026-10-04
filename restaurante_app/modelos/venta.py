from datetime import datetime


class Venta:
    """Representa una venta simple asociada a un usuario y un producto."""

    def __init__(
        self,
        identificador: str,
        usuario_identificacion: str,
        producto_codigo: str,
        fecha: str | None = None,
    ):
        self.identificador = identificador
        self.usuario_identificacion = usuario_identificacion
        self.producto_codigo = producto_codigo
        self.fecha = fecha or datetime.now().isoformat(timespec="seconds")

    @property
    def identificador(self) -> str:
        return self._identificador

    @identificador.setter
    def identificador(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ValueError("El identificador de la venta no puede estar vacío.")
        self._identificador = valor

    @property
    def usuario_identificacion(self) -> str:
        return self._usuario_identificacion

    @usuario_identificacion.setter
    def usuario_identificacion(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ValueError("La venta debe asociarse a un usuario.")
        self._usuario_identificacion = valor

    @property
    def producto_codigo(self) -> str:
        return self._producto_codigo

    @producto_codigo.setter
    def producto_codigo(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ValueError("La venta debe asociarse a un producto.")
        self._producto_codigo = valor

    def convertir_a_diccionario(self) -> dict:
        return {
            "identificador": self.identificador,
            "usuario_identificacion": self.usuario_identificacion,
            "producto_codigo": self.producto_codigo,
            "fecha": self.fecha,
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Venta":
        return cls(
            identificador=datos["identificador"],
            usuario_identificacion=datos["usuario_identificacion"],
            producto_codigo=datos["producto_codigo"],
            fecha=datos["fecha"],
        )
