"""API Georef (datos.gob.ar): provincias y municipios de Argentina."""

from modelos.municipio import Municipio
from modelos.provincia import Provincia
from servicios.cliente_http import ClienteHTTP


class GeorefService(ClienteHTTP): 

    URL = "https://apis.datos.gob.ar/georef/api"

    def __init__(self):
        super().__init__(self.URL)

    def provincias(self) -> list[Provincia]:
        datos = self.get("provincias", {"campos": "id,nombre", "max": 30})
        lista = [Provincia.desde_json(p) for p in datos["provincias"]]
        return sorted(lista, key=lambda p: p.nombre)

    def municipios(self, provincia_id: str) -> list[Municipio]:
        params = {
            "provincia": provincia_id,
            "campos": "id,nombre,centroide",
            "max": 1000,
        }
        datos = self.get("municipios", params)
        lista = [Municipio.desde_json(m) for m in datos["municipios"]]
        return sorted(lista, key=lambda m: m.nombre)