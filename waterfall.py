import os
import time
import matplotlib.pyplot as plt
import numpy as np

from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType

from result_manager import ResultManager, get_results

timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"


def get_data():
    project = r'D:/OneDrive - ANSYS, Inc/Documents/GitHub/AH-64 Apache Cosite.aedt'
    result_manager = ResultManager(project)

    victims = result_manager.revision.get_receiver_names()
    aggressors = result_manager.revision.get_interferer_names()

    victim = victims[0]
    aggressor = aggressors[1]

    victim_bands = result_manager.revision.get_band_names(victim, TxRxMode.RX)
    aggressor_bands = result_manager.revision.get_band_names(aggressor, TxRxMode.TX)

    victim_band = victim_bands[0]
    aggressor_band = aggressor_bands[0]

    print(f'{victim}:{victim_band}, {aggressor}:{aggressor_band}')
    combos = result_manager.get_combos(aggressor, victim, aggressor_band, victim_band)
    emi, _, _, _ = get_results(combos)
    return emi


def plot_matrix_heatmap(data, min_val=None, max_val=None,
                        xlabel="Column index", ylabel="Row index",
                        xticks=None, yticks=None, title="Matrix Heatmap",
                        cmap='rainbow', show_values=True, figsize=(10, 8)):
    # Create figure and axis
    plt.figure(figsize=figsize)

    # If min_val and max_val aren't provided, use data bounds
    if min_val is None:
        min_val = np.min(data)
    if max_val is None:
        max_val = np.max(data)

    # Create the heatmap
    im = plt.imshow(data, cmap=cmap, vmin=min_val, vmax=max_val) #extent=[xticks[0],xticks[-1],yticks[0],yticks[-1]])

    # Add colorbar
    plt.colorbar(im, label='Values')

    # Add title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(range(len(xticks)), xticks)
    plt.yticks(range(len(yticks)), yticks)
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
    data = get_data()
    data = np.array(np.transpose(data))

    # Create visualization
    plot_matrix_heatmap(data, title="EMI Waterfall")
    plt.show()
