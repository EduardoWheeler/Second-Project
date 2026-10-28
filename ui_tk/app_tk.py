import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from servicios.cliente_http import ErrorAPI
from servicios.georef_service import GeorefService


class AppTk(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Georef - Municipios (Tkinter)")
        self.geometry("640x480")
        self.servicio = GeorefService()
        self.provincias = []
        self.cola = queue.Queue()
        self._crear_widgets()
        self._en_segundo_plano(
            self.servicio.provincias, self._mostrar_provincias
        )
        self.after(100, self._revisar_cola)

    def _crear_widgets(self):
        barra = ttk.Frame(self, padding=8)
        barra.pack(fill="x")
        ttk.Label(barra, text="Provincia:").pack(side="left")
        self.combo = ttk.Combobox(barra, state="readonly", width=35)
        self.combo.pack(side="left", padx=6)
        self.btn = ttk.Button(barra, text="Buscar", command=self._buscar)
        self.btn.pack(side="left")

        columnas = ("nombre", "coordenadas")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")
        self.tabla.heading("nombre", text="Municipio")
        self.tabla.heading("coordenadas", text="Lat, Lon")
        self.tabla.column("coordenadas", width=160, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=8)

        self.estado = tk.StringVar(value="Cargando provincias...")
        ttk.Label(self, textvariable=self.estado, padding=6).pack(fill="x")

    def _en_segundo_plano(self, funcion, al_terminar, *args):
        def trabajo():
            try:
                self.cola.put((al_terminar, funcion(*args), None))
            except ErrorAPI as e:
                self.cola.put((al_terminar, None, e))

        threading.Thread(target=trabajo, daemon=True).start()

    def _revisar_cola(self):
        try:
            while True:
                callback, resultado, error = self.cola.get_nowait()
                if error:
                    self.estado.set("Error")
                    self.btn.state(["!disabled"])
                    messagebox.showerror("Error", str(error))
                else:
                    callback(resultado)
        except queue.Empty:
            pass
        self.after(100, self._revisar_cola)


    def _mostrar_provincias(self, provincias):
        self.provincias = provincias
        self.combo["values"] = [p.nombre for p in provincias]
        self.estado.set(f"{len(provincias)} provincias")

    def _buscar(self):
        indice = self.combo.current()
        if indice < 0:
            messagebox.showwarning("Atención", "Elegí una provincia")
            return
        self.btn.state(["disabled"])
        self.estado.set("Consultando la API...")
        prov = self.provincias[indice]
        self._en_segundo_plano(
            self.servicio.municipios, self._mostrar_municipios, prov.id
        )

    def _mostrar_municipios(self, municipios):
        self.tabla.delete(*self.tabla.get_children())
        for m in municipios:
            self.tabla.insert("", "end", values=(m.nombre, m.coordenadas))
        self.estado.set(f"{len(municipios)} municipios")
        self.btn.state(["!disabled"])
