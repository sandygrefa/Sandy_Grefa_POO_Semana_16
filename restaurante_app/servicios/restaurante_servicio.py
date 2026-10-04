from pathlib import Path
from uuid import uuid4

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio


class RestauranteServicio:
    """Gestiona reglas de negocio, consultas y persistencia del restaurante."""

    def __init__(self, directorio_datos: Path | None = None):
        if directorio_datos is None:
            directorio_datos = Path(__file__).resolve().parent.parent / "datos"

        self._ruta_productos = directorio_datos / "productos.json"
        self._ruta_usuarios = directorio_datos / "usuarios.json"
        self._ruta_ventas = directorio_datos / "ventas.json"

        self._productos: list[Producto] = []
        self._usuarios: list[Usuario] = []
        self._ventas: list[Venta] = []

        self._productos_por_codigo: dict[str, Producto] = {}
        self._usuarios_por_usuario: dict[str, Usuario] = {}
        self._usuarios_por_identificacion: dict[str, Usuario] = {}

        self._cargar_datos()
        self._reconstruir_indices()

    def _cargar_datos(self) -> None:
        self._productos = [
            Producto.desde_diccionario(datos)
            for datos in ArchivoServicio.cargar(self._ruta_productos)
        ]
        self._usuarios = [
            Usuario.desde_diccionario(datos)
            for datos in ArchivoServicio.cargar(self._ruta_usuarios)
        ]
        self._ventas = [
            Venta.desde_diccionario(datos)
            for datos in ArchivoServicio.cargar(self._ruta_ventas)
        ]

    def _reconstruir_indices(self) -> None:
        self._productos_por_codigo = {
            producto.codigo: producto for producto in self._productos
        }
        self._usuarios_por_usuario = {
            usuario.usuario: usuario for usuario in self._usuarios
        }
        self._usuarios_por_identificacion = {
            usuario.identificacion: usuario for usuario in self._usuarios
        }

    def _guardar_productos(self) -> None:
        ArchivoServicio.guardar(
            self._ruta_productos,
            [producto.convertir_a_diccionario() for producto in self._productos],
        )

    def _guardar_usuarios(self) -> None:
        ArchivoServicio.guardar(
            self._ruta_usuarios,
            [usuario.convertir_a_diccionario() for usuario in self._usuarios],
        )

    def _guardar_ventas(self) -> None:
        ArchivoServicio.guardar(
            self._ruta_ventas,
            [venta.convertir_a_diccionario() for venta in self._ventas],
        )

    @staticmethod
    def _exigir_administrador(usuario_sesion: Usuario) -> None:
        if usuario_sesion.rol != "Administrador":
            raise PermissionError("Solo el Administrador puede gestionar usuarios.")

    # -------------------- Autenticación --------------------
    def autenticar_usuario(self, usuario: str, contrasena: str) -> Usuario | None:
        usuario = str(usuario).strip()
        contrasena = str(contrasena)
        encontrado = self._usuarios_por_usuario.get(usuario)
        if encontrado is not None and encontrado.contrasena == contrasena:
            return encontrado
        return None

    def validar_credenciales(self, usuario: str, contrasena: str) -> bool:
        return self.autenticar_usuario(usuario, contrasena) is not None

    # -------------------- Productos --------------------
    def listar_productos(self) -> list[Producto]:
        return list(self._productos)

    def buscar_producto(self, codigo: str) -> Producto | None:
        return self._productos_por_codigo.get(str(codigo).strip())

    def registrar_producto(self, codigo: str, nombre: str, precio: float, stock: int) -> Producto:
        codigo = str(codigo).strip()
        if codigo in self._productos_por_codigo:
            raise ValueError("Ya existe un producto con ese código.")
        producto = Producto(codigo, nombre, precio, stock)
        self._productos.append(producto)
        self._productos_por_codigo[producto.codigo] = producto
        self._guardar_productos()
        return producto

    def actualizar_producto(self, codigo: str, nombre: str, precio: float, stock: int) -> Producto:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError("No existe un producto con ese código.")
        producto.nombre = nombre
        producto.precio = precio
        producto.stock = stock
        self._guardar_productos()
        return producto

    def eliminar_producto(self, codigo: str) -> Producto:
        codigo = str(codigo).strip()
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError("No existe un producto con ese código.")
        self._productos.remove(producto)
        del self._productos_por_codigo[codigo]
        self._guardar_productos()
        return producto

    # -------------------- Usuarios --------------------
    def listar_usuarios(self) -> list[Usuario]:
        return list(self._usuarios)

    def buscar_usuario_por_identificacion(self, identificacion: str) -> Usuario | None:
        return self._usuarios_por_identificacion.get(str(identificacion).strip())

    def buscar_usuario_por_usuario(self, nombre_usuario: str) -> Usuario | None:
        return self._usuarios_por_usuario.get(str(nombre_usuario).strip())

    def registrar_usuario(
        self,
        identificacion: str,
        nombre: str,
        nombre_usuario: str,
        contrasena: str,
        rol: str,
        usuario_sesion: Usuario,
    ) -> Usuario:
        self._exigir_administrador(usuario_sesion)
        identificacion = str(identificacion).strip()
        nombre_usuario = str(nombre_usuario).strip()
        rol = str(rol).strip().title()

        if rol not in ("Empleado", "Cliente"):
            raise ValueError("Desde esta sección solo se registran Empleados o Clientes.")
        if identificacion in self._usuarios_por_identificacion:
            raise ValueError("Ya existe un usuario con esa identificación.")
        if nombre_usuario in self._usuarios_por_usuario:
            raise ValueError("Ya existe una cuenta con ese nombre de usuario.")

        usuario = Usuario(identificacion, nombre, nombre_usuario, contrasena, rol)
        self._usuarios.append(usuario)
        self._reconstruir_indices()
        self._guardar_usuarios()
        return usuario

    def actualizar_usuario(
        self,
        identificacion: str,
        nombre: str,
        nombre_usuario: str,
        contrasena: str,
        rol: str,
        usuario_sesion: Usuario,
    ) -> Usuario:
        self._exigir_administrador(usuario_sesion)
        usuario = self.buscar_usuario_por_identificacion(identificacion)
        if usuario is None:
            raise ValueError("No existe un usuario con esa identificación.")
        if usuario.rol == "Administrador":
            raise ValueError("La cuenta Administrador principal no se modifica desde esta sección.")

        nombre_usuario = str(nombre_usuario).strip()
        rol = str(rol).strip().title()
        otro = self._usuarios_por_usuario.get(nombre_usuario)
        if otro is not None and otro.identificacion != usuario.identificacion:
            raise ValueError("Ya existe otra cuenta con ese nombre de usuario.")
        if rol not in ("Empleado", "Cliente"):
            raise ValueError("El rol administrable debe ser Empleado o Cliente.")

        usuario.nombre = nombre
        usuario.usuario = nombre_usuario
        usuario.contrasena = contrasena
        usuario.rol = rol
        self._reconstruir_indices()
        self._guardar_usuarios()
        return usuario

    def eliminar_usuario(self, identificacion: str, usuario_sesion: Usuario) -> Usuario:
        self._exigir_administrador(usuario_sesion)
        usuario = self.buscar_usuario_por_identificacion(identificacion)
        if usuario is None:
            raise ValueError("No existe un usuario con esa identificación.")
        if usuario.identificacion == usuario_sesion.identificacion:
            raise ValueError("La cuenta administrativa autenticada no puede eliminarse.")
        if usuario.rol == "Administrador":
            raise ValueError("La cuenta Administrador principal no puede eliminarse.")

        self._usuarios.remove(usuario)
        self._reconstruir_indices()
        self._guardar_usuarios()
        return usuario

    # -------------------- Ventas --------------------
    def listar_ventas(self) -> list[Venta]:
        return list(self._ventas)

    def registrar_venta(self, usuario_identificacion: str, producto_codigo: str) -> Venta:
        usuario = self.buscar_usuario_por_identificacion(usuario_identificacion)
        producto = self.buscar_producto(producto_codigo)
        if usuario is None:
            raise ValueError("Seleccione un usuario válido para la venta.")
        if producto is None:
            raise ValueError("Seleccione un producto válido para la venta.")

        venta = Venta(
            identificador=uuid4().hex[:8].upper(),
            usuario_identificacion=usuario.identificacion,
            producto_codigo=producto.codigo,
        )
        self._ventas.append(venta)
        self._guardar_ventas()
        return venta
