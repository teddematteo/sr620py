from sr620 import *


device = SR620('/dev/ttyUSB1')
device.set_custom_configuration(
    mode='freq',
    source='A',
    jitter='ALL',
    arming='1s',
    size=5,
    clock='ext',
    clockfr='10mhz'
)
print(device.measure('mean'))
device.close_connection()