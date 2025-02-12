import os
import time
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pyaedt
from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType

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

print(f'{victim}')
print(f'{victim_band}')
print(f'{victim_frequencies}')

print(f'{aggressor}')
print(f'{aggressor_band}')
print(f'{aggressor_frequencies}')

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
    waterfall_emi = np.zeros((num_elements_victim_frequencies, num_elements_aggressor_frequencies))
    num_elements = waterfall_emi.size
    print(num_elements)

index_aggressor = -1

for aggressor_frequency in aggressor_frequencies:
    domain.set_interferer(aggressor, aggressor_band, aggressor_frequency)
    index_aggressor = index_aggressor + 1
    index_victim = 0  # reset victim index for each new aggressor index
    for victim_frequency in victim_frequencies:
        print(f'aggressor_frequency = {aggressor_frequency} victim_frequency = {victim_frequency}')
        print(index_aggressor)
        domain.set_receiver(victim, victim_band, victim_frequency)

        instance = interaction.get_instance(domain)

        if instance.has_valid_values():
            emi = instance.get_value(ResultType.EMI)  # dB
            waterfall_emi[index_victim,index_aggressor] = instance.get_value(
                ResultType.EMI)  # build the data array for future plotting

            index_victim = index_victim + 1
            print(index_victim)
        else:
            warning = instance.get_result_warning()
            print(f'No valid values: {warning}')


    def plot_matrix_heatmap(data, min_val=None, max_val=None, title="Matrix Heatmap",
                            cmap='rainbow', show_values=True, figsize=(10, 8)):
        """
        Create a 2D heatmap visualization of a matrix using a rainbow color scale.

        Parameters:
        -----------
        data : numpy.ndarray
            2D array to visualize
        min_val : float, optional
            Minimum value for color scaling. If None, uses data minimum
        max_val : float, optional
            Maximum value for color scaling. If None, uses data maximum
        title : str, optional
            Title for the plot
        cmap : str, optional
            Colormap to use (default: 'rainbow')
        show_values : bool, optional
            Whether to show numerical values in each cell
        figsize : tuple, optional
            Figure size in inches (width, height)
        """

        # Create figure and axis
        plt.figure(figsize=figsize)

        # If min_val and max_val aren't provided, use data bounds
        if min_val is None:
            min_val = np.min(data)
        if max_val is None:
            max_val = np.max(data)

        # Create the heatmap
        im = plt.imshow(data, cmap=cmap, vmin=min_val, vmax=max_val)

        # Add colorbar
        plt.colorbar(im, label='Values')

        # Add title and labels
        plt.title(title)
        plt.xlabel('Column Index')
        plt.ylabel('Row Index')

        # Show numerical values in each cell if requested
        if show_values:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    text_color = 'white' if im.norm(data[i, j]) > 0.5 else 'black'
                    plt.text(j, i, f'{data[i, j]:.1f}',
                             ha='center', va='center', color=text_color)

        # Adjust layout to prevent cutting off labels
        plt.tight_layout()

        return plt.gcf()


    # Example usage:
    if __name__ == "__main__":




    #can't map wartfall_emi into sample_data, so hardwiring for now...
        R, T = 29, 10
        min_val, max_val = -8, 8
        np.random.seed(42)  # For reproducibility
        sample_data = np.random.uniform(min_val, max_val, size=(R, T))

        # Create visualization
        plot_matrix_heatmap(sample_data,
                            min_val=min_val,
                            max_val=max_val,
                            title="Sample Matrix Visualization")
        plt.show()