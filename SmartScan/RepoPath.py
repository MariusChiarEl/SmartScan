from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QPushButton)
from PySide6.QtCore import QDir

import GitHubImport

from pathlib import Path
import os

class RepoPath(QWidget):

    def __init__(self):
        super().__init__()

        self.bottom_layout = QHBoxLayout(self)

        # Text input (QLineEdit)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter the GitHub repository path...")
        self.bottom_layout.addWidget(self.text_input)

        # Button (QPushButton)
        self.run_button = QPushButton("Analyze")
        self.bottom_layout.addWidget(self.run_button)

    def on_run_button_clicked(self):
        """Event for run_button press"""

        git_hub_import = GitHubImport.GitHubImport(self.text_input.text())
        clone_dir = os.path.join(os.getcwd(), "ClonedRepo")

        dir = Path(clone_dir)

        contracts = []
        for contract in dir.rglob("*.sol"):
            contracts.append(contract)

        return contracts

    