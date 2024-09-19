import os
import sys
import requests
import webbrowser
from PySide6 import QtWidgets, QtCore, QtGui

# Windows-specific import for Mica effects
if sys.platform == "win32":
    try:
        from win32mica import ApplyMica, MicaTheme, MicaStyle
        USE_MICA = True
    except ImportError:
        USE_MICA = False
else:
    USE_MICA = False

# Constants for GitHub API and versioning
GITHUB_API_RELEASES = "https://api.github.com/repos/Aser-Mohamed/Calculator-App/releases/latest"
LOCAL_VERSION = "1.1.0"  # Your app's current version

class Calculator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Calculator")
        self.setGeometry(100, 100, 400, 600)

        # Apply Mica effect for Windows (if on Windows and Mica is available)
        if USE_MICA:
            ApplyMica(self.winId(), MicaTheme.AUTO, MicaStyle.DEFAULT)

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Initialize the UI
        self.init_ui()
        
        # Initialize current input and operator
        self.current_input = ""
        self.previous_input = ""
        self.operator = None

        # Check for updates when the app starts
        self.check_for_updates()

    def init_ui(self):
        """Initialize the calculator UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Result box
        self.result = QtWidgets.QLabel("0")
        self.result.setAlignment(QtCore.Qt.AlignRight)
        self.result.setFixedHeight(100)  # Increase result box height
        self.result.setStyleSheet("""\
            font-size: 48px;
            color: white;
            padding: 20px;
            background-color: #2c2c2c;
            border-radius: 10px;
        """)
        layout.addWidget(self.result)

        # Button layout
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)

        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('÷', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('×', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
            ('0', 3, 0, 1, 2), ('.', 3, 2), ('=', 3, 3),
            ('C', 4, 0, 1, 2), ('⌫', 4, 2), ('+', 4, 3)
        ]

        for button_info in buttons:
            if len(button_info) == 3:
                text, row, col = button_info
                rowspan = colspan = 1
            elif len(button_info) == 5:
                text, row, col, rowspan, colspan = button_info
            else:
                continue

            button = QtWidgets.QPushButton(text)
            button.setStyleSheet("""\
                QPushButton {
                    font-size: 20px;
                    color: white;
                    background-color: #333333;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
                QPushButton:pressed {
                    background-color: #555555;
                }
            """)
            button.clicked.connect(self.on_button_click)
            grid_layout.addWidget(button, row, col, rowspan, colspan)

        layout.addLayout(grid_layout)

        # Create an update button to trigger updates manually
        self.update_button = QtWidgets.QPushButton("Check for Update")
        self.update_button.clicked.connect(self.check_for_updates)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def on_button_click(self):
        """Handle button click events for calculator operations."""
        button_text = self.sender().text()

        if button_text in '0123456789.':
            self.current_input += button_text
            self.update_result()

        elif button_text in '+-×÷':
            if self.operator:
                self.calculate()
            self.previous_input = self.current_input
            self.current_input = ""
            self.operator = button_text

        elif button_text == 'C':
            self.current_input = ""
            self.previous_input = ""
            self.operator = None
            self.update_result()

        elif button_text == '=':
            self.calculate()
            self.operator = None

        elif button_text == '⌫':
            # Remove the last character from current input
            self.current_input = self.current_input[:-1]
            self.update_result()

    def keyPressEvent(self, event):
        """Handle key press events for calculator operations."""
        key = event.key()
        key_text = event.text()

        if key_text in '0123456789.':
            self.current_input += key_text
            self.update_result()

        elif key_text in '+-×÷':
            if self.operator:
                self.calculate()
            self.previous_input = self.current_input
            self.current_input = ""
            self.operator = key_text

        elif key == QtCore.Qt.Key_Backspace:
            # Remove the last character from current input
            self.current_input = self.current_input[:-1]
            self.update_result()

        elif key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            self.calculate()
            self.operator = None

        elif key_text == 'c' or key_text == 'C':
            self.current_input = ""
            self.previous_input = ""
            self.operator = None
            self.update_result()

        event.accept()

    def calculate(self):
        """Perform calculation based on the operator."""
        if self.operator and self.previous_input:
            try:
                # Replace ÷ with / and × with * for calculation
                expression = self.current_input.replace('÷', '/').replace('×', '*')

                # Construct the full expression for evaluation
                full_expression = f"{self.previous_input} {self.operator.replace('×', '*').replace('÷', '/')} {expression}"

                # Evaluate the expression
                result = eval(full_expression)

                # Convert result to integer if it's a whole number
                if isinstance(result, float) and result.is_integer():
                    result = int(result)

                # Update current input with the result
                self.current_input = str(result)
                self.update_result()

            except (SyntaxError, ZeroDivisionError) as e:
                # Handle specific errors for syntax issues or division by zero
                self.current_input = "Error"
                self.update_result()
            except Exception as e:
                # Handle any other unforeseen errors
                self.current_input = "Error"
                self.update_result()

    def update_result(self):
        """Update the display result."""
        self.result.setText(self.current_input if self.current_input else "0")

    def check_for_updates(self):
        """Check GitHub for the latest release and compare with the local version."""
        try:
            response = requests.get(GITHUB_API_RELEASES)
            response.raise_for_status()

            latest_release = response.json()
            latest_version = latest_release['tag_name']

            # Check if a newer version exists
            if self.is_newer_version(latest_version, LOCAL_VERSION):
                # Prompt user if they want to visit the GitHub releases page
                update_prompt = QtWidgets.QMessageBox.question(
                    self, "New Update Available",
                    f"Version {latest_version} is available. Do you want to download it?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if update_prompt == QtWidgets.QMessageBox.Yes:
                    # Find the 'Calculator-App.zip' asset in the release assets
                    for asset in latest_release['assets']:
                        if asset['name'] == 'Calculator-App.zip':
                            download_url = asset['browser_download_url']
                            # Open the download URL in the user's default browser
                            webbrowser.open(download_url)
                            QtWidgets.QMessageBox.information(
                                self, "Redirecting",
                                "You will be redirected to the download page. Please download and replace the files manually."
                            )
                            break
                else:
                    QtWidgets.QMessageBox.information(
                        self, "Update Declined",
                        "You have declined the update."
                    )
            # No update message if no update is available
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(
                self, "Update Error",
                f"Error checking for updates: {e}"
            )

    def is_newer_version(self, latest_version, local_version):
        """Compare the latest version from GitHub with the local version."""
        latest_version_parts = list(map(int, latest_version.lstrip('v').split('.')))
        local_version_parts = list(map(int, local_version.split('.')))

        return latest_version_parts > local_version_parts

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())
