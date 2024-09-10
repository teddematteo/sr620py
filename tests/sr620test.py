import sr620py

device = sr620py.SR620('/dev/ttyUSB0')
device.set_custom_configuration(
    mode = sr620py.MODE_FREQUENCY,
    arming = sr620py.ARMING_SECOND,
    size = 100,
    clock= sr620py.CLOCK_INTERNAL,
    print = True
)
dct = device.start_measurement_allan_variance(num_powers=6,progress=True)
print(dct)
device.close_connection()