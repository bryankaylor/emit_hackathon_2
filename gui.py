
import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np

from ansys.aedt.core.emit_core.emit_constants import TxRxMode

from result_manager import LoadAEDTWorker, ResultManager, RunWorker, get_results
import waterfall
from export_csv import export_csv

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QComboBox, QFileDialog, \
                              QGroupBox, QMainWindow, QGridLayout, QStatusBar, QProgressBar, QLabel, QWidget

timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"


class Form(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.setWindowTitle("EMIT Hackathon 2")

        self.emitApp = None
        self.resultManager = None
        self.results = None
        self.loadWorker = None
        self.runWorker = None
        self.projectFilePath = None

        # Widgets
        self.projectLabel = QLabel('Project:')
        self.projectTextBox = QLineEdit('')
        self.projectTextBox.setDisabled(True)
        self.browseButton = QPushButton('...')

        self.radiosGroupBox = QGroupBox('Radios')
        self.victimLabel = QLabel('Victim:')
        self.victimComboBox = QComboBox()
        self.aggressorLabel = QLabel('Aggressor:')
        self.aggressorComboBox = QComboBox()
        self.victimBandLabel = QLabel('Victim band:')
        self.victimBandComboBox = QComboBox()
        self.aggressorBandLabel = QLabel('Aggressor band:')
        self.aggressorBandComboBox = QComboBox()

        self.runButton = QPushButton("Run")

        self.actionsGroupBox = QGroupBox('Actions')
        self.generateDataButton = QPushButton("Generate")
        self.generateDataButton.setEnabled(False)
        self.waterfallButton = QPushButton("Waterfall")
        self.waterfallButton.setEnabled(False)

        self.runProgressBar = QProgressBar()
        self.runProgressBar.hide()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Ready')
        self.statusBar.addPermanentWidget(self.runProgressBar)
        self.statusBar.setSizeGripEnabled(False)

        # Layout
        layout = QGridLayout(central_widget)
        layout.addWidget(self.projectLabel, 0, 0)
        layout.addWidget(self.projectTextBox, 0, 1)
        layout.addWidget(self.browseButton, 0, 2)

        radios_group_box_layout = QGridLayout()
        radios_group_box_layout.addWidget(self.victimLabel, 0, 0)
        radios_group_box_layout.addWidget(self.victimComboBox, 0, 1, 1, 2)
        radios_group_box_layout.addWidget(self.victimBandLabel, 1, 0,)
        radios_group_box_layout.addWidget(self.victimBandComboBox, 1, 1, 1, 2)
        radios_group_box_layout.addWidget(self.aggressorLabel, 2, 0,)
        radios_group_box_layout.addWidget(self.aggressorComboBox, 2, 1, 1, 2)
        radios_group_box_layout.addWidget(self.aggressorBandLabel, 3, 0)
        radios_group_box_layout.addWidget(self.aggressorBandComboBox, 3, 1, 1, 2)
        self.radiosGroupBox.setLayout(radios_group_box_layout)
        layout.addWidget(self.radiosGroupBox, 1, 0, 4, 3)

        layout.addWidget(self.runButton, 5, 0, 1, 3)

        actions_group_box_layout = QGridLayout()
        actions_group_box_layout.addWidget(self.generateDataButton, 0, 0)
        actions_group_box_layout.addWidget(self.waterfallButton, 1, 0)
        self.actionsGroupBox.setLayout(actions_group_box_layout)
        layout.addWidget(self.actionsGroupBox, 6, 0, 2, 3)

        self.setLayout(layout)

        # Handlers
        # self.projectTextBox.textChanged.connect(self.project_changed)
        self.browseButton.clicked.connect(self.browse)
        self.victimComboBox.currentTextChanged.connect(self.victim_changed)
        self.victimBandComboBox.currentTextChanged.connect(self.victim_band_changed)
        self.aggressorComboBox.currentTextChanged.connect(self.aggressor_changed)
        self.aggressorBandComboBox.currentTextChanged.connect(self.aggressor_band_changed)
        self.runButton.clicked.connect(self.run_start)
        self.generateDataButton.clicked.connect(self.generate)
        self.waterfallButton.clicked.connect(self.waterfall)

    def set_actions_enabled(self, value):
        self.generateDataButton.setEnabled(value)
        self.waterfallButton.setEnabled(value)

    def get_victim(self, name):
        victims = [victim for victim in self.resultManager.victims if victim.name == name]
        return victims[0]

    def get_aggressor(self, name):
        aggressors = [aggressor for aggressor in self.resultManager.aggressors if aggressor.name == name]
        return aggressors[0]

    def browse(self):
        dialog = QFileDialog()
        dialog.setNameFilter("AEDT (*.aedt);; All files (*.*)")

        selected_project = ""
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if filenames:
                selected_project = filenames[0]

        self.projectFilePath = selected_project
        self.project_changed()

    def project_changed(self):
        self.victimComboBox.clear()
        self.aggressorComboBox.clear()
        self.victimBandComboBox.clear()
        self.aggressorBandComboBox.clear()

        self.set_actions_enabled(False)

        project_exists = os.path.exists(self.projectFilePath)
        project_name, project_extension = os.path.splitext(os.path.basename(self.projectFilePath))
        project_is_aedt = (project_extension == '.aedt')
        if project_exists and project_is_aedt:
            self.statusBar.showMessage(f'Loading project {project_name}...')
            self.projectTextBox.setText(project_name)
            self.projectTextBox.setToolTip(self.projectFilePath)
            self.load_aedt_worker_start()
        else:
            self.projectFilePath = None
            self.projectTextBox.setText('')
            self.projectTextBox.setToolTip('')

    def victim_changed(self):
        self.victimBandComboBox.clear()
        victim_name = self.victimComboBox.currentText()
        victim = self.get_victim(victim_name)
        # self.victimBandComboBox.addItem('All')
        self.victimBandComboBox.addItems([band.name for band in victim.bands])
        self.set_actions_enabled(False)

    def victim_band_changed(self):
        self.set_actions_enabled(False)

    def aggressor_changed(self):
        self.aggressorBandComboBox.clear()
        aggressor_name = self.aggressorComboBox.currentText()
        aggressor = self.get_aggressor(aggressor_name)
        # self.aggressorBandComboBox.addItem('All')
        self.aggressorBandComboBox.addItems([band.name for band in aggressor.bands])
        self.set_actions_enabled(False)

    def aggressor_band_changed(self):
        self.set_actions_enabled(False)

    def load_aedt_worker_start(self):
        self.loadWorker = LoadAEDTWorker(self.projectFilePath)
        self.loadWorker.finished.connect(self.load_aedt_worker_complete)
        self.loadWorker.start()

    def load_aedt_worker_complete(self):
        if self.loadWorker:
            self.emitApp = self.loadWorker.emitApp
            self.resultManager = ResultManager(self.emitApp)
            self.victimComboBox.addItems([victim.name for victim in self.resultManager.victims])
            self.aggressorComboBox.addItems([aggressor.name for aggressor in self.resultManager.aggressors])
            self.statusBar.showMessage('Ready')
            self.loadWorker = None

    def run_start(self):
        victim_name = self.victimComboBox.currentText()
        victim_band = self.victimBandComboBox.currentText()
        aggressor_name = self.aggressorComboBox.currentText()
        aggressor_band = self.aggressorBandComboBox.currentText()

        if victim_band == 'All':
            victim_band = None

        if aggressor_band == 'All':
            aggressor_band = None

        if victim_name != aggressor_name:
            combo_count = self.resultManager.count_combos(aggressor_name, victim_name, aggressor_band, victim_band)
            print(f'Generating data for \'{victim_name}\':\'{victim_band}\' vs \'{aggressor_name}:\'{aggressor_band}, '
                  f'{combo_count} combos')

            self.runButton.setEnabled(False)

            self.runProgressBar.setValue(0)
            self.runProgressBar.setRange(0, combo_count)
            self.runProgressBar.show()

            self.statusBar.showMessage(f'Running {combo_count} combos...')

            self.runWorker = RunWorker(self.resultManager, aggressor_name, victim_name, aggressor_band, victim_band)
            self.runWorker.progress.connect(self.runProgressBar.setValue)
            self.runWorker.finished.connect(self.run_complete)
            self.runWorker.start()

    def run_complete(self):
        self.runButton.setEnabled(True)

        self.runProgressBar.hide()

        self.statusBar.showMessage('Ready')

        if self.runWorker:
            self.results = self.runWorker.results
            self.runWorker = None
            self.set_actions_enabled(True)

    def generate(self):
        victim_name = self.victimComboBox.currentText()
        victim_band = self.victimBandComboBox.currentText()
        aggressor_name = self.aggressorComboBox.currentText()
        aggressor_band = self.aggressorBandComboBox.currentText()

        if victim_band == 'All':
            victim_band = None

        if aggressor_band == 'All':
            aggressor_band = None

        if victim_name != aggressor_name:
            aggressor_frequencies = self.resultManager.revision.get_active_frequencies(aggressor_name, aggressor_band,
                                                                                       TxRxMode.TX)
            victim_frequencies = self.resultManager.revision.get_active_frequencies(victim_name, victim_band,
                                                                                    TxRxMode.RX)
            emi, rx_power, desense, sensitivity = get_results(self.results)

            project_path = self.projectFilePath
            project_dir = os.path.dirname(project_path)
            pivot_table_path = os.path.normpath(os.path.join(project_dir, 'pivot_table.csv'))
            size = export_csv(pivot_table_path, emi, rx_power, desense, sensitivity,
                              aggressor_name, aggressor_band, aggressor_frequencies,
                              victim_name, victim_band, victim_frequencies)

            message_time = 5*1000
            self.statusBar.showMessage(f'Wrote {size} bytes to \'pivot_table.csv\'.', message_time)
            QTimer.singleShot(message_time, lambda: self.statusBar.showMessage('Ready'))

    def waterfall(self):
        victim_name = self.victimComboBox.currentText()
        victim_band = self.victimBandComboBox.currentText()
        aggressor_name = self.aggressorComboBox.currentText()
        aggressor_band = self.aggressorBandComboBox.currentText()

        if victim_band == 'All':
            victim_band = None

        if aggressor_band == 'All':
            aggressor_band = None

        if victim_name != aggressor_name:
            emi, _, _, _ = get_results(self.results)
            data = np.array(np.transpose(emi))

            aggressor_frequencies = self.resultManager.revision.get_active_frequencies(aggressor_name,
                                                                                       aggressor_band, TxRxMode.TX)
            victim_frequencies = self.resultManager.revision.get_active_frequencies(victim_name,
                                                                                    victim_band, TxRxMode.RX)

            title = f'EMI Waterfall {os.path.splitext(os.path.basename(self.projectFilePath))[0]}'
            waterfall.plot_matrix_heatmap(data, xticks=aggressor_frequencies, yticks=victim_frequencies,
                                          xlabel="Tx Channel", ylabel="Rx Channel",
                                          title=title)
            plt.show()


def main():
    app = QApplication(sys.argv)

    form = Form()
    form.resize(300, 300)
    form.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
