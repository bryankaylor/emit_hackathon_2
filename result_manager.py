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


class ResultManager:
    def __init__(self, project, version='2025.1'):
        self.emit_app = pyaedt.Emit(project=project, version='2025.1', new_desktop=True, remove_lock=True)
        self.revision = self.emit_app.results.analyze()
        self.domain = self.emit_app.results.interaction_domain()

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
        victims = [vic for vic in self.aggressors if vic.name == victim] if victim else self.victims

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
                        for aggressor_frequency in ab.frequencies:
                            for victim_frequency in vb.frequencies:
                                combos += 1
        return combos

    def get_combos(self, aggressor=None, victim=None, aggressor_band=None, victim_band=None):
        aggressors = [agg for agg in self.aggressors if agg.name == aggressor] if aggressor else self.aggressors
        victims = [vic for vic in self.aggressors if vic.name == victim] if victim else self.victims

        results = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(
                        lambda: defaultdict(
                            lambda: defaultdict(Combination))))))

        interaction = self.revision.run(self.domain)
        with self.revision.get_license_session():
            for aggressor in aggressors:
                for victim in victims:
                    if aggressor.name == victim.name:
                        continue

                    aggressor_bands = [ab for ab in aggressor.bands if ab.name == aggressor_band] if aggressor_band else \
                        aggressor.bands
                    victim_bands = [vb for vb in victim.bands if vb.name == victim_band] if victim_band else \
                        victim.bands

                    for ab in aggressor_bands:
                        self.domain.set_interferer(aggressor.name, ab.name)
                        for vb in victim_bands:
                            self.domain.set_receiver(victim.name, vb.name)
                            for af in ab.frequencies:
                                self.domain.set_interferer(aggressor.name, ab.name, af)
                                for vf in vb.frequencies:
                                    self.domain.set_receiver(victim.name, vb.name, vf)

                                    try:
                                        instance = interaction.get_instance(self.domain)
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
