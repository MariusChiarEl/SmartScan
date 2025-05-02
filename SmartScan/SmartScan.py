from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTreeView, QTextEdit, QFileSystemModel,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget, QToolBar
)
from PySide6.QtCore import Qt, QDir; from PySide6.QtGui import QAction
import FileTree; import CodeArea; import RepoPath

"""
Main window logic: Contains the components: CodeArea, FileTree and RepoPath
CodeArea -> Shows the analyzed code from the selected file
FileTree -> Shows the analyzed project
RepoPath -> Takes the path to the repository as input
"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("SmartScan")
        self.setGeometry(100, 100, 1200, 800)

        """
        Add Menu Bar. It will hold the following functionalities:
        1. Saving the current file (which is opened)
        2. Setting the API Key (for private repos)
        3. Generate the Slither Report File (after the analysis is done)
        """
        menu_bar = self.menuBar()
        

        action_save_current_file = QAction("Save", self)
        action_save_current_file.triggered.connect(self.save_current_file)
        menu_bar.addAction(action_save_current_file)

        action_set_api_key = QAction("Set API Key", self)
        action_set_api_key.triggered.connect(self.set_api_key)
        menu_bar.addAction(action_set_api_key)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        """
        Create a horizontal splitter
        This way, you may resize the FileTreeView to see longer file names
        or drag it away to the right to see longer code lines.
        """
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Container for CodeArea and RepoPath
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # Add CodeArea
        self.analyzed_code_area = CodeArea.CodeArea()
        left_layout.addWidget(self.analyzed_code_area, stretch=1)  # Make it stretch to fill available space

        # Add RepoPath
        self.repo_path = RepoPath.RepoPath()

        left_layout.addWidget(self.repo_path, stretch=0)  # Prevent the bottom row from stretching

        # Add the left side to the splitter
        splitter.addWidget(left_container)

        # Add the FileTree to the right side
        self.file_tree = FileTree.FileTree()
        splitter.addWidget(self.file_tree)

        # Add the splitter to the layout
        layout.addWidget(splitter)

        # Set initial sizes for the splitter (left side : 75%, right side : 25%)
        splitter.setSizes([int(self.width() * 0.75), int(self.width() * 0.25)])

        self.initEvents()
        
    def save_current_file(self):
        with open(self.currentFilePath, "w+") as currentFile:
            currentFile.write(self.analyzed_code_area.toPlainText())
        print(f"Current file saved: {self.currentFilePath}")

    def set_api_key(self):
        print("Private API Key set!")

    def initEvents(self):
        """
        RepoPath Events
        """
        # Create event for run_button press
        self.repo_path.run_button.clicked.connect(self.repo_path.on_run_button_clicked)

        """
        FileTree Events
        """
        self.file_tree.doubleClicked.connect(self.on_file_selected)

    def on_file_selected(self, index):
        file_path = self.file_tree.on_file_selected(index)

        if file_path != "":
            try:
                with open(file_path, "r+") as currentFile:
                    content = currentFile.read()
                    self.analyzed_code_area.setPlainText(content)
                    self.currentFilePath = file_path
            except Exception as e:
                print(f"Error reading file: {e}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()