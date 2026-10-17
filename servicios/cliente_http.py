"""Clase base reutilizable para cualquier API REST que devuelva JSON."""

import requests


class ErrorAPI(Exception):
    """Error propio: la interfaz no necesita conocer 'requests'."""


class ClienteHTTP:

    def __init__(self, url_base: str, timeout: int = 10):
        self.url_base = url_base.rstrip("/")
        self.timeout = timeout
        self._sesion = requests.Session()  # reutiliza la conexión TCP
        self._sesion.headers["Accept"] = "application/json"

    def get(self, recurso: str, params: dict | None = None) -> dict:
        url = f"{self.url_base}/{recurso.lstrip('/')}"
        try:
            resp = self._sesion.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()  # 4xx / 5xx -> excepción
            return resp.json()
        except requests.Timeout as e:
            raise ErrorAPI("El servidor tardó demasiado en responder") from e
        except requests.ConnectionError as e:
            raise ErrorAPI("Sin conexión con el servidor") from e
        except requests.HTTPError as e:
            raise ErrorAPI(f"HTTP {resp.status_code}: {resp.reason}") from e
        except ValueError as e:
            raise ErrorAPI("La respuesta no es JSON válido") from e