
import os
import sys

import PySide6.QtCore
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QComboBox, QFileDialog

print(f'{PySide6.__version__} {PySide6.QtCore.__version__}')


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("EMIT Hackathon 2")

        # Widgets
        self.projectTextBox = QLineEdit("")
        self.browseButton = QPushButton("Browse")

        self.victimComboBox = QComboBox()
        self.aggressorComboBox = QComboBox()

        self.victimBandComboBox = QComboBox()
        self.aggressorBandComboBox = QComboBox()

        self.generateDataButton = QPushButton("Generate")

        # Layout
        layout = QFormLayout()
        layout.addRow("Project:", self.projectTextBox)
        layout.addRow(self.browseButton)
        layout.addRow("Victim:", self.victimComboBox)
        layout.addRow("Victim band:", self.victimBandComboBox)
        layout.addRow("Aggressor:", self.aggressorComboBox)
        layout.addRow("Aggressor band:", self.aggressorBandComboBox)
        layout.addRow(self.generateDataButton)

        self.setLayout(layout)

        # Handlers
        self.projectTextBox.textChanged.connect(self.project_changed)
        self.browseButton.clicked.connect(self.browse)
        self.victimComboBox.currentTextChanged.connect(self.victim_changed)
        self.aggressorComboBox.currentTextChanged.connect(self.aggressor_changed)
        self.generateDataButton.clicked.connect(self.generate)

    def browse(self):
        dialog = QFileDialog()
        dialog.setNameFilter("AEDT (*.aedt);; All files (*.*)")

        selected_project = ""
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                selected_project = filenames[0]

        self.projectTextBox.setText(selected_project)

    def project_changed(self):
        self.victimComboBox.clear()
        self.aggressorComboBox.clear()
        self.victimBandComboBox.clear()
        self.aggressorBandComboBox.clear()

        project = self.projectTextBox.text()
        project_exists = os.path.exists(project)
        if project_exists:
            print(f'Loading project {self.projectTextBox.text()}')
            victims = ["V1", "V2", "V3"]
            aggressors = ["A1", "A2", "A3"]
            self.victimComboBox.addItems(victims)
            self.aggressorComboBox.addItems(aggressors)

    def victim_changed(self):
        self.victimBandComboBox.clear()
        victim_bands = ["VB1", "VB2"]
        self.victimBandComboBox.addItems(victim_bands)

    def aggressor_changed(self):
        self.aggressorBandComboBox.clear()
        aggressor_bands = ["AB1", "AB2"]
        self.aggressorBandComboBox.addItems(aggressor_bands)

    def generate(self):
        victim = self.victimComboBox.currentText()
        victim_band = self.victimBandComboBox.currentText()
        aggressor = self.aggressorComboBox.currentText()
        aggressor_band = self.aggressorBandComboBox.currentText()

        print(f'Generating data for {victim}:{victim_band} vs {aggressor}:{aggressor_band}')


def main():
    app = QApplication(sys.argv)

    form = Form()
    # form.resize(800, 600)
    form.show()

    sys.exit(app.exec())
    pass


if __name__ == "__main__":
    main()
