from sr620 import *
from sr620 import SR620

device = SR620('/dev/ttyUSB1','logfile.log')
device.set_custom_configuration(
    mode = MODE_FREQUENCY,
    source = SOURCE_A,
    arming = ARMING_SECOND,
    size = 1,
    print = True
)
val = device.measure(STATISTICS_MEAN)
print(val)
vals = device.start_measurement_set(STATISTICS_MEAN,5,progress=True)
print(vals)
device.close_connection()