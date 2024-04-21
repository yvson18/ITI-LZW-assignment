from utils import *
from encoding import *
from io_builder import *

def compress(files : list[str], max_dict_len : int, allow_rd: bool):
    if allow_rd:
        print("Compressing with RD strategy")
    indices_per_file, _ = encode(files, max_dict_len, allow_rd)
    write_file(indices_per_file, files, allow_rd)
    return

def decompress(files : list[str], max_dict_len : int):
    for file in files:
        indices_per_file, filenames, allow_rd = read_file(file)
        if allow_rd:
            print("Decompressing with RD strategy")
        decode(indices_per_file, filenames, max_dict_len, allow_rd)
    return
