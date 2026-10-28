from servicios.cliente_http import ErrorAPI
from servicios.georef_service import GeorefService

servicio = GeorefService()
try:
    provincias = servicio.provincias()
    print(len(provincias), "provincias")  
    santa_fe = next(p for p in provincias if p.nombre == "Santa Fe")
    for m in servicio.municipios(santa_fe.id)[:5]:
        print(m.nombre, m.coordenadas)
except ErrorAPI as e:
    print("No se pudo consultar:", e)