# Restaurante App - Semana 16

**Asignatura:** Programación Orientada a Objetos  
**Estudiante:** Sandy Yarina Grefa Alvarado

## Propósito de la Semana 16

Esta versión de `restaurante_app` continúa el proyecto desarrollado en semanas anteriores. Conserva la arquitectura modular, la persistencia mediante archivos JSON y las funciones previas de inicio de sesión, gestión de productos y ventas.

En la Semana 16 se evoluciona la sección **Usuarios** para incorporar roles básicos, operaciones CRUD y manejo explícito de eventos en Tkinter mediante `bind()`, manteniendo `command=` en los botones principales.

## Evolución del proyecto

- **Semanas previas:** arquitectura modular, inicio de sesión, navegación gráfica y gestión de productos.
- **Semana 15:** sección Ventas con selección de usuario y producto, registro mediante botón con `command=`, callback y persistencia en `ventas.json`.
- **Semana 16:** CRUD de usuarios, roles, control administrativo básico y eventos `<<TreeviewSelect>>`, `<Return>`, `<Escape>` y `<<ComboboxSelected>>`.

## Estructura del proyecto

```text
restaurante_app/
|-- assets/
|   |-- logo.png
|   |-- productos.png
|   |-- ventas.png
|   |-- usuarios.png
|   `-- salir.png
|-- datos/
|   |-- productos.json
|   |-- usuarios.json
|   `-- ventas.json
|-- modelos/
|   |-- __init__.py
|   |-- producto.py
|   |-- usuario.py
|   `-- venta.py
|-- servicios/
|   |-- __init__.py
|   |-- archivo_servicio.py
|   `-- restaurante_servicio.py
|-- ui/
|   |-- __init__.py
|   |-- login_view.py
|   `-- main_view.py
`-- main.py
```

## Gestión de usuarios y roles

El modelo `Usuario` incorpora el atributo `rol`.

- **Administrador:** puede acceder a la gestión administrativa de usuarios.
- **Empleado:** puede utilizar Productos y Ventas, pero no administra usuarios.
- **Cliente:** no dispone de la gestión administrativa de usuarios.

Desde la sección **Usuarios**, el Administrador puede:

1. Registrar usuarios de tipo Empleado o Cliente.
2. Consultar los usuarios registrados.
3. Seleccionar un usuario desde el `Treeview` y cargar sus datos en el formulario.
4. Actualizar la información del usuario seleccionado.
5. Eliminar usuarios con confirmación previa.

La cuenta administrativa autenticada no puede eliminarse accidentalmente.

## Eventos implementados

### `<<TreeviewSelect>>`

Se asocia al `Treeview` mediante `bind()`. Al seleccionar una fila, la interfaz obtiene el identificador y consulta el objeto correspondiente mediante `RestauranteServicio`. La contraseña no se muestra en la tabla.

### `<Return>`

Funciona como atajo para registrar un usuario desde el formulario. El callback reutiliza el mismo método utilizado por el botón **Registrar**, evitando duplicar lógica.

### `<Escape>`

Limpia el formulario, cancela la selección actual del `Treeview` y devuelve la sección a su estado inicial.

### `<<ComboboxSelected>>`

Se asocia al `Combobox` de rol y actualiza la retroalimentación visual cuando cambia la selección.

## Diferencia entre `command=` y `bind()`

- `command=` se utiliza en los botones de las acciones principales.
- `bind()` se utiliza para eventos de teclado y eventos virtuales de componentes.

Los callbacks coordinan la interacción con la interfaz, mientras que las validaciones, reglas de negocio y persistencia permanecen en `RestauranteServicio`.

## Persistencia

La aplicación utiliza archivos JSON:

- `productos.json`: productos registrados.
- `usuarios.json`: usuarios, credenciales y roles.
- `ventas.json`: ventas registradas.

`ArchivoServicio` centraliza la lectura y escritura de los archivos JSON.

## Recursos visuales

La carpeta `assets/` contiene el logotipo y los íconos utilizados en la interfaz para mejorar la navegación, la claridad visual y la experiencia de usuario.

## Datos de demostración

Los archivos JSON incluyen datos de prueba académica para facilitar la verificación del funcionamiento del sistema. Estos registros son demostrativos y permiten comprobar persistencia, roles, productos y ventas sin presentarlos como historial real de uso.

## Accesos de prueba

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin` | `1234` |
| Empleado | `empleado` | `1234` |
| Cliente | `cliente` | `1234` |

## Ejecución

Desde la carpeta `restaurante_app`:

```bash
python main.py
```

La aplicación utiliza módulos de la biblioteca estándar de Python y Tkinter; no requiere instalar librerías externas.
