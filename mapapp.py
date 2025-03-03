import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

API_KEY_STATIC = "API_KEY_STATIC"
API_KEY_GEOCODE = "API_KEY_GEOCODE"


class MapViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.lon, self.lat = 28.97709, 41.005233
        self.zoom = 12
        self.theme = "light"
        self.marker = None

        self.initUI()
        self.load_map()

    def initUI(self):
        layout = QVBoxLayout()

        self.map_label = QLabel(self)
        layout.addWidget(self.map_label)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Введите запрос...")
        self.search_input.returnPressed.connect(self.search_location)
        layout.addWidget(self.search_input)

        search_button = QPushButton("Искать", self)
        search_button.clicked.connect(self.search_location)
        layout.addWidget(search_button)

        self.theme_switch = QComboBox(self)
        self.theme_switch.addItems(["light", "dark"])
        self.theme_switch.currentTextChanged.connect(self.change_theme)
        layout.addWidget(self.theme_switch)

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

    def search_location(self):
        query = self.search_input.text()
        if not query:
            return
        url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY_GEOCODE}&geocode={query}&format=json"
        response = requests.get(url).json()
        try:
            coords = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
                "pos"].split()
            self.lon, self.lat = float(coords[0]), float(coords[1])
            self.marker = f"{self.lon},{self.lat}"
            self.load_map()
        except (KeyError, IndexError):
            print("Местоположение не найдено.")

    def change_theme(self, theme):
        self.theme = theme
        self.load_map()

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
        elif event.key() == Qt.Key_Left:
            self.lon -= step
        elif event.key() == Qt.Key_Right:
            self.lon += step
        self.load_map()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MapViewer()
    viewer.show()
    sys.exit(app.exec_())
