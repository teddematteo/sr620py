"""
Library to control and take measure from a SR620 Universal Time Interval Counter

@requires: pyserial, time
"""
from sr620utils import *
from sr620exceptions import *
import serial
import time

class SR620():
    """Class describing the SR620 device. From this instance all the functions can be called"""

    def __init__(self,serial_port_path:str):
        self.ser = serial.Serial(serial_port_path,9600,timeout=None)

    def execute_command(self,ser:serial.Serial,command:str,needs_response:bool):
        ser.write(f"{command}\r".encode('ASCII'))
        time.sleep(0.01)
        if needs_response: #if a response is needed
            try:
                response = ser.read_until("\r\n".encode('ASCII')).decode('utf-8')
                return parse_string_to_dict(response)
            except Exception:
                raise SR620ReadException("An error occurs while reading from the device",errors={"value":1})

