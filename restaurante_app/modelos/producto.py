class Producto:
    """Representa un producto disponible en el restaurante."""

    def __init__(self, codigo: str, nombre: str, precio: float, stock: int):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ValueError("El código del producto no puede estar vacío.")
        self._codigo = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        valor = str(valor).strip()
        if not valor:
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = valor

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        try:
            valor = float(valor)
        except (TypeError, ValueError) as error:
            raise ValueError("El precio debe ser numérico.") from error
        if valor < 0:
            raise ValueError("El precio no puede ser negativo.")
        self._precio = valor

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        try:
            valor = int(valor)
        except (TypeError, ValueError) as error:
            raise ValueError("El stock debe ser un número entero.") from error
        if valor < 0:
            raise ValueError("El stock no puede ser negativo.")
        self._stock = valor

    def convertir_a_diccionario(self) -> dict:
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }

    @classmethod
    def desde_diccionario(cls, datos: dict) -> "Producto":
        return cls(
            codigo=datos["codigo"],
            nombre=datos["nombre"],
            precio=datos["precio"],
            stock=datos["stock"],
        )

    def __str__(self) -> str:
        return (
            f"Código: {self.codigo} | Nombre: {self.nombre} | "
            f"Precio: ${self.precio:.2f} | Stock: {self.stock}"
        )
