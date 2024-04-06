import os
import argparse
from tqdm import tqdm

bar_format = "{desc}: {percentage:3.0f}%|{bar:50}| {n_fmt}/{total_fmt} | {elapsed}<{remaining} | elapsed: {elapsed_s:.3f}s"

def get_args():
    parser = argparse.ArgumentParser(description="LZEY")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--compress", action="store_true", help="compress the file")
    group.add_argument("-d", "--decompress", action="store_true", help="decompress the file")
    parser.add_argument("filename", help="name of the file to compress or decompress")
    args = parser.parse_args()
    return vars(args)

def get_filename_and_ext(filepath):
    filename_ext = os.path.basename(filepath)
    filename, ext = os.path.splitext(filename_ext)
    return filename, ext

def get_nb_bits_and_bytes(indices: list[int]): # Retorna o número mínimo de bits e bytes para representar os índices
    max_value = max(indices)
    min_nb_bits = max_value.bit_length()
    min_nb_bytes = (min_nb_bits + 7) // 8
    return min_nb_bits, min_nb_bytes

def to_fixed_bits(number, nb_bits): # Escreve uma string do número em binário com "nb_bits"
    return bin(number)[2:].zfill(nb_bits)

def from_fixed_bits(binary, nb_bits): # Retorna um número pelos primeiros "nb_bits" de um binário
    return int(bin(binary)[2:].zfill(8)[-nb_bits:], 2)
