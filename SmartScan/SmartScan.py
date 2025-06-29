from pathlib import WindowsPath
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTreeView, QTextEdit, QFileSystemModel,
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget, QToolBar
)
from PySide6.QtCore import Qt, QDir; from PySide6.QtGui import QAction, QIcon
import ErrorWindow
import FileTree, CodeArea, RepoPath, SlitherScanner
import time

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
        1. Save the current file (which is opened)
        2. Generate the Slither Report File (after the analysis is done)
        """
        menu_bar = self.menuBar()
        

        action_save_current_file = QAction("Save", self)
        action_save_current_file.triggered.connect(self.save_current_file)

        action_open_error_window = QAction("Open Error Window", self)
        action_open_error_window.triggered.connect(self.open_error_window)
        
        menu_bar.addAction(action_save_current_file)
        menu_bar.addAction(action_open_error_window)
        self.star_actions = list()

        star_action1 = QAction(QIcon("red-star.png"), "Star Item 1", self)
        star_action1.setEnabled(False)
        self.star_actions.append(star_action1)
        menu_bar.addAction(star_action1)

        star_action2 = QAction(QIcon("red-star.png"), "Star Item 2", self)
        star_action2.setEnabled(False)
        self.star_actions.append(star_action2)
        menu_bar.addAction(star_action2)

        star_action3 = QAction(QIcon("red-star.png"), "Star Item 3", self)
        star_action3.setEnabled(False)
        self.star_actions.append(star_action3)
        menu_bar.addAction(star_action3)

        star_action4 = QAction(QIcon("red-star.png"), "Star Item 4", self)
        star_action4.setEnabled(False)
        self.star_actions.append(star_action4)
        menu_bar.addAction(star_action4)

        star_action5 = QAction(QIcon("red-star.png"), "Star Item 5", self)
        star_action5.setEnabled(False)
        self.star_actions.append(star_action5)
        menu_bar.addAction(star_action5)

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
        welcomeMessage = "Welcome to SmartScan! \n\n"
        welcomeMessage += "If your repository is private, please insert the API Key in API_KEY.txt for SmartScan to access it.\n\n"
        welcomeMessage += "Insert the GitHub repository link and press 'Analyze'.\n\n"
        self.analyzed_code_area.setPlainText(welcomeMessage)
        self.analyzed_code_area.zoomIn(5)
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

        self.SlitherScanner = None

        self.initEvents()

        self.alreadyZoomed = False

        self.file_to_errors_mapping = dict()
        
    def save_current_file(self):
        with open(self.currentFilePath, "w+") as currentFile:
            currentFile.write(self.analyzed_code_area.toPlainText())
        print(f"Current file saved: {self.currentFilePath}")
        
    def open_error_window(self):
        self.analyzed_code_area.ErrorWindow.show()

    def set_api_key(self):
        print("Private API Key set!")

    def initEvents(self):
        # Create event for run_button press
        self.repo_path.run_button.clicked.connect(self.on_run_button_clicked)

        # FileTree Events
        self.file_tree.doubleClicked.connect(self.on_file_selected)

    def on_file_selected(self, index):
        file_path = self.file_tree.on_file_selected(index)

        if file_path != "":
            try:
                with open(file_path, "r+") as currentFile:
                    content = currentFile.read()

                    file_path_split = file_path.split("/")

                    file_name = file_path_split[len(file_path_split) - 1]

                    if file_name != "security_report.txt" and file_name != "API_KEY.txt":
                        self.analyzed_code_area.affected_lines = self.file_tree.affected_lines_mapping[WindowsPath(file_path)]
                        self.analyzed_code_area.file_to_errors_mapping = self.file_to_errors_mapping[WindowsPath(file_path)]
                        if not self.alreadyZoomed:
                            self.analyzed_code_area.zoomOut(5)
                            self.alreadyZoomed = True

                    else:
                        self.analyzed_code_area.affected_lines.clear()

                    self.analyzed_code_area.setPlainText(content)
                    self.currentFilePath = file_path
            except Exception as e:
                print(f"Error reading file: {e}")

    def on_run_button_clicked(self):
        analisys_time_start = time.time()
        # Reset the star rating
        for i in range(5):
            self.star_actions[i].setEnabled(False)

        contracts = self.repo_path.on_run_button_clicked() # get the smart contracts

        if self.repo_path.failed:
            content = "The cloning process failed."
            content += "\n\nPlease make sure you are connected to the internet and that the repository link is valid and try again."
            self.analyzed_code_area.affected_lines = []
            self.analyzed_code_area.setPlainText(content)
            return


        if len(contracts) == 0:
            content = f"No Solidity file found in the cloned repository.\n"
            content += "Please try again with another project."

            self.analyzed_code_area.setPlainText(content)
            return

        self.SlitherScanner = SlitherScanner.SlitherScanner()
        for contract in contracts:
            self.SlitherScanner.solidity_analysis(contract)
            errors_list = self.SlitherScanner.errors_list
            self.file_to_errors_mapping[contract] = errors_list

        self.file_tree.affected_lines_mapping = self.SlitherScanner.affected_lines_mapping
        analisys_time_end = time.time()
        elapsed_time = round(analisys_time_end - analisys_time_start, 2)
        print("Repository scanned successfuly!")

        content = f"Repository scanned successfuly! (in {elapsed_time} second(s))\n\n"
        content += self.SlitherScanner.generate_severity_report()
        content += "\n The cloned project can be accessed in the ClonedRepo directory."
        content += "\n\n Double click any .sol file to see its code."
        content += "\n\n All the affected lines will be highlighted."
        content += " Navigate the console to see each error."

        self.analyzed_code_area.affected_lines = []
        self.analyzed_code_area.setPlainText(content)

        # Reset the stars color
        for i in range(5):
            self.star_actions[i].setEnabled(False)

        # Set the stars color based on the severity score
        for i in range(self.SlitherScanner.stars):
            self.star_actions[i].setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()