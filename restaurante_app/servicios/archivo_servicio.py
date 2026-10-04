import json
from pathlib import Path
from typing import Any


class ArchivoServicio:
    """Centraliza la lectura y escritura de archivos JSON."""

    @staticmethod
    def cargar(ruta: Path) -> list[dict[str, Any]]:
        ruta.parent.mkdir(parents=True, exist_ok=True)

        if not ruta.exists():
            ArchivoServicio.guardar(ruta, [])
            return []

        try:
            contenido = ruta.read_text(encoding="utf-8").strip()
            if not contenido:
                return []

            datos = json.loads(contenido)
            if not isinstance(datos, list):
                raise ValueError(f"El archivo {ruta.name} debe contener una lista JSON.")
            return datos
        except json.JSONDecodeError as error:
            raise ValueError(f"El archivo {ruta.name} contiene JSON inválido.") from error

    @staticmethod
    def guardar(ruta: Path, datos: list[dict[str, Any]]) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(
            json.dumps(datos, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )
