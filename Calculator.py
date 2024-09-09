from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QComboBox, QFormLayout, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QThread
import qtmodern.styles
import qtmodern.windows
import webbrowser
import os
import requests
import sys
import json
from flask import Flask, jsonify
from threading import Thread

API_KEY = '8482bf59cdfccb689631bdef'
API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'
CURRENT_VERSION = "v1.0.0"  # Update this as needed

def check_for_updates():
    try:
        response = requests.get("http://127.0.0.1:5000/check-update")
        response.raise_for_status()
        
        update_info = response.json()
        print("Update check response data:", update_info)

        if 'latest_version' in update_info and 'download_url' in update_info:
            latest_version = update_info['latest_version']
            download_url = update_info['download_url']

            if latest_version != CURRENT_VERSION:
                print(f"New version available: {latest_version}")
                print(f"Download here: {download_url}")
                show_update_popup(download_url)
            else:
                print("No new updates found.")
        else:
            print("Expected keys are missing in the update information.")

    except requests.RequestException as e:
        print(f"Failed to check for updates: {e}")

def show_update_popup(download_url):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setWindowTitle("Update Available")
    msg.setText("A new version of the application is available.")
    msg.setInformativeText("Click OK to download the latest version.")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.buttonClicked.connect(lambda: webbrowser.open(download_url))
    msg.exec()

class CurrencyConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Currency Converter')
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #2e2e2e;")
        
        self.create_widgets()
        layout = QFormLayout(self)
        layout.addRow(QLabel('Amount:'), self.amount_input)
        layout.addRow(QLabel('From Currency:'), self.from_currency_combo)
        layout.addRow(QLabel('To Currency:'), self.to_currency_combo)
        layout.addRow(QLabel('Converted Amount:'), self.result_label)

        self.setLayout(layout)

        self.update_conversion()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_conversion)
        self.timer.start(60000)

    def create_widgets(self):
        self.amount_input = QLineEdit()
        self.amount_input.setFont(QFont('Segoe UI', 18))
        self.amount_input.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border-radius: 10px; padding: 10px;")
        self.amount_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.amount_input.textChanged.connect(self.update_conversion)

        self.from_currency_combo = QComboBox()
        self.to_currency_combo = QComboBox()

        self.result_label = QLabel()
        self.result_label.setFont(QFont('Segoe UI', 18))
        self.result_label.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border-radius: 10px; padding: 10px;")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.load_currency_list()

    def load_currency_list(self):
        try:
            response = requests.get(API_URL)
            data = response.json()
            currencies = list(data['conversion_rates'].keys())

            self.from_currency_combo.addItems(currencies)
            self.to_currency_combo.addItems(currencies)
        except requests.RequestException as e:
            print(f"Failed to load currency list: {e}")

    def update_conversion(self):
        try:
            amount = float(self.amount_input.text())
            from_currency = self.from_currency_combo.currentText()
            to_currency = self.to_currency_combo.currentText()

            conversion_rate = self.get_conversion_rate(from_currency, to_currency)
            converted_amount = amount * conversion_rate
            self.result_label.setText(f"{converted_amount:.2f}")
        except ValueError:
            self.result_label.setText("Invalid input")

    def get_conversion_rate(self, from_currency, to_currency):
        try:
            response = requests.get(API_URL)
            data = response.json()
            rates = data['conversion_rates']

            if from_currency == to_currency:
                return 1.0

            return rates[to_currency] / rates[from_currency]
        except requests.RequestException as e:
            print(f"Failed to get conversion rate: {e}")
            return 1.0

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Modern UI Calculator')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2e2e2e;")

        self.converter_widget = CurrencyConverter()
        self.current_widget = None

        self.first_run_file = "first_run.txt"
        if not os.path.exists(self.first_run_file):
            self.open_github_profile()
            with open(self.first_run_file, 'w') as file:
                file.write('This file indicates that the app has run before.')

        self.main_layout = QHBoxLayout(self)
        
        self.side_menu_container = QWidget()
        self.side_menu_toggle_button = QPushButton("☰")
        self.side_menu_toggle_button.setFont(QFont('Segoe UI', 18))
        self.side_menu_toggle_button.setFixedSize(40, 40)
        self.side_menu_toggle_button.setStyleSheet("""
            background-color: #333333;
            color: #FFFFFF;
            border: none;
            border-radius: 20px;
        """)
        self.side_menu_toggle_button.clicked.connect(self.toggle_side_menu)

        self.calculator_widget = QWidget()
        self.create_widgets()
        calculator_layout = QVBoxLayout(self.calculator_widget)
        calculator_layout.addWidget(self.display)
        calculator_layout.addLayout(self.button_layout())
        calculator_layout.addWidget(self.history_list)
        self.calculator_widget.setLayout(calculator_layout)

        self.side_menu = QWidget()
        self.create_side_menu()
        side_menu_layout = QVBoxLayout(self.side_menu)
        side_menu_layout.addWidget(self.github_button)
        side_menu_layout.addWidget(self.mode_toggle_button)
        side_menu_layout.addWidget(self.converter_toggle_button)
        self.side_menu.setLayout(side_menu_layout)

        side_menu_layout = QVBoxLayout(self.side_menu_container)
        side_menu_layout.addWidget(self.side_menu_toggle_button)
        side_menu_layout.addWidget(self.side_menu)
        self.side_menu_container.setLayout(side_menu_layout)
        self.side_menu_container.setFixedWidth(250)

        self.main_layout.addWidget(self.side_menu_container)
        self.main_layout.addWidget(self.calculator_widget)

        self.side_menu_visible = True
        self.current_widget = self.calculator_widget

        self.animation = QPropertyAnimation(self.side_menu_container, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)

        self.button_press_animation = QPropertyAnimation()
        self.button_press_animation.setDuration(200)
        self.button_press_animation.setEasingCurve(QEasingCurve.Type.InOutQuart)

        self.update_ui()
    
    def create_widgets(self):
        self.display = QLineEdit()
        self.display.setFont(QFont('Segoe UI', 24))
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border-radius: 10px; padding: 20px;")
        self.display.setReadOnly(True)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

    def button_layout(self):
        buttons = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('C', '0', '=', '+')
        ]
        layout = QGridLayout()

        for row, row_buttons in enumerate(buttons):
            for col, button_text in enumerate(row_buttons):
                button = QPushButton(button_text)
                button.setFont(QFont('Segoe UI', 18))
                button.setStyleSheet("""
                    background-color: #333333;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                """)
                button.clicked.connect(self.button_clicked)
                layout.addWidget(button, row, col)

        return layout

    def button_clicked(self):
        button = self.sender()
        text = button.text()

        if text == 'C':
            self.display.clear()
        elif text == '=':
            try:
                expression = self.display.text()
                result = eval(expression)
                self.display.setText(str(result))
                self.history_list.addItem(f"{expression} = {result}")
            except Exception as e:
                self.display.setText("Error")
        else:
            self.display.setText(self.display.text() + text)

    def create_side_menu(self):
        self.github_button = QPushButton('Open GitHub')
        self.github_button.setFont(QFont('Segoe UI', 18))
        self.github_button.setStyleSheet("""
            background-color: #333333;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 20px;
        """)
        self.github_button.clicked.connect(self.open_github_profile)

        self.mode_toggle_button = QPushButton('Toggle Mode')
        self.mode_toggle_button.setFont(QFont('Segoe UI', 18))
        self.mode_toggle_button.setStyleSheet("""
            background-color: #333333;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 20px;
        """)
        self.mode_toggle_button.clicked.connect(self.toggle_mode)

        self.converter_toggle_button = QPushButton('Currency Converter')
        self.converter_toggle_button.setFont(QFont('Segoe UI', 18))
        self.converter_toggle_button.setStyleSheet("""
            background-color: #333333;
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 20px;
        """)
        self.converter_toggle_button.clicked.connect(self.toggle_converter)

    def toggle_side_menu(self):
        if self.side_menu_visible:
            self.side_menu.setFixedWidth(0)
        else:
            self.side_menu.setFixedWidth(250)

        self.side_menu_visible = not self.side_menu_visible

    def open_github_profile(self):
        webbrowser.open('https://github.com/Aser-Mohamed/Calculator-App')

    def toggle_mode(self):
        current_mode = QApplication.instance().style().objectName()

        if current_mode == "dark":
            qtmodern.styles.light(QApplication.instance())
        else:
            qtmodern.styles.dark(QApplication.instance())

    def toggle_converter(self):
        if self.current_widget is self.calculator_widget:
            self.current_widget.hide()
            self.current_widget = self.converter_widget
        else:
            self.current_widget.hide()
            self.current_widget = self.calculator_widget

        self.main_layout.addWidget(self.current_widget)
        self.current_widget.show()

    def update_ui(self):
        self.show()
        check_for_updates()

    def on_button_pressed(self, button):
        original_geometry = button.geometry()

        self.button_press_animation.setTargetObject(button)
        self.button_press_animation.setPropertyName(b"geometry")
        self.button_press_animation.setStartValue(original_geometry)
        self.button_press_animation.setEndValue(QRect(original_geometry.x() + 2, original_geometry.y() + 2, original_geometry.width() - 4, original_geometry.height() - 4))
        self.button_press_animation.start()
    
    def on_button_released(self, button):
        self.button_press_animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.button_press_animation.start()

# Update check server
app = Flask(__name__)

@app.route('/check-update', methods=['GET'])
def check_update():
    latest_version = "v1.1.0"
    download_url = "https://github.com/Aser-Mohamed/Calculator-App/releases/latest/download/Calculator-App.zip"
    return jsonify({"latest_version": latest_version, "download_url": download_url})

def run_flask():
    app.run(debug=False, port=5000)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app = QApplication(sys.argv)
    qtmodern.styles.dark(app)

    calculator = Calculator()

    window = qtmodern.windows.ModernWindow(calculator)
    window.show()

    sys.exit(app.exec())
