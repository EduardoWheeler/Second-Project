from dataclasses import dataclass


@dataclass(frozen=True)
class Provincia:
    id: str
    nombre: str

    @classmethod
    def desde_json(cls, datos: dict) -> "Provincia":
        return cls(id=datos["id"], nombre=datos["nombre"])