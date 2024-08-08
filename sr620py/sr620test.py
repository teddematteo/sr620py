from sr620 import *
from sr620 import SR620

device = SR620('/dev/ttyUSB1','logfile.log')
# device.set_custom_configuration(
#     mode = MODE_TIME,
#     arming = ARMING_SECOND,
#     size = 1,
#     print = True
# )
print(device)
device.start_measurement_set_forever(STATISTICS_MEAN,progress=True,file_path='results.csv')
device.close_connection()