from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPlainTextEdit, QPushButton, QWidget, QProcess
import sys
from PyQt6.QtCore import QProcess
class PythonIDE(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python IDE")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.editor = QPlainTextEdit(self)
        self.layout.addWidget(self.editor)

        self.terminal = QPlainTextEdit(self)
        self.layout.addWidget(self.terminal)

        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.run_python_script)
        self.layout.addWidget(self.run_button)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)

    def run_python_script(self):
        script = self.editor.toPlainText()
        self.terminal.clear()
        self.process.start("python", ["-c", script])

    def handle_output(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.terminal.appendPlainText(data)

    def handle_error(self):
        data = self.process.readAllStandardError().data().decode()
        self.terminal.appendPlainText(f"Error: {data}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ide = PythonIDE()
    ide.show()
    sys.exit(app.exec())
