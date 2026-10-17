import sys
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from servicios.cliente_http import ErrorAPI
from servicios.georef_service import GeorefService


class Worker(QObject):
    """Ejecuta una función fuera del hilo de la interfaz."""

    terminado = pyqtSignal(object)
    fallo = pyqtSignal(str)

    def __init__(self, funcion, *args):
        super().__init__()
        self.funcion, self.args = funcion, args

    def run(self):
        try:
            self.terminado.emit(self.funcion(*self.args))
        except ErrorAPI as e:
            self.fallo.emit(str(e))


class VentanaPrincipal(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Georef - Municipios (PyQt6)")
        self.resize(640, 480)
        self.servicio = GeorefService()
        self.provincias = []
        self._hilos = []  # evita que el GC los destruya
        self._crear_widgets()
        self._en_segundo_plano(
            self.servicio.provincias, self._mostrar_provincias
        )

    def _crear_widgets(self):
        self.combo = QComboBox()
        self.btn = QPushButton("Buscar")
        self.btn.clicked.connect(self._buscar)  # señal -> slot

        barra = QHBoxLayout()
        barra.addWidget(QLabel("Provincia:"))
        barra.addWidget(self.combo, stretch=1)
        barra.addWidget(self.btn)

        self.tabla = QTableWidget(0, 2)
        self.tabla.setHorizontalHeaderLabels(["Municipio", "Lat, Lon"])
        encabezado = self.tabla.horizontalHeader()
        encabezado.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        encabezado.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout = QVBoxLayout()
        layout.addLayout(barra)
        layout.addWidget(self.tabla)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Cargando provincias...")

    def _en_segundo_plano(self, funcion, al_terminar, *args):
        hilo, worker = QThread(), Worker(funcion, *args)
        worker.moveToThread(hilo)
        hilo.started.connect(worker.run)
        worker.terminado.connect(al_terminar)
        worker.fallo.connect(self._mostrar_error)
        worker.terminado.connect(hilo.quit)
        worker.fallo.connect(hilo.quit)
        hilo.finished.connect(lambda: self._hilos.remove((hilo, worker)))
        self._hilos.append((hilo, worker))
        hilo.start()

    def _mostrar_provincias(self, provincias):
        self.provincias = provincias
        self.combo.addItems([p.nombre for p in provincias])
        self.statusBar().showMessage(f"{len(provincias)} provincias")

    def _buscar(self):
        indice = self.combo.currentIndex()
        if indice < 0:
            return
        self.btn.setEnabled(False)
        self.statusBar().showMessage("Consultando la API...")
        self._en_segundo_plano(
            self.servicio.municipios,
            self._mostrar_municipios,
            self.provincias[indice].id,
        )

    def _mostrar_municipios(self, municipios):
        self.tabla.setRowCount(len(municipios))
        for fila, m in enumerate(municipios):
            self.tabla.setItem(fila, 0, QTableWidgetItem(m.nombre))
            self.tabla.setItem(fila, 1, QTableWidgetItem(m.coordenadas))
        self.statusBar().showMessage(f"{len(municipios)} municipios")
        self.btn.setEnabled(True)

    def _mostrar_error(self, mensaje):
        self.btn.setEnabled(True)
        self.statusBar().showMessage("Error")
        QMessageBox.critical(self, "Error", mensaje)
