from tqdm import tqdm
import threading
import time

def parse_string_to_dict(string:str) -> dict:
    parts = string.strip().rstrip('\r').split(';')
    result = {f'value_{i}': float(parts[i]) for i in range(len(parts))}
    return result

def progress(i):
    for j in tqdm(range(i)):
        time.sleep(i)

def start_progress(i):
    threadpr = threading.Thread(target=progress, args=(i,))
    threadpr.start()
    return threadpr