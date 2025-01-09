def export_csv(file, emi, rx_power, desense, sensitivity, aggressor, victim, aggressor_band, victim_band):

    victim_frequencies = revision.get_active_frequencies(victim, victim_bands[0], TxRxMode.RX)
    aggressor_frequencies = revision.get_active_frequencies(aggressor, aggressor_bands[0], TxRxMode.TX)

    for aggressor_frequency in aggressor_frequencies:

        emi_line=[]
        rx_power_line=[]
        desense_line=[]
        sensitivity_line=[]
        domain.set_interferer(aggressor, aggressor_band, aggressor_frequency)

        for victim_frequency in victim_frequencies:

            #print(f'aggressor_frequency = {aggressor_frequency} victim_frequency = {victim_frequency}')
            domain.set_receiver(victim, victim_band, victim_frequency)

            instance = interaction.get_instance(domain)

            if instance.has_valid_values():
                emi_line.append(instance.get_value(ResultType.EMI))  # dB
                rx_power_line.append(instance.get_value(ResultType.POWER_AT_RX)) # dBM
                desense_line.append(instance.get_value(ResultType.DESENSE))
                sensitivity_line.append(instance.get_value(ResultType.SENSITIVITY))
            else:
                warning = instance.get_result_warning()
                print(f'No valid values: {warning}')

        emi.append(emi_line)
        rx_power.append(rx_power_line)
        desense.append(desense_line)
        sensitivity.append(sensitivity_line)

return emi, rx_power, desense, sensitivity
