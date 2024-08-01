"""
Library to control and take measure from a SR620 Universal Time Interval Counter

@requires: pyserial, time, tqdm, threading
"""
from sr620utils import *
from sr620exceptions import *
import serial
import time
from datetime import datetime
from zoneinfo import ZoneInfo

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
    ARMM_TIME = {'1cs':0.01,'1ds':0.1,'1s':1,'ext1cs':0.01,'ext1ds':0.1,'ext1s':1}
    DELAY_CONF = 1

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
        cmm = f"SRCE {self.SOURCE_DICT[self.source]}; MODE {self.MODE_DICT[self.mode]}; ARMM {self.ARMM_DICT[self.armm]}; SIZE {self.size}; JTTR {self.JTTR_DICT[self.jttr]}; CLCK {self.CLCK_DICT[self.clock]}; CLKF {self.CLKF_DICT[self.clockfr]}"
        return cmm

    def apply_custom_configuration(self,*,print=True):
        gcs = self.generate_configuration_string()
        self.execute_command(gcs,False)
        if print: print('Setting parameters...')
        time.sleep(self.DELAY_CONF)
        self.retrieve_parameters()

    def set_custom_configuration(self,*,mode=None,source=None,jitter=None,arming=None,size=None,clock=None,clockfr=None,print=False):
        if mode!=None: self.mode = mode
        if source!=None: self.source = source
        if jitter!=None: self.jttr = jitter
        if arming!=None: self.armm = arming
        if clock!=None: self.clock = clock
        if clockfr!=None: self.clockfr = clockfr
        if size!=None: 
            if (size not in self.SIZE_LIST):
                raise SR620SizeException(self.SIZE_LIST)
            else:
                self.size = size
        self.apply_custom_configuration(print=print)
            
    def set_mode(self,mode:str,*,print=False):
        self.set_custom_configuration(mode=mode,print=print)

    def set_source(self,source:str,*,print=False):
        self.set_custom_configuration(source=source,print=print)

    def set_jitter_type(self,jitter:str,*,print=False):
        self.set_custom_configuration(jitter=jitter,print=print)

    def set_arming(self,arming:str,*,print=False):
        self.set_custom_configuration(arming=arming,print=print)

    def set_number_samples(self,size:int,*,print=False):
        self.set_custom_configuration(size=size,print=print)

    def set_clock(self,clock:str,*,print=False):
        self.set_custom_configuration(clock=clock,print=print)

    def set_clock_frequency(self,clockfr:str,*,print=False):
        self.set_custom_configuration(clockfr=clockfr,print=print)

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

    def __str__(self):
        return f"-------------------------------------\n***SR620 parameters configuration***\nMode: {self.mode}\nSource: {self.source}\nArming: {self.armm}\nNumOfSamples: {self.size}\nTypeOfJitter: {self.jttr}\nClock: {self.clock}\nClockFrequency: {self.clockfr}\n-------------------------------------"
    
    def measure(self,stat:str,*,progress=True) -> float:
        self.ser.flush()
        thread = None
        if (progress and self.armm in self.ARMM_TIME.keys() and self.mode=='freq'):        
            thread = start_progress(int(self.size),self.ARMM_TIME[self.armm])
        res = self.execute_command(f'STOP; AUTM 0; MEAS? {self.STAT_DICT[stat]}',True)
        if (thread!=None):
            thread.join()
        return float(res['value_0'])
    
    def start_measurement_set(self,stat:str,num_meas:int,*,file_path=None,progress=False):
        print('Measurement set started...')
        fout = None
        if file_path!=None:
            fout = open(file_path,'w')
            fout.write(f'timestamp,{stat}\n')
            fout.flush()
        for i in range(num_meas):
            res = self.measure(stat,progress=progress)
            rec = f"{datetime.now(ZoneInfo('Europe/Rome')).strftime('%Y-%m-%d_%H-%M-%S')},{res}"
            print(rec)
            if fout!=None:
                fout.write(rec+'\n')
                fout.flush()
        if fout!=None: fout.close()
        print(f'Measurement set concluded, file saved in {file_path}')

    def start_measurement_allan_variance(self,num_powers:int,*,file_path=None,progress=True):
        """Only powers of 10"""
        thread = None
        if (progress):        
            thread = start_progress(tot_allan_time(num_powers),self.ARMM_TIME[self.armm])
        self.set_custom_configuration(
            mode='freq',
            jitter='ALL',
            print=False
        )
        fout = None
        if file_path!=None:
            fout = open(file_path,'w')
            fout.write(f'number of observations,allan variance\n')
            fout.flush()
        for i in range(1,num_powers+1):
            self.set_number_samples(int(float(f'1e{i}')),print=False)
            res = self.measure('jitter',progress=False)
            rec = f"1e{i},{res}"
            if fout!=None:
                fout.write(rec+'\n')
                fout.flush()
        if fout!=None: fout.close()
        print(f'File saved in {file_path}')