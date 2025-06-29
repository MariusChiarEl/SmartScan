from PySide6.QtGui import QWindow, QTextBlock
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPlainTextEdit, QScrollBar

# Separate Window that displays the specific error whenever the user clicks on a line
# In the main CodeArea

class ErrorWindow(QMainWindow):
    def __init__(self):
        # Set window title and size
        super().__init__()
        self.setGeometry(1500, 100, 1000, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.error_description_box = QTextEdit()
        self.error_description_box.setReadOnly(True)
        layout.addWidget(self.error_description_box)

        content = "Click any affected line of code and the error description will show here."
        self.error_description_box.setPlainText(content)