from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QComboBox, QFormLayout
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
import qtmodern.styles
import qtmodern.windows
import webbrowser
import os
import requests

# Replace with your own API key from ExchangeRate-API or other service
API_KEY = ' 8482bf59cdfccb689631bdef'
API_URL = 'https://v6.exchangerate-api.com/v6/8482bf59cdfccb689631bdef/latest/USD'

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

        # Set up a timer to refresh conversion rates periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_conversion)
        self.timer.start(60000)  # Update every minute

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
        # Load currency list from API
        response = requests.get(API_URL.format(API_KEY))
        data = response.json()
        currencies = list(data['conversion_rates'].keys())

        self.from_currency_combo.addItems(currencies)
        self.to_currency_combo.addItems(currencies)

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
        response = requests.get(API_URL.format(API_KEY))
        data = response.json()
        rates = data['conversion_rates']

        if from_currency == to_currency:
            return 1.0

        return rates[to_currency] / rates[from_currency]

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Modern UI Calculator')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2e2e2e;")

        # Initialize the converter widget
        self.converter_widget = CurrencyConverter()

        # Initialize the current widget
        self.current_widget = None

        # First launch check
        self.first_run_file = "first_run.txt"
        if not os.path.exists(self.first_run_file):
            self.open_github_profile()
            with open(self.first_run_file, 'w') as file:
                file.write('This file indicates that the app has run before.')

        # Create main layout
        self.main_layout = QHBoxLayout(self)
        
        # Create the side menu container and toggle button
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

        # Create the calculator widget
        self.calculator_widget = QWidget()
        self.create_widgets()
        calculator_layout = QVBoxLayout(self.calculator_widget)
        calculator_layout.addWidget(self.display)
        calculator_layout.addLayout(self.button_layout())
        calculator_layout.addWidget(self.history_list)
        self.calculator_widget.setLayout(calculator_layout)

        # Create the side menu
        self.side_menu = QWidget()
        self.create_side_menu()
        side_menu_layout = QVBoxLayout(self.side_menu)
        side_menu_layout.addWidget(self.github_button)
        side_menu_layout.addWidget(self.mode_toggle_button)
        side_menu_layout.addWidget(self.converter_toggle_button)
        self.side_menu.setLayout(side_menu_layout)

        # Set up the layout for the side menu container
        side_menu_layout = QVBoxLayout(self.side_menu_container)
        side_menu_layout.addWidget(self.side_menu_toggle_button)
        side_menu_layout.addWidget(self.side_menu)
        self.side_menu_container.setLayout(side_menu_layout)
        self.side_menu_container.setFixedWidth(250)  # Adjusted fixed width for better layout

        # Add widgets to main layout
        self.main_layout.addWidget(self.side_menu_container)
        self.main_layout.addWidget(self.calculator_widget)

        # Set initial state
        self.side_menu_visible = True
        self.current_widget = self.calculator_widget  # Set the initial widget to calculator
        self.update_side_menu_visibility()

        # Create animations
        self.animation = QPropertyAnimation(self.side_menu_container, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)

        # Create button press animations
        self.button_press_animation = QPropertyAnimation()
        self.button_press_animation.setDuration(100)
        self.button_press_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        self.show()

    def create_widgets(self):
        self.display = QLineEdit()
        self.display.setFont(QFont('Segoe UI', 24))
        self.display.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border-radius: 10px; padding: 10px;")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            background-color: #1e1e1e; 
            color: #ffffff; 
            border-radius: 10px; 
            padding: 5px;
            margin: 5px;
        """)

    def button_layout(self):
        layout = QGridLayout()

        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('+', 4, 3),
            ('C', 5, 0), ('=', 5, 1, 1, 3)
        ]

        for button in buttons:
            if len(button) == 3:
                text, row, col = button
                rowspan, colspan = 1, 1
            elif len(button) == 4:
                text, row, col, rowspan = button
                colspan = 1
            elif len(button) == 5:
                text, row, col, rowspan, colspan = button
            else:
                continue

            button_widget = QPushButton(text)
            button_widget.setFont(QFont('Segoe UI', 18))
            button_widget.setStyleSheet(f"""
                background-color: #444444; 
                color: #FFFFFF; 
                border-radius: 10px; 
                padding: 15px;
                margin: 5px;
            """)
            button_widget.clicked.connect(lambda checked, key=text: self.on_button_click(key))
            button_widget.installEventFilter(self)  # Install event filter for visual effects
            layout.addWidget(button_widget, row, col, rowspan, colspan)

        return layout

    def create_side_menu(self):
        self.github_button = QPushButton("GitHub Repository")
        self.github_button.setFont(QFont('Segoe UI', 14))
        self.github_button.setStyleSheet("""
            background-color: #444444; 
            color: #FFFFFF; 
            border-radius: 10px; 
            padding: 15px;
            margin: 10px;
        """)
        self.github_button.clicked.connect(self.open_github_profile)

        self.mode_toggle_button = QPushButton("Toggle Mode")
        self.mode_toggle_button.setFont(QFont('Segoe UI', 14))
        self.mode_toggle_button.setStyleSheet("""
            background-color: #444444; 
            color: #FFFFFF; 
            border-radius: 10px; 
            padding: 15px;
            margin: 10px;
        """)
        self.mode_toggle_button.clicked.connect(self.toggle_mode)

        self.converter_toggle_button = QPushButton("Currency Converter")
        self.converter_toggle_button.setFont(QFont('Segoe UI', 14))
        self.converter_toggle_button.setStyleSheet("""
            background-color: #444444; 
            color: #FFFFFF; 
            border-radius: 10px; 
            padding: 15px;
            margin: 10px;
        """)
        self.converter_toggle_button.clicked.connect(self.toggle_converter)

    def toggle_side_menu(self):
        if self.side_menu_visible:
            end_rect = QRect(-self.side_menu_container.width(), 0, self.side_menu_container.width(), self.side_menu_container.height())
            self.animation.setStartValue(self.side_menu_container.geometry())
            self.animation.setEndValue(end_rect)
            self.animation.start()
        else:
            end_rect = QRect(0, 0, self.side_menu_container.width(), self.side_menu_container.height())
            self.animation.setStartValue(self.side_menu_container.geometry())
            self.animation.setEndValue(end_rect)
            self.animation.start()
        self.side_menu_visible = not self.side_menu_visible

    def update_side_menu_visibility(self):
        if self.side_menu_visible:
            self.side_menu_container.setGeometry(QRect(0, 0, self.side_menu_container.width(), self.side_menu_container.height()))
        else:
            self.side_menu_container.setGeometry(QRect(-self.side_menu_container.width(), 0, self.side_menu_container.width(), self.side_menu_container.height()))

    def toggle_mode(self):
        if "background-color: #2e2e2e;" in self.styleSheet():
            self.setStyleSheet("background-color: #ffffff;")  # Light mode
            self.display.setStyleSheet("background-color: #f0f0f0; color: #000000; border-radius: 10px; padding: 10px;")
            self.mode_toggle_button.setText("Switch to Dark Mode")
        else:
            self.setStyleSheet("background-color: #2e2e2e;")  # Dark mode
            self.display.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border-radius: 10px; padding: 10px;")
            self.mode_toggle_button.setText("Switch to Light Mode")

    def toggle_converter(self):
        if self.current_widget == self.calculator_widget:
            self.main_layout.removeWidget(self.calculator_widget)
            self.calculator_widget.setParent(None)
            self.main_layout.addWidget(self.converter_widget)
            self.current_widget = self.converter_widget
        elif self.current_widget == self.converter_widget:
            self.main_layout.removeWidget(self.converter_widget)
            self.converter_widget.setParent(None)
            self.main_layout.addWidget(self.calculator_widget)
            self.current_widget = self.calculator_widget

    def on_button_click(self, key):
        if key == 'C':
            self.display.clear()
        elif key == '=':
            try:
                expression = self.display.text()
                result = str(eval(expression))  # NOTE: eval is used for simplicity; use safer methods in production
                self.display.setText(result)
                self.history_list.addItem(expression + ' = ' + result)
            except Exception:
                self.display.setText('Error')
        else:
            current_text = self.display.text()
            self.display.setText(current_text + key)

    def open_github_profile(self):
        webbrowser.open('https://github.com/Aser-Mohamed/Calculator-App')

    def eventFilter(self, obj, event):
        if event.type() == event.Type.MouseButtonPress and obj in self.findChildren(QPushButton):
            obj.setStyleSheet("""
                background-color: #555555; 
                color: #FFFFFF; 
                border-radius: 10px; 
                padding: 15px;
                margin: 5px;
            """)
        elif event.type() == event.Type.MouseButtonRelease and obj in self.findChildren(QPushButton):
            obj.setStyleSheet("""
                background-color: #444444; 
                color: #FFFFFF; 
                border-radius: 10px; 
                padding: 15px;
                margin: 5px;
            """)
        return super().eventFilter(obj, event)

if __name__ == '__main__':
    app = QApplication([])
    qtmodern.styles.dark(app)
    window = qtmodern.windows.ModernWindow(Calculator())
    window.show()
    app.exec()
