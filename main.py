
import pyaedt
from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType


def main():
    print("EMIT Hackathon 2 for Jason")
    print("Thanks, Bryan!")

    project = r'C:\Users\bkaylor\Downloads\AH-64 Apache Cosite.aedt'
    desktop = pyaedt.Desktop(specified_version="2025.1", new_desktop=True)
    print(f'{desktop.aedt_process_id}')

    emit = pyaedt.Emit(project=project)
    revision = emit.results.analyze()
    domain = emit.results.interaction_domain()

    victims = revision.get_receiver_names()
    aggressors = revision.get_interferer_names()

    victim = victims[0]
    aggressor = aggressors[1]

    victim_bands = revision.get_band_names(victim, TxRxMode.RX)
    aggressor_bands = revision.get_band_names(aggressor, TxRxMode.TX)

    victim_band = victim_bands[0]
    aggressor_band = aggressor_bands[0]

    victim_frequencies = revision.get_active_frequencies(victim, victim_bands[0], TxRxMode.RX)
    aggressor_frequencies = revision.get_active_frequencies(aggressor, aggressor_bands[0], TxRxMode.TX)

    print(f'{victim} {victim_band} {victim_frequencies}')
    print(f'{aggressor} {aggressor_band} {aggressor_frequencies}')

    domain.set_receiver(victim, victim_band)
    domain.set_interferer(aggressor, aggressor_band)
    interaction = revision.run(domain)

    for aggressor_frequency in aggressor_frequencies:
        domain.set_interferer(aggressor, aggressor_band, aggressor_frequency)
        for victim_frequency in victim_frequencies:
            domain.set_receiver(victim, victim_band, victim_frequency)

            instance = interaction.get_instance(domain)

            if instance.has_valid_values():
                emi = instance.get_value(ResultType.EMI)
                print(f'({victim_frequency}, {aggressor_frequency}) = {emi}')
            else:
                warning = instance.get_result_warning()
                print(f'No valid values: {warning}')

    pass


if __name__ == "__main__":
    main()
