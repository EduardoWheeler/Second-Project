from dataclasses import dataclass


@dataclass(frozen=True)
class Municipio:
    id: str
    nombre: str
    lat: float
    lon: float

    @classmethod
    def desde_json(cls, datos: dict) -> "Municipio":
        centro = datos.get("centroide", {})
        return cls(
            id=datos["id"],
            nombre=datos["nombre"],
            lat=centro.get("lat", 0.0),
            lon=centro.get("lon", 0.0),
        )

    @property
    def coordenadas(self) -> str:
        return f"{self.lat:.4f}, {self.lon:.4f}"