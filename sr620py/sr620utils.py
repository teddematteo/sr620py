from tqdm import tqdm
from sr620exceptions import *
import threading
import time

def parse_string_to_dict(string:str) -> dict:
    result = {'value_0':'-1'}
    try:
        parts = string.strip().rstrip('\r').split(',')
        result = {f'value_{i}': parts[i] for i in range(len(parts))}
    except Exception:
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

def progress(tot,p):
    print('Measuring...')
    for j in tqdm(range(tot)):
        time.sleep(p)
    print('Measure completed!...')

def start_progress(tot,p):
    threadpr = threading.Thread(target=progress, args=(tot,p))
    threadpr.start()
    return threadpr