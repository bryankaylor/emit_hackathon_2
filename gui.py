
import os
import sys
import time

from ansys.aedt.core.emit_core.emit_constants import TxRxMode

import tx_rx_response

import PySide6.QtCore
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QFormLayout, QComboBox, QFileDialog

timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"

print(f'{PySide6.__version__} {PySide6.QtCore.__version__}')


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("EMIT Hackathon 2")

        self.domain = None
        self.revision = None

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
        project_is_aedt = (os.path.splitext(project)[1] == ".aedt")
        if project_exists and project_is_aedt:
            print(f'Loading project {self.projectTextBox.text()}')
            aggressors, victims, domain, revision = tx_rx_response.get_radios(project, "2025.1")
            self.domain = domain
            self.revision = revision

            self.victimComboBox.addItems(victims)
            self.aggressorComboBox.addItems(aggressors)

    def victim_changed(self):
        self.victimBandComboBox.clear()
        victim = self.victimComboBox.currentText()
        victim_bands = self.revision.get_band_names(victim, TxRxMode.RX)
        self.victimBandComboBox.addItems(victim_bands)

    def aggressor_changed(self):
        self.aggressorBandComboBox.clear()
        aggressor = self.aggressorComboBox.currentText()
        aggressor_bands = self.revision.get_band_names(aggressor, TxRxMode.TX)
        self.aggressorBandComboBox.addItems(aggressor_bands)

    def generate(self):
        victim = self.victimComboBox.currentText()
        victim_band = self.victimBandComboBox.currentText()
        aggressor = self.aggressorComboBox.currentText()
        aggressor_band = self.aggressorBandComboBox.currentText()

        print(f'Generating data for {victim}:{victim_band} vs {aggressor}:{aggressor_band}')
        emi, rx_power, desense, sensitivity = tx_rx_response.tx_rx_response(aggressor, victim, aggressor_band, victim_band, self.domain, self.revision)

        for row in emi:
            print(f'{row}')


def main():
    app = QApplication(sys.argv)

    form = Form()
    # form.resize(800, 600)
    form.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
