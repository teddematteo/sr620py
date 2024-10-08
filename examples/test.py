from sr620py import *

device = SR620('/dev/ttyUSB0')
device.set_custom_configuration(
    mode=MODE_FREQUENCY,
    source=SOURCE_A,
    jitter=JITTER_ALLAN,
    arming=ARMING_SECOND,
    clock=CLOCK_EXTERNAL,
    print=True
)
device.start_measurement_allan_variance(10,file_path='allan.csv',plot_path='allan.png')
device.close_connection()