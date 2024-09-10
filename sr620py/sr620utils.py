from .sr620exceptions import *
from tqdm import tqdm
import threading
import time
import logging

def parse_string_to_dict(string:str) -> dict:
    result = {'value_0':'-1'}
    try:
        parts = string.strip().rstrip('\r').split(',')
        result = {f'value_{i}': parts[i] for i in range(len(parts))}
    except BaseException:
        logging.error("An error has occured while reading from the device. The execution has been concluded!")
        raise SR620ReadException()
    finally:
        return result
    
def get_key_from_value(d:dict,value):
    for k, v in d.items():
        if v == value:
            return k
    return None

def get_bit(x, i):
    shifted_x = x >> i
    bit = shifted_x & 1
    return bit

def progress(tot,p,dev):
    #logging.debug('Start measuring...')
    for j in tqdm(range(tot)):
        time.sleep(p)
        if (not dev.cont):
            break
    #logging.debug('Measurement completed!...')

def start_progress(tot,p,dev):
    threadpr = threading.Thread(target=progress, args=(tot,p,dev))
    threadpr.start()
    return threadpr

def tot_allan_time(p):
    tot = 0
    for i in range(1,p+1):
        tot = tot+int(float(f'1e{i}'))
    return tot

# def get_log_file_path():
#     for handler in logging.getLogger().handlers:
#         if isinstance(handler, logging.FileHandler):
#             return open(handler.baseFilename,'a')
#     return None