from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio


class MainView(ttk.Frame):
    """Vista principal de Productos, Ventas y gestión administrativa de Usuarios."""

    def __init__(
        self,
        master: tk.Misc,
        servicio: RestauranteServicio,
        usuario_actual: Usuario,
        al_cerrar_sesion,
    ):
        super().__init__(master, style="App.TFrame")
        self.servicio = servicio
        self.usuario_actual = usuario_actual
        self.al_cerrar_sesion = al_cerrar_sesion

        self.estado_var = tk.StringVar(value="Aplicación lista.")
        self._contenido = None
        self._imagenes = {}
        self._tabla_productos = None
        self._tabla_ventas = None
        self._tabla_usuarios = None
        self._usuario_seleccionado_id = None
        self._widgets_evento_usuario = []

        # Productos
        self.codigo_var = tk.StringVar()
        self.nombre_producto_var = tk.StringVar()
        self.precio_var = tk.StringVar()
        self.stock_var = tk.StringVar()

        # Ventas
        self.venta_usuario_var = tk.StringVar()
        self.venta_producto_var = tk.StringVar()
        self._venta_usuario_map = {}
        self._venta_producto_map = {}

        # Usuarios
        self.usuario_id_var = tk.StringVar()
        self.usuario_nombre_var = tk.StringVar()
        self.usuario_cuenta_var = tk.StringVar()
        self.usuario_clave_var = tk.StringVar()
        self.usuario_rol_var = tk.StringVar(value="Cliente")
        self.usuario_evento_var = tk.StringVar(value="Seleccione o registre un usuario.")

        self._construir_interfaz()
        self.mostrar_productos()

    # -------------------- Estructura general --------------------
    def _cargar_imagen(self, nombre: str):
        ruta = Path(__file__).resolve().parent.parent / "assets" / nombre
        if not ruta.exists():
            return None
        try:
            imagen = tk.PhotoImage(file=str(ruta))
            self._imagenes[nombre] = imagen
            return imagen
        except tk.TclError:
            return None

    def _construir_interfaz(self) -> None:
        self.pack(fill="both", expand=True)

        encabezado = ttk.Frame(self, padding=(20, 12), style="Header.TFrame")
        encabezado.pack(fill="x")

        logo = self._cargar_imagen("logo.png")
        if logo is not None:
            ttk.Label(encabezado, image=logo, background="#17324D").pack(side="left", padx=(0, 14))

        ttk.Label(encabezado, text="Restaurante App", style="HeaderTitle.TLabel").pack(side="left")
        ttk.Label(
            encabezado,
            text=f"  |  {self.usuario_actual.nombre} · {self.usuario_actual.rol}",
            style="HeaderInfo.TLabel",
        ).pack(side="left", padx=(12, 0))

        cuerpo = ttk.Frame(self, style="App.TFrame")
        cuerpo.pack(fill="both", expand=True)

        navegacion = ttk.Frame(cuerpo, padding=14, style="Nav.TFrame")
        navegacion.pack(side="left", fill="y")

        ttk.Label(navegacion, text="NAVEGACIÓN", font=("Segoe UI", 9, "bold"), background="#E8EEF5").pack(
            anchor="w", pady=(0, 14)
        )

        self._boton_nav(navegacion, "Productos", "productos.png", self.mostrar_productos)
        self._boton_nav(navegacion, "Ventas", "ventas.png", self.mostrar_ventas)

        if self.usuario_actual.rol == "Administrador":
            self._boton_nav(navegacion, "Usuarios", "usuarios.png", self.mostrar_usuarios)

        ttk.Separator(navegacion).pack(fill="x", pady=16)
        self._boton_nav(navegacion, "Cerrar sesión", "salir.png", self.al_cerrar_sesion)

        self._contenido = ttk.Frame(cuerpo, padding=20, style="App.TFrame")
        self._contenido.pack(side="left", fill="both", expand=True)

        pie = ttk.Frame(self, padding=(16, 8), style="App.TFrame")
        pie.pack(fill="x")
        ttk.Label(pie, textvariable=self.estado_var, style="Status.TLabel").pack(anchor="w")

    def _boton_nav(self, padre, texto, icono, comando):
        imagen = self._cargar_imagen(icono)
        kwargs = {"text": texto, "command": comando, "style": "Nav.TButton", "width": 20}
        if imagen is not None:
            kwargs.update({"image": imagen, "compound": "left"})
        ttk.Button(padre, **kwargs).pack(fill="x", pady=4)

    def _limpiar_contenido(self) -> None:
        self._desvincular_eventos_usuario()
        for widget in self._contenido.winfo_children():
            widget.destroy()

    # -------------------- Productos --------------------
    def mostrar_productos(self) -> None:
        self._limpiar_contenido()
        ttk.Label(self._contenido, text="Gestión de productos", style="Section.TLabel").pack(
            anchor="w", pady=(0, 14)
        )

        formulario = ttk.LabelFrame(self._contenido, text="Datos del producto", padding=16)
        formulario.pack(fill="x", pady=(0, 14))

        campos = [
            ("Código:", self.codigo_var, 0, 0),
            ("Nombre:", self.nombre_producto_var, 0, 2),
            ("Precio:", self.precio_var, 1, 0),
            ("Stock:", self.stock_var, 1, 2),
        ]
        for etiqueta, variable, fila, columna in campos:
            ttk.Label(formulario, text=etiqueta).grid(row=fila, column=columna, sticky="w", padx=(0, 8), pady=6)
            ttk.Entry(formulario, textvariable=variable).grid(
                row=fila, column=columna + 1, sticky="ew", padx=(0, 18) if columna == 0 else 0, pady=6
            )
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        acciones = ttk.Frame(self._contenido, style="App.TFrame")
        acciones.pack(fill="x", pady=(0, 14))
        ttk.Button(acciones, text="Registrar", command=self._registrar_producto, style="Primary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(acciones, text="Cargar / Consultar", command=self._cargar_producto).pack(side="left", padx=8)
        ttk.Button(acciones, text="Actualizar", command=self._actualizar_producto).pack(side="left", padx=8)
        ttk.Button(acciones, text="Eliminar", command=self._eliminar_producto).pack(side="left", padx=8)
        ttk.Button(acciones, text="Limpiar", command=self._limpiar_formulario_producto).pack(side="left", padx=8)

        tabla_frame = ttk.LabelFrame(self._contenido, text="Productos registrados", padding=10)
        tabla_frame.pack(fill="both", expand=True)
        self._tabla_productos = ttk.Treeview(
            tabla_frame,
            columns=("codigo", "nombre", "precio", "stock"),
            show="headings",
            height=14,
        )
        for columna, texto, ancho in [
            ("codigo", "Código", 130),
            ("nombre", "Nombre", 280),
            ("precio", "Precio", 130),
            ("stock", "Stock", 100),
        ]:
            self._tabla_productos.heading(columna, text=texto)
            self._tabla_productos.column(columna, width=ancho, anchor="center" if columna != "nombre" else "w")
        scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=self._tabla_productos.yview)
        self._tabla_productos.configure(yscrollcommand=scroll.set)
        self._tabla_productos.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._actualizar_tabla_productos()
        self.estado_var.set("Sección Productos disponible.")

    def _obtener_datos_producto(self):
        codigo = self.codigo_var.get().strip()
        nombre = self.nombre_producto_var.get().strip()
        if not codigo or not nombre:
            raise ValueError("Código y nombre son obligatorios.")
        try:
            precio = float(self.precio_var.get())
        except ValueError as error:
            raise ValueError("El precio debe ser numérico.") from error
        try:
            stock = int(self.stock_var.get())
        except ValueError as error:
            raise ValueError("El stock debe ser un número entero.") from error
        return codigo, nombre, precio, stock

    def _registrar_producto(self) -> None:
        try:
            producto = self.servicio.registrar_producto(*self._obtener_datos_producto())
            self._actualizar_tabla_productos()
            self._limpiar_formulario_producto()
            self.estado_var.set(f"Producto {producto.codigo} registrado correctamente.")
        except ValueError as error:
            messagebox.showerror("Registro de producto", str(error))

    def _cargar_producto(self) -> None:
        codigo = self.codigo_var.get().strip()
        producto = self.servicio.buscar_producto(codigo)
        if producto is None:
            messagebox.showinfo("Consulta de producto", "No existe un producto con ese código.")
            return
        self.codigo_var.set(producto.codigo)
        self.nombre_producto_var.set(producto.nombre)
        self.precio_var.set(f"{producto.precio:.2f}")
        self.stock_var.set(str(producto.stock))
        self.estado_var.set(f"Producto {producto.codigo} cargado.")

    def _actualizar_producto(self) -> None:
        try:
            producto = self.servicio.actualizar_producto(*self._obtener_datos_producto())
            self._actualizar_tabla_productos()
            self.estado_var.set(f"Producto {producto.codigo} actualizado correctamente.")
        except ValueError as error:
            messagebox.showerror("Actualización de producto", str(error))

    def _eliminar_producto(self) -> None:
        codigo = self.codigo_var.get().strip()
        if not codigo:
            messagebox.showwarning("Eliminación de producto", "Ingrese el código del producto.")
            return
        if not messagebox.askyesno("Eliminar producto", f"¿Desea eliminar el producto {codigo}?"):
            return
        try:
            producto = self.servicio.eliminar_producto(codigo)
            self._actualizar_tabla_productos()
            self._limpiar_formulario_producto()
            self.estado_var.set(f"Producto {producto.codigo} eliminado.")
        except ValueError as error:
            messagebox.showerror("Eliminación de producto", str(error))

    def _actualizar_tabla_productos(self) -> None:
        if self._tabla_productos is None:
            return
        for item in self._tabla_productos.get_children():
            self._tabla_productos.delete(item)
        for producto in self.servicio.listar_productos():
            self._tabla_productos.insert("", "end", values=(producto.codigo, producto.nombre, f"${producto.precio:.2f}", producto.stock))

    def _limpiar_formulario_producto(self) -> None:
        self.codigo_var.set("")
        self.nombre_producto_var.set("")
        self.precio_var.set("")
        self.stock_var.set("")

    # -------------------- Ventas --------------------
    def mostrar_ventas(self) -> None:
        self._limpiar_contenido()
        ttk.Label(self._contenido, text="Registro de ventas", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(
            self._contenido,
            text="Seleccione un usuario y un producto para registrar una venta.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 14))

        formulario = ttk.LabelFrame(self._contenido, text="Nueva venta", padding=16)
        formulario.pack(fill="x", pady=(0, 14))

        usuarios = self.servicio.listar_usuarios()
        productos = self.servicio.listar_productos()
        self._venta_usuario_map = {f"{u.identificacion} - {u.nombre}": u.identificacion for u in usuarios}
        self._venta_producto_map = {f"{p.codigo} - {p.nombre}": p.codigo for p in productos}

        ttk.Label(formulario, text="Usuario:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        combo_usuario = ttk.Combobox(formulario, textvariable=self.venta_usuario_var, values=list(self._venta_usuario_map), state="readonly")
        combo_usuario.grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=6)

        ttk.Label(formulario, text="Producto:").grid(row=0, column=2, sticky="w", padx=(0, 8), pady=6)
        combo_producto = ttk.Combobox(formulario, textvariable=self.venta_producto_var, values=list(self._venta_producto_map), state="readonly")
        combo_producto.grid(row=0, column=3, sticky="ew", pady=6)
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        ttk.Button(
            self._contenido,
            text="Registrar venta",
            command=self._registrar_venta,
            style="Primary.TButton",
        ).pack(anchor="w", pady=(0, 14))

        tabla_frame = ttk.LabelFrame(self._contenido, text="Ventas registradas", padding=10)
        tabla_frame.pack(fill="both", expand=True)
        self._tabla_ventas = ttk.Treeview(
            tabla_frame,
            columns=("id", "usuario", "producto", "fecha"),
            show="headings",
            height=14,
        )
        for col, texto, ancho in [
            ("id", "Venta", 110),
            ("usuario", "Usuario", 220),
            ("producto", "Producto", 220),
            ("fecha", "Fecha", 180),
        ]:
            self._tabla_ventas.heading(col, text=texto)
            self._tabla_ventas.column(col, width=ancho, anchor="center" if col != "usuario" and col != "producto" else "w")
        self._tabla_ventas.pack(fill="both", expand=True)
        self._actualizar_tabla_ventas()
        self.estado_var.set("Sección Ventas disponible.")

    def _registrar_venta(self) -> None:
        usuario_id = self._venta_usuario_map.get(self.venta_usuario_var.get())
        producto_codigo = self._venta_producto_map.get(self.venta_producto_var.get())
        if not usuario_id or not producto_codigo:
            messagebox.showwarning("Registro de venta", "Seleccione un usuario y un producto.")
            return
        try:
            venta = self.servicio.registrar_venta(usuario_id, producto_codigo)
            self._actualizar_tabla_ventas()
            self.venta_usuario_var.set("")
            self.venta_producto_var.set("")
            self.estado_var.set(f"Venta {venta.identificador} registrada correctamente.")
        except ValueError as error:
            messagebox.showerror("Registro de venta", str(error))

    def _actualizar_tabla_ventas(self) -> None:
        if self._tabla_ventas is None:
            return
        for item in self._tabla_ventas.get_children():
            self._tabla_ventas.delete(item)
        for venta in self.servicio.listar_ventas():
            usuario = self.servicio.buscar_usuario_por_identificacion(venta.usuario_identificacion)
            producto = self.servicio.buscar_producto(venta.producto_codigo)
            self._tabla_ventas.insert(
                "",
                "end",
                values=(
                    venta.identificador,
                    usuario.nombre if usuario else venta.usuario_identificacion,
                    producto.nombre if producto else venta.producto_codigo,
                    venta.fecha.replace("T", " "),
                ),
            )

    # -------------------- Usuarios y eventos Semana 16 --------------------
    def mostrar_usuarios(self) -> None:
        if self.usuario_actual.rol != "Administrador":
            messagebox.showwarning("Acceso restringido", "Solo el Administrador puede gestionar usuarios.")
            return

        self._limpiar_contenido()
        self._usuario_seleccionado_id = None
        ttk.Label(self._contenido, text="Gestión de usuarios", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Label(
            self._contenido,
            text="Administre empleados y clientes del restaurante desde esta sección.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 14))

        formulario = ttk.LabelFrame(self._contenido, text="Datos del usuario", padding=14)
        formulario.pack(fill="x", pady=(0, 10))

        ttk.Label(formulario, text="Identificación:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        entrada_id = ttk.Entry(formulario, textvariable=self.usuario_id_var)
        entrada_id.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(formulario, text="Nombre:").grid(row=0, column=2, sticky="w", padx=(0, 8), pady=5)
        entrada_nombre = ttk.Entry(formulario, textvariable=self.usuario_nombre_var)
        entrada_nombre.grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(formulario, text="Usuario:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=5)
        entrada_usuario = ttk.Entry(formulario, textvariable=self.usuario_cuenta_var)
        entrada_usuario.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(formulario, text="Contraseña:").grid(row=1, column=2, sticky="w", padx=(0, 8), pady=5)
        entrada_clave = ttk.Entry(formulario, textvariable=self.usuario_clave_var, show="*")
        entrada_clave.grid(row=1, column=3, sticky="ew", pady=5)

        ttk.Label(formulario, text="Rol:").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=5)
        combo_rol = ttk.Combobox(
            formulario,
            textvariable=self.usuario_rol_var,
            values=("Empleado", "Cliente"),
            state="readonly",
        )
        combo_rol.grid(row=2, column=1, sticky="ew", padx=(0, 16), pady=5)
        ttk.Label(formulario, textvariable=self.usuario_evento_var).grid(
            row=2, column=2, columnspan=2, sticky="w", pady=5
        )

        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        acciones = ttk.Frame(self._contenido, style="App.TFrame")
        acciones.pack(fill="x", pady=(0, 10))
        ttk.Button(acciones, text="Registrar", command=self._registrar_usuario, style="Primary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(acciones, text="Actualizar", command=self._actualizar_usuario).pack(side="left", padx=8)
        ttk.Button(acciones, text="Eliminar", command=self._eliminar_usuario).pack(side="left", padx=8)
        ttk.Button(acciones, text="Limpiar", command=self._limpiar_formulario_usuario).pack(side="left", padx=8)

        tabla_frame = ttk.LabelFrame(self._contenido, text="Usuarios registrados", padding=10)
        tabla_frame.pack(fill="both", expand=True)
        self._tabla_usuarios = ttk.Treeview(
            tabla_frame,
            columns=("identificacion", "nombre", "usuario", "rol"),
            show="headings",
            height=12,
            selectmode="browse",
        )
        for col, texto, ancho in [
            ("identificacion", "Identificación", 150),
            ("nombre", "Nombre", 240),
            ("usuario", "Usuario", 170),
            ("rol", "Rol", 140),
        ]:
            self._tabla_usuarios.heading(col, text=texto)
            self._tabla_usuarios.column(col, width=ancho, anchor="center" if col != "nombre" else "w")
        scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=self._tabla_usuarios.yview)
        self._tabla_usuarios.configure(yscrollcommand=scroll.set)
        self._tabla_usuarios.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Eventos requeridos por la Semana 16.
        self._tabla_usuarios.bind("<<TreeviewSelect>>", self._al_seleccionar_usuario)
        combo_rol.bind("<<ComboboxSelected>>", self._al_cambiar_rol)
        for widget in (entrada_id, entrada_nombre, entrada_usuario, entrada_clave, combo_rol):
            widget.bind("<Return>", self._al_presionar_enter)
            widget.bind("<Escape>", self._al_presionar_escape)
            self._widgets_evento_usuario.append(widget)
        self._tabla_usuarios.bind("<Escape>", self._al_presionar_escape)
        self._widgets_evento_usuario.append(self._tabla_usuarios)

        self._actualizar_tabla_usuarios()
        entrada_id.focus_set()
        self.estado_var.set("Sección Usuarios disponible para Administrador.")

    def _desvincular_eventos_usuario(self) -> None:
        for widget in self._widgets_evento_usuario:
            try:
                widget.unbind("<Return>")
                widget.unbind("<Escape>")
                widget.unbind("<<ComboboxSelected>>")
                widget.unbind("<<TreeviewSelect>>")
            except tk.TclError:
                pass
        self._widgets_evento_usuario.clear()

    def _obtener_datos_usuario(self):
        identificacion = self.usuario_id_var.get().strip()
        nombre = self.usuario_nombre_var.get().strip()
        cuenta = self.usuario_cuenta_var.get().strip()
        clave = self.usuario_clave_var.get()
        rol = self.usuario_rol_var.get().strip()
        if not identificacion or not nombre or not cuenta or not clave or not rol:
            raise ValueError("Complete identificación, nombre, usuario, contraseña y rol.")
        return identificacion, nombre, cuenta, clave, rol

    def _registrar_usuario(self) -> None:
        try:
            usuario = self.servicio.registrar_usuario(
                *self._obtener_datos_usuario(),
                usuario_sesion=self.usuario_actual,
            )
            self._actualizar_tabla_usuarios()
            self._limpiar_formulario_usuario()
            self.estado_var.set(f"Usuario {usuario.usuario} registrado correctamente.")
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Registro de usuario", str(error))

    def _actualizar_usuario(self) -> None:
        if not self._usuario_seleccionado_id:
            messagebox.showwarning("Actualización de usuario", "Seleccione un usuario en la tabla.")
            return
        try:
            identificacion, nombre, cuenta, clave, rol = self._obtener_datos_usuario()
            if identificacion != self._usuario_seleccionado_id:
                raise ValueError("La identificación del usuario seleccionado no se puede cambiar.")
            usuario = self.servicio.actualizar_usuario(
                identificacion,
                nombre,
                cuenta,
                clave,
                rol,
                usuario_sesion=self.usuario_actual,
            )
            self._actualizar_tabla_usuarios()
            self._limpiar_formulario_usuario()
            self.estado_var.set(f"Usuario {usuario.usuario} actualizado correctamente.")
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Actualización de usuario", str(error))

    def _eliminar_usuario(self) -> None:
        if not self._usuario_seleccionado_id:
            messagebox.showwarning("Eliminación de usuario", "Seleccione un usuario en la tabla.")
            return
        usuario = self.servicio.buscar_usuario_por_identificacion(self._usuario_seleccionado_id)
        if usuario is None:
            return
        if not messagebox.askyesno("Eliminar usuario", f"¿Desea eliminar a {usuario.nombre}?"):
            return
        try:
            eliminado = self.servicio.eliminar_usuario(
                self._usuario_seleccionado_id,
                usuario_sesion=self.usuario_actual,
            )
            self._actualizar_tabla_usuarios()
            self._limpiar_formulario_usuario()
            self.estado_var.set(f"Usuario {eliminado.usuario} eliminado correctamente.")
        except (ValueError, PermissionError) as error:
            messagebox.showerror("Eliminación de usuario", str(error))

    def _al_seleccionar_usuario(self, _event) -> None:
        seleccion = self._tabla_usuarios.selection() if self._tabla_usuarios else ()
        if not seleccion:
            return
        valores = self._tabla_usuarios.item(seleccion[0], "values")
        if not valores:
            return
        identificacion = str(valores[0])
        usuario = self.servicio.buscar_usuario_por_identificacion(identificacion)
        if usuario is None:
            return

        self._usuario_seleccionado_id = usuario.identificacion
        self.usuario_id_var.set(usuario.identificacion)
        self.usuario_nombre_var.set(usuario.nombre)
        self.usuario_cuenta_var.set(usuario.usuario)
        self.usuario_clave_var.set(usuario.contrasena)
        self.usuario_rol_var.set(usuario.rol)
        self.usuario_evento_var.set(f"<<TreeviewSelect>> → {usuario.nombre}")
        self.estado_var.set("Usuario seleccionado y cargado mediante bind().")

    def _al_presionar_enter(self, _event) -> str:
        # Reutiliza el mismo método del botón Registrar; no duplica la operación.
        self._registrar_usuario()
        return "break"

    def _al_presionar_escape(self, _event) -> str:
        self._limpiar_formulario_usuario()
        self.usuario_evento_var.set("<Escape> → formulario limpio")
        self.estado_var.set("Formulario y selección limpiados mediante <Escape>.")
        return "break"

    def _al_cambiar_rol(self, _event) -> None:
        rol = self.usuario_rol_var.get()
        self.usuario_evento_var.set(f"<<ComboboxSelected>> → {rol}")
        self.estado_var.set(f"Rol seleccionado: {rol}.")

    def _actualizar_tabla_usuarios(self) -> None:
        if self._tabla_usuarios is None:
            return
        for item in self._tabla_usuarios.get_children():
            self._tabla_usuarios.delete(item)
        for usuario in self.servicio.listar_usuarios():
            self._tabla_usuarios.insert(
                "",
                "end",
                iid=usuario.identificacion,
                values=(usuario.identificacion, usuario.nombre, usuario.usuario, usuario.rol),
            )

    def _limpiar_formulario_usuario(self) -> None:
        self.usuario_id_var.set("")
        self.usuario_nombre_var.set("")
        self.usuario_cuenta_var.set("")
        self.usuario_clave_var.set("")
        self.usuario_rol_var.set("Cliente")
        self._usuario_seleccionado_id = None
        if self._tabla_usuarios is not None:
            for item in self._tabla_usuarios.selection():
                self._tabla_usuarios.selection_remove(item)
        self.usuario_evento_var.set("Formulario listo para un nuevo usuario.")
