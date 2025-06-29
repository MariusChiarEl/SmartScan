from PySide6.QtWidgets import (QTreeView, QFileSystemModel)
from PySide6.QtCore import QDir
from PySide6.QtGui import QFileOpenEvent

class FileTree(QTreeView):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTreeView {
                border: 2px solid gray;
                border-radius: 10px;  /* Rounded corners */
                padding: 5px;         /* Padding inside the tree view */
                margin: 10;
            }
            QTreeView::item {
                padding: 5px;         /* Padding for each item */
            }
        """)
        self.setHeaderHidden(True)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())  # Set the root path to the current directory
        self.setModel(self.file_model)
        self.setRootIndex(self.file_model.index(QDir.currentPath()))  # Display the current directory
        self.setHeaderHidden(True) # hide the headers

        # Show the file/directory names only
        for column in range(1, self.file_model.columnCount()):
            self.hideColumn(column)

        self.affected_lines_mapping = dict()

    def on_file_selected(self, index):
        file_path = self.file_model.filePath(index)

        file_path_split = file_path.split("/")

        file_name = file_path_split[len(file_path_split) - 1]

        if file_name == "security_report.txt" or file_name == "API_KEY.txt":
            return file_path

        if len(file_name.split(".")) < 2:
            return ""

        file_extension = file_name.split(".")[1]

        if file_extension == "sol":
            return file_path
        else:
            return ""
