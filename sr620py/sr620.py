"""
Library to control and take measure from a SR620 Universal Time Interval Counter

@requires: pyserial, time, tqdm, threading
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
    ARMM_DICT = {'+-time':0,'+time':1,'1per':2,'1cs':3,'1ds':4,'1s':5,'ext+-time':6,'ext+time':7,'extgate':8,'ext1per':9,'ext1cs':10,'ext1ds':11,'ext1s':12}
    CLCK_DICT = {'int':0,'ext':1}
    SIZE_LIST = [1,2,5,1e1,2e1,5e1,1e2,2e2,5e2,1e3,2e3,5e3,1e4,2e4,5e4,1e5,2e5,5e5,1e6,2e6,5e6]
    CLKF_DICT = {'10mhz':0,'5mhz':1}
    STAT_DICT = {'mean':0,'jitter':1,'max':2,'min':3}
    ARMM_TIME = {3:0.01,4:0.1,5:1,10:0.01,11:0.1,12:1}

    def __init__(self,serial_port_path:str):
        self.ser = serial.Serial(serial_port_path,9600,timeout=None)
        self.execute_command("ENDT; STOP",False)
        self.retrieve_parameters()
        
    def close_connection(self):
        self.ser.close()
        
    def execute_command(self,command:str,needs_response:bool):
        try:
            self.ser.write(command.encode('ASCII')+b'\r')
        except Exception:
            print('error occured!')
            raise SR620WriteException("An error occured while writing on the device",errors={"value":1})

        if needs_response: #if a response is needed
            try:
                response = self.ser.read_until("\r\n".encode('ASCII')).decode('utf-8')
                return parse_string_to_dict(response)
            except Exception:
                raise SR620ReadException("An error occurs while reading from the device",errors={"value":1})
            
    def generate_configuration_string(self) -> str:
        cmm = f"SRCE {self.source}; MODE {self.mode}; ARMM {self.armm}; SIZE {self.size}; JTTR {self.jttr}; CLCK {self.clock}; CLKF {self.clockfr}"
        return cmm
            
    def set_default_configuration(self):
        self.set_custom_configuration()

    def set_custom_configuration(self,*,mode='freq',source='A',jitter='ALL',arming='1s',size=1,clock='ext',clockfr='10mhz'):
        self.mode = self.MODE_DICT[mode]
        self.source = self.SOURCE_DICT[source]
        self.jttr = self.JTTR_DICT[jitter]
        self.armm = self.ARMM_DICT[arming]
        self.clock = self.CLCK_DICT[clock]
        self.clockfr = self.CLKF_DICT[clockfr]
        if (size not in self.SIZE_LIST):
            raise SR620SizeException(self.SIZE_LIST)
        else:
            self.size = size
        gcs = self.generate_configuration_string()
        self.execute_command(gcs,False)
        print('Setting parameter...')
        time.sleep(2)
            
    def measure(self,stat:str) -> float:
        self.ser.flush()
        thread = None

        if (self.armm in self.ARMM_TIME.keys() and self.mode==3):          
            thread = start_progress(self.size,self.ARMM_TIME[self.armm])
        res = self.execute_command(f'AUTM 0; STOP; MEAS? {self.STAT_DICT[stat]}',True)
        if (thread!=None):
            thread.join()
        return float(res['value_0'])

    def set_mode(self,mode:str):
        self.mode = self.MODE_DICT[mode]
        self.execute_command(f'MODE {self.mode}',False)
        print('Setting parameter...')
        time.sleep(2)

    def retrieve_parameters(self):
        """Retrieve the parameters set on the machine"""
        res = self.execute_command('STUP?',True)
        x = int(res['value_7'])
        self.mode = get_key_from_value(self.MODE_DICT,int(res['value_0']))
        self.source = get_key_from_value(self.SOURCE_DICT,int(res['value_1']))
        self.armm = get_key_from_value(self.ARMM_DICT,int(res['value_2']))
        self.size = self.SIZE_LIST[int(res['value_4'])]
        self.clock = get_key_from_value(self.CLCK_DICT,get_bit(x,6))
        self.jttr = get_key_from_value(self.JTTR_DICT,get_bit(x,5))
        self.clockfr = get_key_from_value(self.CLKF_DICT,get_bit(x,7))

        print(f"{self.mode},{self.source},{self.armm},{self.size},{self.jttr},{self.clock},{self.clockfr}")
    

