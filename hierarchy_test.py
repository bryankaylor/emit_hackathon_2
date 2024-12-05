import tx_rx_response

# stub test code for stitching functions together
# Ideally, the inputs come from a GUI or some other I/O external to the code
#
project = r'D:\Designs\Electronics_Desktop_2025\EMIT\AH-64 Apache Cosite.aedt'

aggressors, victims, domain, revision = tx_rx_response.get_radios(project,"2025.1")

aggressor = aggressors[1]
victim    = victims[0]

emi, rx_power, desense, sensitivity = tx_rx_response.tx_rx_response(aggressor, victim, domain, revision)


pass