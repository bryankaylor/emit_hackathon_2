
def export_csv(csv_file, emi, rx_power, desense, sensitivity,
               aggressor, aggressor_band, aggressor_frequencies,
               victim, victim_band, victim_frequencies):

    pivot_results = "Aggressor_Radio,Aggressor_Band,Aggressor_Channel," \
                    "Victim_Radio,Victim_Band,Victim_Channel," \
                    "EMI,RX_Power,Desense,Sensitivity\n"

    for ai, aggressor_frequency in enumerate(aggressor_frequencies):
        for vi, victim_frequency in enumerate(victim_frequencies):
            pivot_results += f'{aggressor},{aggressor_band},{aggressor_frequency},' \
                             f'{victim},{victim_band},{victim_frequency},' \
                             f'{emi[ai][vi]},{rx_power[ai][vi]},{desense[ai][vi]},{sensitivity[ai][vi]}\n'

    print(pivot_results)
    with open(csv_file, 'w') as file:
        file.write(pivot_results)
