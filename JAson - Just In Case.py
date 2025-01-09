
import os
import time
import matplotlib.pyplot as plt
import numpy as np
import pyaedt
from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType

timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"


def main():

    project = r'D:\OneDrive - ANSYS, Inc\Documents\GitHub\AH-64 Apache Cosite.aedt'
    desktop = pyaedt.Desktop(specified_version="2025.1", new_desktop=True)


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
    with revision.get_license_session():

        text_results = ""
        pivot_results = "Agressor_Radio,Aggressor_Band,Agg_Channel,Victim_Radio,Victim_Band,Vic_Channel,EMI,RX_Power,Desense,Sensitivity \n"

        num_elements_aggressor_frequencies = len(aggressor_frequencies)
        print(num_elements_aggressor_frequencies)
        num_elements_victim_frequencies = len(victim_frequencies)
        print(num_elements_victim_frequencies)
        waterfall_emi = np.zeros((num_elements_aggressor_frequencies,num_elements_victim_frequencies))
        num_elements = waterfall_emi.size
        print(num_elements)

        index_aggressor = -1

        for aggressor_frequency in aggressor_frequencies:
            domain.set_interferer(aggressor, aggressor_band, aggressor_frequency)
            index_aggressor = index_aggressor + 1
            index_victim = -1   #reset victim index for each new aggressor index
            for victim_frequency in victim_frequencies:
                print(f'aggressor_frequency = {aggressor_frequency} victim_frequency = {victim_frequency}')
                print(index_aggressor)
                domain.set_receiver(victim, victim_band, victim_frequency)

                instance = interaction.get_instance(domain)

                if instance.has_valid_values():
                    emi = instance.get_value(ResultType.EMI) # dB
                    waterfall_emi[index_aggressor,index_victim] = instance.get_value(ResultType.EMI) #build the data array for future plotting

                    index_victim = index_victim + 1
                    print(index_victim)
                    power_at_rx = instance.get_value(ResultType.POWER_AT_RX) # dBM
                    desense = instance.get_value(ResultType.DESENSE)
                    sensitivity = instance.get_value(ResultType.SENSITIVITY)
                    text_result = f'({victim_frequency}, {aggressor_frequency}) = ({emi}, {power_at_rx})\n'
                    text_results += text_result
                    pivot_results += f'{aggressor},{aggressor_band},{aggressor_frequency},{victim},{victim_band},{victim_frequency},{emi},{power_at_rx},{desense},{sensitivity}\n'
                else:
                    warning = instance.get_result_warning()
                    print(f'No valid values: {warning}')

        #from Claude. Plot emi_waterfall

        # Assuming your data is in a 2D numpy array called 'waterfall_emi'
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(waterfall_emi, cmap='YlOrRd', vmin=-10, vmax=10)
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.set_title('2D Color Plot')
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Magnitude')
        # Set the ticks and tick labels
        ax.set_xticks(np.arange(waterfall_emi.shape[1]))
        ax.set_yticks(np.arange(waterfall_emi.shape[0]))
        #ax.set_xticklabels(['Ach1', 'Ach2', 'Ach3', 'Ach4', 'Ach5', 'Ach6', 'Ach7', '10kN', '20kN', '50kN', '100kN', 'Bottom-x', 'Bottom-y'])
        #ax.set_yticklabels(['HF_1_-Top', 'HF_2_-Bottom', 'HF_-Bottom', 'FF_-Upper', 'FF_-Lower', 'Radar Warning Rx', 'GPS'])

        # Rotate the x-axis tick labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

        # Adjust the spacing between subplots
        plt.subplots_adjust(bottom=0.15, right=0.85)

        plt.show()

    print(text_results)
    print(waterfall_emi)
    with open("data.txt", 'w') as file:
        file.write(text_results)
    with open("pivot_table.csv", 'w') as file:
        file.write(pivot_results)
    pass


if __name__ == "__main__":
    main()
