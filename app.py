import sys
import io
import os
import geojson
import simplekml
import folium
from folium.plugins import Draw
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMessageBox, QMainWindow, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView # pip install PyQtWebEngine
from PyQt5 import QtGui

"""
Folium in PyQt5
"""

from design import Ui_MainWindow

class ApplicationWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.setWindowIcon(QtGui.QIcon('Army\\Icons\\Mechanized Infantry.png'))
        self.setWindowTitle("NATO symbol Creator")
        self.setGeometry(200,200,1440,900)


        self.directory_path()
        self.leaflet()
        self.handle_combo_unit_modifier()


        self.pushButton_Create.clicked.connect(self.btn_command)


    def btn_command(self):
        if self.description_check():
            self.create_units()
            self.default_screen

    def read_geojson(self):
        with open(f"{self.directory}\\data.geojson") as f:
            self.gj = geojson.load(f)

        self.features = self.gj['features']
    

    def create_units(self):
        self.read_geojson()
        scale_size = {'Battalion':1.5, 
            'Regiment':1.5, 
            'Brigade': 1.7, 
            'Division': 2,
            'Corps':2.4,
            'Army':2.8}

        target_list = []

        for i in range(len(self.features)):
            if self.features[i]['geometry']['type'] == 'Point':
                coordinates = self.features[i]['geometry']["coordinates"]
                target_list.append(coordinates)

        kml = simplekml.Kml()

        for i in range(len(target_list)):
            try:
                affiliation = self.comboBox_affiliation.currentText()
                unit = self.comboBox_unit_modifier.currentText()
                size = self.comboBox_battle_dimension.currentText().split(' (')[0]
                state = self.lineEdit_description.text()

                this = kml.newpoint(name='', coords = [target_list[i]])
                this.style.iconstyle.icon.href = f"{self.directory}\\Army\\{affiliation}\\{unit}\\{unit}_{size}.png"
                this.iconstyle.scale = scale_size[size]
                this.description = f"{state} {unit} {size} ({i+1}/{len(target_list)})"
                print(affiliation, unit, size)
            except:
                pass
        
        filename = QFileDialog.getSaveFileName(self, "Save File", "units.kml", )
        if filename[0]:
            kml.save(filename[0])


    def description_check(self):
        if not self.lineEdit_description.text():
            res = QMessageBox.information(self,"Warning", "Are you sure you don't want to provide description?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if res == QMessageBox.StandardButton.Yes:
                return True
            return False
        return True

    def leaflet(self):
        m = folium.Map(
            location = [53.5511, 9.9937],
            zoom_start = 5)
        Draw(
            export=True,
            filename=f'{self.directory}\\data.geojson',
            position='topleft',
            draw_options={'polyline': {'allowIntersection': False}},
            edit_options={'poly': {'allowIntersection': False}}
        ).add_to(m)
        data = io.BytesIO()
        m.save(data, close_file = False)

        webView = QWebEngineView()
        webView.page().profile().downloadRequested.connect(
            self.handle_downloadRequested
        )
        webView.setHtml(data.getvalue().decode())

        self.verticalLayout_frame = QVBoxLayout(self.frame)
        self.verticalLayout_frame.addWidget(webView)

        
    def handle_downloadRequested(self, item):
        path = f'{self.directory}\\data.geojson'
        if path:
            item.setPath(path)
            item.accept()
        
    def handle_combo_unit_modifier(self):
        self.default_screen()
        disable_list = [0, 6, 12, 18]
        for index in disable_list:
            self.comboBox_unit_modifier.model().item(index).setEnabled(False)

    def default_screen(self):
        self.comboBox_affiliation.setCurrentIndex(0)
        self.comboBox_unit_modifier.setCurrentIndex(1)
        self.comboBox_battle_dimension.setCurrentIndex(0)
        self.lineEdit_description.clear()

    def directory_path(self):
        self.directory = os.getcwd()



app = QApplication(sys.argv)
w = ApplicationWindow()
w.show()

sys.exit(app.exec_())