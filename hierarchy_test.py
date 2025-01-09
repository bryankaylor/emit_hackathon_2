import tx_rx_response
from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType

# stub test code for stitching functions together
# Ideally, the inputs come from a GUI or some other I/O external to the code
#
project = r'D:\Designs\Electronics_Desktop_2025\EMIT\AH-64 Apache Cosite.aedt'

aggressors, victims, domain, revision = tx_rx_response.get_radios(project,"2025.1")

# Aggressor, Victim and their selected bands are hard coded here. Passed in later
aggressor = aggressors[1]
victim    = victims[0]

victim_bands = revision.get_band_names(victim, TxRxMode.RX)
aggressor_bands = revision.get_band_names(aggressor, TxRxMode.TX)

aggressor_band = aggressor_bands[0]
victim_band    = victim_bands[0]
emi, rx_power, desense, sensitivity = tx_rx_response.tx_rx_response(aggressor, victim, aggressor_band, victim_band, domain, revision)

file = 'D:\Designs\Electronics_Desktop_2025\EMIT\Apache.csv'
#export_csv(file, emi, rx_power, desense, sensitivity, aggressor, victim, aggressor_band, victim_band)
#plot(emi, rx_power, desense, sensitivity, aggressor_band, victim_band)

pass