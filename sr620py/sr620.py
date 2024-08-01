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

    MODE_DICT = {'time':0,'width':1,'ratio':2,'freq':3,'period':4,'phase':5,'count':6}
    SOURCE_DICT = {'A':0,'B':1,'REF':2,'RATIO':3}
    JTTR_DICT = {'STD':0,'ALL':1}

    def __init__(self,serial_port_path:str):
        self.ser = serial.Serial(serial_port_path,9600,timeout=None)
        self.execute_command(self.ser,"ENDT; STOP",False)
        self.mode = self.MODE_DICT['freq']
        self.source = self.SOURCE_DICT['A']
        self.jttr = self.JTTR_DICT['ALL']
        
        


    def execute_command(self,ser:serial.Serial,command:str,needs_response:bool):
        try:
            ser.write(f"{command}\r".encode('ASCII'))
        except Exception:
            raise SR620WriteException("An error occurs while writing on the device",errors={"value":1})

        if needs_response: #if a response is needed
            try:
                response = ser.read_until("\r\n".encode('ASCII')).decode('utf-8')
                return parse_string_to_dict(response)
            except Exception:
                raise SR620ReadException("An error occurs while reading from the device",errors={"value":1})
            
    def get_configuration():
        print('ciao')

    def set_configuration(self,mode=3,source=0,jttr=1):
        print('ciao')
            
    def start_measurement():
        print('ciao')

