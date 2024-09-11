'''
Unofficial library to manage a SR620 Universal Time Counter (Stanford Research Systems)

@requires: pip install pyserial,tqdm

@author: Matteo Tedde (Lab3841 s.r.l.)
@contact: teddematteo03@gmail.com
'''
from .sr620utils import *
from .sr620exceptions import *
from .sr620constants import *
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import allantools
import serial
import time
import logging

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
    ARMM_TIME = {'1cs':0.01,'1ds':0.1,'1s':1,'ext1cs':0.01,'ext1ds':0.1,'ext1s':1,'1per':0.001}
    DELAY_CONF = 1

    def __init__(self,serial_port_path:str,log_file=None):
        """
        Constructor.
        Parameters:
        :param serial_port_path (str): path of the serial port on which the device is connected (i.e. "/dev/ttyUSB0")
        :param log_file (str): path to the log file. If nothing is specified, then the output will be the console
        """
        try:
            self.cont = True
            logging.basicConfig(filename=log_file,level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
            self.ser = serial.Serial(serial_port_path,9600,timeout=None)
            self.__execute_command__("STOP;AUTM0;",False)
            logging.debug('Connection established...')
            self.__retrieve_parameters__()
        except:
            self.cont = False
            logging.error('Error in opening the connection')
            raise #program terminated
            
    def close_connection(self):
        """
        Close the serial port connection.
        """
        try:
            self.ser.close()
        finally:
            logging.debug('...Connection expired!')
        
    def __execute_command__(self,command:str,needs_response:bool):
        """
        Execute a command on the machine.
        Parameters:
        :param command (str): command that must be executed, according to the format requested by the device ('command(?) param')
        :param needs_response (bool): when an output is expected from the device must be set on True, otherwise on False
        :return (dict): value returned when needs_response is set on True. The format is a dictionary whose keys are progressive strings 'value_i', with the corresponding returned values (i.e. {'value_0':'10','value_1':'5','value_2':'30'})
        """
        try:
            self.ser.timeout = 0.1 #clean the buffer (the only working way...)
            self.ser.readall()
            self.ser.timeout = None
            
            self.ser.write(command.encode('ASCII')+b'\r')
            self.ser.flush()
        except:
            self.cont = False
            logging.error("An error has occured while writing on the device. The execution has been concluded!")
            raise SR620WriteException()

        if needs_response: #if a response is needed
            try:
                response = self.ser.read_until(b'\r\n').decode('utf-8')
                return parse_string_to_dict(response)
            except:
                self.cont = False
                logging.error("An error has occured while reading from the device. The execution has been concluded!")
                raise SR620ReadException()
            
        
            
    def __generate_configuration_string__(self) -> str:
        """
        Generate a command string containing the configuration of the device, according to the values set by the user.
        Parameters:
        :return (str): string representing the command
        """
        try:
            cmm = f"SRCE {self.SOURCE_DICT[self.source]}; MODE {self.MODE_DICT[self.mode]}; ARMM {self.ARMM_DICT[self.armm]}; SIZE {self.size}; JTTR {self.JTTR_DICT[self.jttr]}; CLCK {self.CLCK_DICT[self.clock]}; CLKF {self.CLKF_DICT[self.clockfr]};"
            return cmm
        except:
            self.cont = False
            logging.error("One (or more) of the parameters does not exist! The execution has been concluded... please, check the documentation!")
            raise SR620ValueException()

    def __apply_custom_configuration__(self,*,print=True):
        """
        Apply the configuration chosen by the user. First of all a command string is generated, and then is executed on the device. Finally, the new configuration is retrieved directly from the device.
        Parameters:
        :param print (bool): when it is set on True, a feedback string is printed
        """
        gcs = self.__generate_configuration_string__()
        self.__execute_command__(gcs,False)
        if print: logging.debug('Setting parameters...')
        time.sleep(self.DELAY_CONF)
        self.__retrieve_parameters__()

    def set_custom_configuration(self,*,mode=None,source=None,jitter=None,arming=None,size=None,clock=None,clock_frequency=None,print=False):
        """
        Choose the configuration to apply on the device. All the parameters are optional, which means that if something is not specified, than it is kept on the current value. The function will finally apply the new configuration on the device.
        Parameters:
        :param mode (str): string representing the mode of measurement. Options: MODE_TIME,MODE_WIDTH,MODE_RATIO,MODE_FREQUENCY,MODE_PERIOD,MODE_PHASE,MODE_COUNT
        :param source (str): string representing the source of the measurement. Options: SOURCE_A,SOURCE_B,SOURCE_REF,SOURCE_RATIO
        :param jitter (str): string representing the kind of jitter to compute. Options: JITTER_ALLAN(for Allan Variance),JITTER_STDDEV(for Standard Deviation)
        :param arming (str): string representing the kind of arming to use. Options: ARMING_PLUS_MINUS_TIME,ARMING_PLUS_TIME,ARMING_PERIOD(1 period),ARMING_CENTISECOND(0.01 s),ARMING_DECISECOND(0.1 s),ARMING_SECOND(1 s),ARMING_EXT_PLUS_MINUS_TIME,ARMING_EXT_PLUS_TIME,ARMING_EXT_GATE,ARMING_EXT_PERIOD,ARMING_EXT_CENTISECOND,ARMING_EXT_DECISECOND,ARMING_EXT_SECOND
        :param size (float): number representing the number of samples. The value must be one the following: 1,2,5,1e1,2e1,5e1,1e2,2e2,5e2,1e3,2e3,5e3,1e4,2e4,5e4,1e5,2e5,5e5,1e6,2e6,5e6
        :param clock (str): string representing the source of the clock, internal or external. Options: CLOCK_INTERNAL,CLOCK_EXTERNAL
        :param clockfr (str): string representing the frequency of the clock. Options: CLOCK_FREQUENCY_10_MEGAHZ,CLOCK_FREQUENCY_5_MEGAHZ
        :param print (bool): when it is set on True, a feedback string is printed
        """
        try:
            if mode!=None: self.mode = mode
            if source!=None: self.source = source
            if jitter!=None: self.jttr = jitter
            if arming!=None: self.armm = arming
            if clock!=None: self.clock = clock
            if clock_frequency!=None: self.clockfr = clock_frequency
            if size!=None: 
                if (size not in self.SIZE_LIST):
                    logging.error("The size inserted is not valid! The execution has been concluded... please, check the documentation!")
                    raise SR620SizeException(self.SIZE_LIST)
                else:
                    self.size = size
            self.__apply_custom_configuration__(print=print)
            if print: logging.info("Current configuration:\n"+str(self))
        except:
            logging.error("Configuration set terminated with an error")
            
    def set_mode(self,mode:str,*,print=False):
        """
        Set the mode of measurement.
        Parameters:
        :param mode (str): string representing the mode of measurement. Options: MODE_TIME,MODE_WIDTH,MODE_RATIO,MODE_FREQUENCY,MODE_PERIOD,MODE_PHASE,MODE_COUNT
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(mode=mode,print=print)

    def set_source(self,source:str,*,print=False):
        """
        Set the source of the measurement.
        Parameters:
        :param source (str): string representing the source of the measurement. Options: SOURCE_A,SOURCE_B,SOURCE_REF,SOURCE_RATIO
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(source=source,print=print)

    def set_jitter_type(self,jitter:str,*,print=False):
        """
        Set the kind of jitter to compute.
        Parameters:
        :param jitter (str): string representing the kind of jitter to compute. Options: JITTER_ALLAN(for Allan Variance),JITTER_STDDEV(for Standard Deviation)
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(jitter=jitter,print=print)

    def set_arming(self,arming:str,*,print=False):
        """
        Set the kind of arming to use.
        Parameters:
        :param arming (str): string representing the kind of arming to use. Options: ARMING_PLUS_MINUS_TIME,ARMING_PLUS_TIME,ARMING_PERIOD(1 period),ARMING_CENTISECOND(0.01 s),ARMING_DECISECOND(0.1 s),ARMING_SECOND(1 s),ARMING_EXT_PLUS_MINUS_TIME,ARMING_EXT_PLUS_TIME,ARMING_EXT_GATE,ARMING_EXT_PERIOD,ARMING_EXT_CENTISECOND,ARMING_EXT_DECISECOND,ARMING_EXT_SECOND
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
        :param clock (str): string representing the source of the clock, internal or external. Options: CLOCK_INTERNAL,CLOCK_EXTERNAL
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(clock=clock,print=print)

    def set_clock_frequency(self,clockfr:str,*,print=False):
        """
        Set the frequeny of the clock.
        Parameters:
        :param clockfr (str): string representing the frequency of the clock. Options: CLOCK_FREQUENCY_10_MEGAHZ,CLOCK_FREQUENCY_5_MEGAHZ
        :param print (bool): when it is set on True, a feedback string is printed
        """
        self.set_custom_configuration(clock_frequency=clockfr,print=print)

    def __retrieve_parameters__(self):
        """
        Retrieve the parameters set on the device, saving them in the corresponding attributes of the class.
        """
        res = self.__execute_command__("STUP?;",True)
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
    
    def measure(self,stat=STATISTICS_MEAN,*,progress=True) -> float:
        """
        Start a new measurement of the specified statistics on the device.
        Parameters:
        :param stat (str): string representing the statistics to measure. Options: STATISTICS_MEAN,STATISTICS_JITTER,STATISTICS_MAX,STATISTICS_MIN
        :param progress (bool): when it is set on True, a progress bar is shown on the console
        """
        try:
            thread = None
            if (progress and self.armm in self.ARMM_TIME.keys() and self.mode=='freq'):        
                thread = start_progress(int(self.size),self.ARMM_TIME[self.armm],self)
            res = self.__execute_command__(f'STOP;AUTM0;MEAS?{self.STAT_DICT[stat]}',True)
            if (thread!=None):
                thread.join()
            return float(res['value_0'])
        except:
            logging.error('Measure terminated')
            return None #program not terminated
    
    def start_measurement_set(self,stat:str,num_meas:int,*,file_path=None,print=True,progress=False) -> list:
        """
        Start a new set of measures of the specified statistics on the device. Return a list of the measurements.
        Parameters:
        :param stat (str): string representing the statistics to measure. Options: STATISTICS_MEAN,STATISTICS_JITTER,STATISTICS_MAX,STATISTICS_MIN
        :param num_meas (int): number of measurements to perform
        :param file_path (str): if specified, the set of measurements is saved in the corresponding output file
        :param progress (bool): when it is set on True, a progress bar is shown on the console
        :return (list): list of float values corresponding to the measurements
        """
        if print: logging.debug('Measurement set started...')
        fout = None
        lst = []
        try:
            if file_path!=None:
                fout = open(file_path,'w')
                fout.write(f'timestamp,{stat}\n')
                fout.flush()
            for i in range(num_meas):
                if self.cont:
                    res = self.measure(stat,progress=progress)
                    if res is not None:
                        lst.append(res)
                        rec = f"{str(datetime.now(ZoneInfo('Europe/Rome')))},{res}"
                        if print: logging.debug(f'Value read: {res}')
                        if fout!=None:
                            fout.write(rec+'\n')
                            fout.flush()
            if fout!=None:
                fout.close()
                if print: logging.debug(f'Measurement set concluded, file saved in {file_path}')
        except:
            logging.error('Measurement set terminated')
        return lst

    def start_measurement_set_forever(self,stat:str,*,file_path=None,print=True,progress=False) -> list:
        """
        Start a new set of measures of the specified statistics on the device. Return a list of the measurements.
        Parameters:
        :param stat (str): string representing the statistics to measure. Options: STATISTICS_MEAN,STATISTICS_JITTER,STATISTICS_MAX,STATISTICS_MIN
        :param file_path (str): if specified, the set of measurements is saved in the corresponding output file
        :param progress (bool): when it is set on True, a progress bar is shown on the console
        :return (list): list of float values corresponding to the measurements
        """
        if print: logging.debug('Measurement set started...')
        fout = None
        lst = []
        try:
            if file_path!=None:
                fout = open(file_path,'w')
                fout.write(f'timestamp,{stat}\n')
                fout.flush()
            while self.cont:
                res = self.measure(stat,progress=progress)
                if res is not None:
                    lst.append(res)
                    rec = f"{str(datetime.now(ZoneInfo('Europe/Rome')))},{res}"
                    if print: logging.debug(f'Value read: {res}')
                    if fout!=None:
                        fout.write(rec+'\n')
                        fout.flush()
            if fout!=None:
                fout.close()
                if print: logging.debug(f'Measurement set concluded, file saved in {file_path}')
        except:
            logging.error('Measurement set terminated')
        return lst

    def start_measurement_allan_variance(self,n:int,*,command=ALLAN_OVERLAPPING,file_path=None,plot_path=None,progress=True,print=True) -> dict:
        """
        Start a set of measurements corresponding to the Allan Variance for an increasing averaging time. Return a dictionary of the measurements.
        Parameters:
        :param n (int): number of measurements to perform
        :param command (str): kind of Allan Variance to compute. Options: ALLAN_CLASSIC, ALLAN_OVERLAPPING, ALLAN_MODIFIED
        :param file_path (str): if specified, the set of measurements is saved in the corresponding output file
        :param plot_path (str): if specified, the plot is saved in the corresponding output file
        :param progress (bool): when it is set on True, a progress bar is shown on the console
        :return (dict): dictionary containing the measurements. The keys are the averaging times, while the values are the corresponding Allan Variances
        """
        thread = None
        dct = {}
        lst = []
        try:
            if (progress):        
                thread = start_progress(n,self.ARMM_TIME[self.armm],self)
            fout = None
            if file_path!=None:
                fout = open(file_path,'w')
                fout.write(f'averaging time,allan deviation\n')
                fout.flush()
            self.set_number_samples(1)
            for i in range(n):
                if self.cont:
                    res = self.measure(STATISTICS_MEAN,progress=False)
                    if res is not None:
                        lst.append(res)
            
            a = allantools.Dataset(data=lst,rate=1/self.ARMM_TIME[self.armm])
            a.compute(command) #compute allan variance

            for i in range(len(a.out['taus'])):
                dct[float(a.out['taus'][i])] = float(a.out['stat'][i])
                if fout!=None:
                    rec = f"{float(a.out['taus'][i])},{float(a.out['stat'][i])}"
                    fout.write(rec+'\n')
                    fout.flush()

            if fout!=None:
                fout.close()
                if print: logging.debug(f'Measurement set concluded, file saved in {file_path}')

            if plot_path!=None:
                save_plot(a,plot_path)
                if print: logging.debug(f'Plot created, file saved in {plot_path}')

        except:
            logging.error('Measurement set terminated')
        return dct