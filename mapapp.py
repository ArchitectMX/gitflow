import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint

API_KEY_STATIC = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
API_KEY_GEOCODE = "8013b162-6b42-4997-9691-77b7074026e0"
API_KEY_ORGANIZATION = "YOUR_ORGANIZATION_SEARCH_API_KEY"


class MapViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.lon, self.lat = 28.97709, 41.005233  # Начальные координаты (Стамбул)
        self.zoom = 12  # Начальный масштаб
        self.theme = "light"  # Тема карты
        self.marker = None  # Метка (координаты)
        self.address = ""
        self.show_postal_code = False

        self.initUI()
        self.load_map()

    def initUI(self):
        layout = QVBoxLayout()

        self.map_label = QLabel(self)
        layout.addWidget(self.map_label)
        self.map_label.mousePressEvent = self.map_clicked

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Введите запрос...")
        self.search_input.returnPressed.connect(self.search_location)
        layout.addWidget(self.search_input)

        search_button = QPushButton("Искать", self)
        search_button.clicked.connect(self.search_location)
        layout.addWidget(search_button)

        reset_button = QPushButton("Сброс поискового результата", self)
        reset_button.clicked.connect(self.reset_marker)
        layout.addWidget(reset_button)

        self.address_label = QLabel("Адрес: ", self)
        layout.addWidget(self.address_label)

        self.theme_switch = QComboBox(self)
        self.theme_switch.addItems(["light", "dark"])
        self.theme_switch.currentTextChanged.connect(self.change_theme)
        layout.addWidget(self.theme_switch)

        self.postal_code_checkbox = QCheckBox("Добавлять почтовый индекс", self)
        self.postal_code_checkbox.stateChanged.connect(self.toggle_postal_code)
        layout.addWidget(self.postal_code_checkbox)

        self.setLayout(layout)
        self.setWindowTitle("Карта")
        self.setGeometry(100, 100, 600, 500)

    def load_map(self):
        url = f"https://static-maps.yandex.ru/v1?lang=ru_RU&ll={self.lon},{self.lat}&z={self.zoom}&theme={self.theme}&apikey={API_KEY_STATIC}"
        if self.marker:
            url += f"&pt={self.marker},pm2rdm"
        response = requests.get(url)
        if response.status_code == 200:
            with open("map.png", "wb") as file:
                file.write(response.content)
            self.map_label.setPixmap(QPixmap("map.png"))
        self.address_label.setText(f"Адрес: {self.address}")

    def search_location(self):
        query = self.search_input.text()
        if not query:
            return
        url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY_GEOCODE}&geocode={query}&format=json"
        response = requests.get(url).json()
        try:
            geo_object = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            coords = geo_object["Point"]["pos"].split()
            self.lon, self.lat = float(coords[0]), float(coords[1])
            self.marker = f"{self.lon},{self.lat}"
            self.address = geo_object["metaDataProperty"]["GeocoderMetaData"]["text"]
            if not self.show_postal_code:
                self.address = self.address.split(',')[0]
            self.load_map()
        except (KeyError, IndexError):
            print("Местоположение не найдено.")

    def reset_marker(self):
        self.marker = None
        self.address = ""
        self.load_map()

    def change_theme(self, theme):
        self.theme = theme
        self.load_map()

    def toggle_postal_code(self, state):
        self.show_postal_code = state == Qt.Checked
        self.load_map()

    def map_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.find_location_by_click(event.pos())
        elif event.button() == Qt.RightButton:
            self.find_organization_by_click(event.pos())

    def find_location_by_click(self, pos: QPoint):
        self.lon += (pos.x() - self.width() / 2) / 10000
        self.lat -= (pos.y() - self.height() / 2) / 10000
        self.marker = f"{self.lon},{self.lat}"
        self.search_location()

    def find_organization_by_click(self, pos: QPoint):
        self.lon += (pos.x() - self.width() / 2) / 10000
        self.lat -= (pos.y() - self.height() / 2) / 10000
        url = f"https://search-maps.yandex.ru/v1/?apikey={API_KEY_ORGANIZATION}&text=организация&lang=ru_RU&ll={self.lon},{self.lat}&spn=0.001,0.001&results=1"
        response = requests.get(url).json()
        try:
            org = response["features"][0]
            org_lon, org_lat = org["geometry"]["coordinates"]
            if ((self.lon - org_lon) ** 2 + (self.lat - org_lat) ** 2) ** 0.5 <= 0.0005:
                self.marker = f"{org_lon},{org_lat}"
                self.address = org["properties"]["CompanyMetaData"]["name"]
                self.load_map()
        except (KeyError, IndexError):
            print("Организация не найдена.")

    def keyPressEvent(self, event):
        step = 0.1 if self.zoom > 10 else 1.0
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_PageUp:
            if self.zoom < 17:
                self.zoom += 1
        elif event.key() == Qt.Key_Minus or event.key() == Qt.Key_PageDown:
            if self.zoom > 1:
                self.zoom -= 1
        elif event.key() == Qt.Key_Up:
            self.lat += step
        elif event.key() == Qt.Key_Down:
            self.lat -= step
        elif event.key() == Qt.Key_Alt:
            self.lon -= step
        elif event.key() == Qt.Key_Control:
            self.lon += step
        self.load_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(app.exec_())
