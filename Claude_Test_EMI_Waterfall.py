import os
import time
import matplotlib.pyplot as plt
import numpy as np
import pyaedt

from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType

from tx_rx_response import tx_rx_response

timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"


def get_data():
    project = r'C:\Program Files\ANSYS Inc\v252\AnsysEM\Examples\EMIT\AH-64 Apache Cosite.aedt'
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

    print(f'{victim}:{victim_band}, {aggressor}:{aggressor_band}')

    emi, rx_power, desense, sensitivity = tx_rx_response(aggressor, victim, aggressor_band, victim_band, domain, revision)
    return emi


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
    data = get_data()
    data = np.array(np.transpose(data))

    # Create visualization
    plot_matrix_heatmap(data, title="Sample Matrix Visualization")
    plt.show()
