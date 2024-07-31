def parse_string_to_dict(string:str) -> dict:
    parts = str.strip().rstrip('\r').split(',')
    result = {f'value_{i}': float(parts[i]) for i in range(len(parts))}
    return result