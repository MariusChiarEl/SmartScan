from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QPushButton)
from PySide6.QtCore import QDir

import GitHubImport

from slither import Slither
from slither.detectors import all_detectors
import inspect
from slither.detectors.abstract_detector import AbstractDetector

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

        git_hub_import = GitHubImport.GitHubImport(self.text_input.text(), "")
        clone_dir = os.path.join(os.getcwd(), "ClonedRepo")

        dir = Path(clone_dir)

        for contract in dir.rglob("*.sol"):
            self.solidity_analysis(contract)

    def solidity_analysis(self, path):
        try:
            slither = Slither(str(path))
            
            # Get all detector classes
            detectors_ = [getattr(all_detectors, name) for name in dir(all_detectors)]
            detector_classes = [d for d in detectors_ if inspect.isclass(d) and issubclass(d, AbstractDetector)]

            # Register all detectors
            for detector_cls in detector_classes:
                slither.register_detector(detector_cls)

            # Run detectors
            detector_resultss = slither.run_detectors()

            # Flatten the list of results (essentially merges the lists for the found vulnerabilities from each detector)
            detector_results = [item for sublist in detector_resultss for item in sublist]

            vulnerabilities_found = False

            for result in detector_results:
                vulnerabilities_found = True

                # Get the specifications of each vulnerability

                #detector_name = result.get('check', 'N/A')
                #severity = result.get('impact', 'N/A')
                #confidence = result.get('confidence', 'N/A')
                description = result.get('description', 'N/A')
                elements = result.get('elements', 'N/A')

                source_mapping = elements[0].get("source_mapping", {})
                lines = source_mapping.get("lines", [])
                print(f"Error: {lines[0]} - {lines[-1]}")
                print(description)

                print("-" * 20)

            if not vulnerabilities_found:
                print(f"No vulnerabilities found!")

        except FileNotFoundError:
            print(f"Error: Solidity file not found.")
        except Exception as e:
            print(f"An error occurred during analysis: {e}")
    