# ===========================================================================
# Description:
#   This python library will extract EMIT response like EMI, Rx_Power,
#   Sensitivity and Desense. The first function will extract this data
#   for all channel combinations between a single Transmit and Receive band.
#
# Authors: Bryan Kaylor, Jason Bommer, Eldon Staggs
#
# Revision History:
#   12/05/2024[Eldon]: Initial creation of EMI extraction for band to band interaction
#
# ===========================================================================
import os
import time
from dataclasses import dataclass
from collections import defaultdict

import ansys.aedt.core as pyaedt
from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType

from PySide6.QtCore import QThread, Signal


timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"


@dataclass
class Combination:
    emi: float
    rx_power: float
    desense: float
    sensitivity: float


class Band:
    def __init__(self, name, radio, result_manager):
        self.name = name
        self.radio = radio
        self.result_manager = result_manager
        self.frequencies = self.result_manager.revision.get_active_frequencies(radio.name, self.name, radio.type)


class Radio:
    def __init__(self, name, mode, result_manager):
        self.name = name
        self.type = mode
        self.result_manager = result_manager
        self.bands = [Band(band, self, self.result_manager)
                      for band in self.result_manager.revision.get_band_names(name, mode)]


def get_results(combos):
    aggressor = list(combos.keys())[0]
    victim = list(combos[aggressor].keys())[0]
    aggressor_band = list(combos[aggressor][victim].keys())[0]
    victim_band = list(combos[aggressor][victim][aggressor_band].keys())[0]

    aggressor_frequencies = list(combos[aggressor][victim][aggressor_band][victim_band].keys())

    combos_2d = []
    for af in aggressor_frequencies:
        combo_row = []
        victim_frequencies = list(combos[aggressor][victim][aggressor_band][victim_band][af].keys())
        for vf in victim_frequencies:
            combo = combos[aggressor][victim][aggressor_band][victim_band][af][vf]
            combo_row.append(combo)
        combos_2d.append(combo_row)

    emi = []
    rx_power = []
    desense = []
    sensitivity = []

    for x in range(len(combos_2d)):
        combo_row = combos_2d[x]
        emi_row = []
        rx_power_row = []
        desense_row = []
        sensitivity_row = []
        for y in range(len(combo_row)):
            combo = combo_row[y]
            emi_row.append(combo.emi)
            rx_power_row.append(combo.rx_power)
            desense_row.append(combo.desense)
            sensitivity_row.append(combo.sensitivity)
        emi.append(emi_row)
        rx_power.append(rx_power_row)
        desense.append(desense_row)
        sensitivity.append(sensitivity_row)

    return emi, rx_power, desense, sensitivity


class RunWorker(QThread):
    progress = Signal(int)
    finished = Signal()

    def __init__(self, result_manager, aggressor_name, victim_name, aggressor_band, victim_band):
        super().__init__()

        self.resultManager = result_manager
        self.aggressorName = aggressor_name
        self.victimName = victim_name
        self.aggressorBand = aggressor_band
        self.victimBand = victim_band

        self.results = None

    def run(self):
        aggressors = [agg for agg in self.resultManager.aggressors if agg.name == self.aggressorName] if \
            self.aggressorName else self.resultManager.aggressors
        victims = [vic for vic in self.resultManager.victims if vic.name == self.victimName] if \
            self.victimName else self.resultManager.victims

        results = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(Combination))))))

        domain = self.resultManager.emitApp.results.interaction_domain()

        interaction = self.resultManager.revision.run(domain)
        with self.resultManager.revision.get_license_session():
            combos = 0
            for aggressor in aggressors:
                for victim in victims:
                    if aggressor.name == victim.name:
                        continue

                    aggressor_bands = [ab for ab in aggressor.bands if
                                       ab.name == self.aggressorBand] if self.aggressorBand else \
                        aggressor.bands
                    victim_bands = [vb for vb in victim.bands if vb.name == self.victimBand] if self.victimBand else \
                        victim.bands

                    for ab in aggressor_bands:
                        domain.set_interferer(aggressor.name, ab.name)
                        for vb in victim_bands:
                            domain.set_receiver(victim.name, vb.name)
                            for af in ab.frequencies:
                                domain.set_interferer(aggressor.name, ab.name, af)
                                for vf in vb.frequencies:
                                    domain.set_receiver(victim.name, vb.name, vf)

                                    try:
                                        instance = interaction.get_instance(domain)
                                    except Exception as e:
                                        print(f'Error: {e}')
                                        continue

                                    if instance.has_valid_values():
                                        emi = instance.get_value(ResultType.EMI)
                                        rx_power = instance.get_value(ResultType.POWER_AT_RX)
                                        desense = instance.get_value(ResultType.DESENSE)
                                        sensitivity = instance.get_value(ResultType.SENSITIVITY)

                                        combo = Combination(emi, rx_power, desense, sensitivity)
                                        results[aggressor.name][victim.name][ab.name][vb.name][af][vf] = combo
                                    else:
                                        warning = instance.get_result_warning()
                                        print(f'No valid values: {warning}')

                                    self.progress.emit(combos)
                                    combos += 1
        self.results = results
        self.finished.emit()


class LoadAEDTWorker(QThread):
    finished = Signal()

    def __init__(self, project, version='2025.1'):
        super().__init__()

        self.project = project
        self.version = version

        self.emitApp = None

    def run(self):
        self.emitApp = pyaedt.Emit(project=self.project, version=self.version, new_desktop=True, remove_lock=True)
        self.finished.emit()


class ResultManager:
    def __init__(self, emit_app):
        self.emitApp = emit_app
        self.revision = self.emitApp.results.analyze()
        self.aggressors = [Radio(name, TxRxMode.TX, self) for name in self.revision.get_interferer_names()]
        self.victims = [Radio(name, TxRxMode.RX, self) for name in self.revision.get_receiver_names()]

    def print_radio_data(self):
        result = ''
        for aggressor in self.aggressors:
            result += f'{aggressor.name}\n'
            for band in aggressor.bands:
                result += f' {band.name}\n'
                for channel in band.frequencies:
                    result += f'  {channel}\n'
        for victim in self.victims:
            result += f'{victim.name}\n'
            for band in victim.bands:
                result += f' {band.name}\n'
                for channel in band.frequencies:
                    result += f'  {channel}\n'
        print(result)

    def count_combos(self, aggressor=None, victim=None, aggressor_band=None, victim_band=None):
        aggressors = [agg for agg in self.aggressors if agg.name == aggressor] if aggressor else self.aggressors
        victims = [vic for vic in self.victims if vic.name == victim] if victim else self.victims

        combos = 0
        for aggressor in aggressors:
            for victim in victims:
                if aggressor.name == victim.name:
                    continue

                aggressor_bands = [ab for ab in aggressor.bands if ab.name == aggressor_band] if aggressor_band else \
                    aggressor.bands
                victim_bands = [vb for vb in victim.bands if vb.name == victim_band] if victim_band else \
                    victim.bands

                for ab in aggressor_bands:
                    for vb in victim_bands:
                        for _ in ab.frequencies:
                            for _ in vb.frequencies:
                                combos += 1
        return combos

    def get_combos(self, aggressor=None, victim=None, aggressor_band=None, victim_band=None):
        aggressors = [agg for agg in self.aggressors if agg.name == aggressor] if aggressor else self.aggressors
        victims = [vic for vic in self.victims if vic.name == victim] if victim else self.victims

        results = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(Combination))))))

        domain = self.emitApp.results.interaction_domain()

        interaction = self.revision.run(domain)
        with self.revision.get_license_session():
            for aggressor in aggressors:
                for victim in victims:
                    if aggressor.name == victim.name:
                        continue

                    aggressor_bands = [ab for ab in aggressor.bands if ab.name == aggressor_band] if \
                        aggressor_band else aggressor.bands

                    victim_bands = [vb for vb in victim.bands if vb.name == victim_band] if \
                        victim_band else victim.bands

                    for ab in aggressor_bands:
                        domain.set_interferer(aggressor.name, ab.name)
                        for vb in victim_bands:
                            domain.set_receiver(victim.name, vb.name)
                            for af in ab.frequencies:
                                domain.set_interferer(aggressor.name, ab.name, af)
                                for vf in vb.frequencies:
                                    domain.set_receiver(victim.name, vb.name, vf)

                                    try:
                                        instance = interaction.get_instance(domain)
                                    except Exception as e:
                                        print(f'Error: {e}')
                                        continue

                                    if instance.has_valid_values():
                                        emi = instance.get_value(ResultType.EMI)
                                        rx_power = instance.get_value(ResultType.POWER_AT_RX)
                                        desense = instance.get_value(ResultType.DESENSE)
                                        sensitivity = instance.get_value(ResultType.SENSITIVITY)

                                        combo = Combination(emi, rx_power, desense, sensitivity)
                                        results[aggressor.name][victim.name][ab.name][vb.name][af][vf] = combo
                                    else:
                                        warning = instance.get_result_warning()
                                        print(f'No valid values: {warning}')
        return results
