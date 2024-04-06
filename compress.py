from utils import *
from encoding import *
from io_builder import *

def compress(file, max_dict_len):
    with open(file, 'rb') as f:
        data = f.read()
    indices, _ = encode(data, max_dict_len)
    filename, _ = get_filename_and_ext(file)
    write_file(indices, f"{filename}.lzey")
    return

def decompress(file, max_dict_len):
    indices = read_file(file)
    filename, _ = get_filename_and_ext(file)
    data, _ = decode(indices, max_dict_len)
    with open(f"{filename}2", 'wb') as f:
        f.write(data)
    return
