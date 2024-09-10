from sr620 import *
from sr620 import SR620

device = SR620('/dev/ttyUSB0')
device.set_custom_configuration(
    mode = MODE_FREQUENCY,
    arming = ARMING_SECOND,
    size = 100,
    clock=CLOCK_INTERNAL,
    print = True
)
dct = device.start_measurement_allan_variance(num_powers=6,progress=True)
print(dct)
device.close_connection()