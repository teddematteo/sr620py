"""
Library to control and take measure from a SR620 Universal Time Interval Counter

@requires: pyserial, time, tqdm, threading
"""
from sr620utils import *
from sr620exceptions import *
from datetime import datetime
from zoneinfo import ZoneInfo
import serial
import time

class SR620():
    """Class describing the SR620 device. This class encapsulates all the functions to configure and control the instrument"""

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
        """
        Constructor.
        Parameters:
        :param serial_port_path (str): path of the serial port on which the device is connected (i.e. "/dev/ttyUSB0")
        """
        self.ser = serial.Serial(serial_port_path,9600,timeout=None)
        self.execute_command("ENDT; STOP",False)
        self.retrieve_parameters()
        
    def close_connection(self):
        """
        Close the serial port connection.
        """
        self.ser.close()
        
    def execute_command(self,command:str,needs_response:bool):
        """
        Execute a command on the machine.
        Parameters:
        :param command (str): command that must be executed, according to the format requested by the device ('command(?) param')
        :param needs_response (bool): when an output is expected from the device must be set on True, otherwise on False
        :return (dict): value returned when needs_response is set on True. The format is a dictionary whose keys are progressive strings 'value_i', with the corresponding values (i.e. {'value_0':'10','value_1':'5','value_2':'30'})
        """
        try:
            self.ser.write(command.encode('ASCII')+b'\r')
        except Exception:
            raise SR620WriteException()

        if needs_response: #if a response is needed
            try:
                response = self.ser.read_until("\r\n".encode('ASCII')).decode('utf-8')
                return parse_string_to_dict(response)
            except Exception:
                raise SR620ReadException()
            
    def generate_configuration_string(self) -> str:
        """
        Generate a command string containing the configuration of the device, according to the values set by the user.
        Parameters:
        :return (str): string representing the command
        """
        cmm = f"SRCE {self.SOURCE_DICT[self.source]}; MODE {self.MODE_DICT[self.mode]}; ARMM {self.ARMM_DICT[self.armm]}; SIZE {self.size}; JTTR {self.JTTR_DICT[self.jttr]}; CLCK {self.CLCK_DICT[self.clock]}; CLKF {self.CLKF_DICT[self.clockfr]}"
        return cmm

    def apply_custom_configuration(self,*,print=True):
        """
        Apply the configuration chosen by the user. First of all a command string is generated, and then is executed on the device. Finally, the new configuration is retrieved directly from the device.
        Parameters:
        :param print (bool): when it is set on True, a feedback string is printed
        """
        gcs = self.generate_configuration_string()
        self.execute_command(gcs,False)
        if print: print('Setting parameters...')
        time.sleep(self.DELAY_CONF)
        self.retrieve_parameters()

    def set_custom_configuration(self,*,mode=None,source=None,jitter=None,arming=None,size=None,clock=None,clockfr=None,print=False):
        """
        Choose the configuration to apply on the device. All the parameters are optional, which means that if something is not specified, than it is kept on the current value. The function will finally apply the new configuration on the device.
        Parameters:
        :param mode (str): string representing the mode of measurement. Options: 'time','width','ratio','freq','period','phase','count'
        :param source (str): string representing the source of the measurement. Options: 'A','B','REF','RATIO'
        :param jitter (str): string representing the kind of jitter to compute. Options: 'ALL'(for Allan Variance),'STD'(for Standard Deviation)
        :param arming (str): string representing the kind of arming to use. Options: '+-time','+time','1per'(1 period),'1cs'(0.01 s),'1ds'(0.1 s),'1s'(1 s),'ext+-time','ext+time','extgate','ext1per','ext1cs','ext1ds','ext1s'
        :param size (float): number representing the number of samples. The value must be one the following: 1,2,5,1e1,2e1,5e1,1e2,2e2,5e2,1e3,2e3,5e3,1e4,2e4,5e4,1e5,2e5,5e5,1e6,2e6,5e6
        :param clock (str): string representing the source of the clock, internal or external. Options: 'int','ext'
        :param clockfr (str): string representing the frequency of the clock. Options: '10mhz'(10 MegaHz),'5mhz'(5 MegaHz)
        :param print (bool): when it is set on True, a feedback string is printed
        """
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
        """
        Set the mode of measurement.
        Parameters:
        :param mode (str): string representing the mode of measurement. Options: 'time','width','ratio','freq','period','phase','count'
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(mode=mode,print=print)

    def set_source(self,source:str,*,print=False):
        """
        Set the source of the measurement.
        Parameters:
        :param source (str): string representing the source of the measurement. Options: 'A','B','REF','RATIO'+
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(source=source,print=print)

    def set_jitter_type(self,jitter:str,*,print=False):
        """
        Set the kind of jitter to compute.
        Parameters:
        :param jitter (str): string representing the kind of jitter to compute. Options: 'ALL'(for Allan Variance),'STD'(for Standard Deviation)
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(jitter=jitter,print=print)

    def set_arming(self,arming:str,*,print=False):
        """
        Set the kind of arming to use.
        Parameters:
        :param arming (str): string representing the kind of arming to use. Options: '+-time','+time','1per'(1 period),'1cs'(0.01 s),'1ds'(0.1 s),'1s'(1 s),'ext+-time','ext+time','extgate','ext1per','ext1cs','ext1ds','ext1s'
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(arming=arming,print=print)

    def set_number_samples(self,size:int,*,print=False):
        """
        Set the number of samples.
        Parameters:
        :param size (float): number representing the number of samples. The value must be one the following: 1,2,5,1e1,2e1,5e1,1e2,2e2,5e2,1e3,2e3,5e3,1e4,2e4,5e4,1e5,2e5,5e5,1e6,2e6,5e6
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(size=size,print=print)

    def set_clock(self,clock:str,*,print=False):
        """
        Set the source of the clock, internal or external.
        Parameters:
        :param clock (str): string representing the source of the clock, internal or external. Options: 'int','ext'
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(clock=clock,print=print)

    def set_clock_frequency(self,clockfr:str,*,print=False):
        """
        Set the frequeny of the clock.
        Parameters:
        :param clockfr (str): string representing the frequency of the clock. Options: '10mhz'(10 MegaHz),'5mhz'(5 MegaHz)
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(clockfr=clockfr,print=print)

    def retrieve_parameters(self):
        """
        Retrieve the parameters set on the device, saving them in the corresponding attributes of the class.
        """
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
        """
        Return a string representing the configuration of the device.
        Parameters:
        :return (str): string representing the configuration of the device
        """
        return f"-------------------------------------\n***SR620 parameters configuration***\nMode: {self.mode}\nSource: {self.source}\nArming: {self.armm}\nNumOfSamples: {self.size}\nTypeOfJitter: {self.jttr}\nClock: {self.clock}\nClockFrequency: {self.clockfr}\n-------------------------------------"
    
    def measure(self,stat:str,*,progress=True) -> float:
        """
        Start a new measurement of the specified statistics on the device.
        Parameters:
        :param stat (str): string representing the statistics to measure. Options: 'mean','jitter','max','min'
        :param progress (bool): when it is set on True, a progress bar is showed on the console
        """
        self.ser.flush()
        thread = None
        if (progress and self.armm in self.ARMM_TIME.keys() and self.mode=='freq'):        
            thread = start_progress(int(self.size),self.ARMM_TIME[self.armm])
        res = self.execute_command(f'STOP; AUTM 0; MEAS? {self.STAT_DICT[stat]}',True)
        if (thread!=None):
            thread.join()
        return float(res['value_0'])
    
    def start_measurement_set(self,stat:str,num_meas:int,*,file_path=None,progress=False):
        """
        Start a new set of measures of the specified statistics on the device.
        Parameters:
        :param stat (str): string representing the statistics to measure. Options: 'mean','jitter','max','min'
        :param num_meas (int): number of measurements to perform
        :param file_path (str): if specified, the set of measurements is saved in the corresponding output file
        :param progress (bool): when it is set on True, a progress bar is showed on the console
        """
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
        """
        Start a set of measurements corresponding to the Allan Variance for an increasing number of observations.
        Parameters:
        :param num_powers (int): number of 'powers of ten' of observations to consider (i.e. if num_powers is set to 3, then the Allan Variance will be computed on 10^1, 10^2 and 10^3)
        :param file_path (str): if specified, the set of measurements is saved in the corresponding output file
        :param progress (bool): when it is set on True, a progress bar is showed on the console
        """
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