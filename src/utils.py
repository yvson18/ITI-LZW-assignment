import os
import math
import argparse
import numpy as np
from tqdm import tqdm
from collections import Counter
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog

bar_format = "{desc}: {percentage:3.0f}%|{bar:50}| {n_fmt}/{total_fmt} | {elapsed}<{remaining} | elapsed: {elapsed_s:.3f}s"

def get_args():
    parser = argparse.ArgumentParser(description="LZEY")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--compress", action="store_true", help="compression mode")
    group.add_argument("-d", "--decompress", action="store_true", help="decompression mode")
    parser.add_argument("-rd", action="store_true", help="use RD strategy for compression mode")
    args = parser.parse_args()
    return vars(args)

def provide_files(args):
    mode = "compress" if args['compress'] else "decompress"
    filetypes = [("All files", "*")] if args['compress'] else [("LZEY files", "*.lzey")]
    print(f"Select files to {mode}")
    files = filedialog.askopenfilenames(
        initialdir=os.getcwd(),
        title=f"Select files to {mode}",
        filetypes=filetypes
    )
    return list(files)

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

def static_entropy(data: bytes) -> float:
    total = len(data)
    frequency = Counter(data)
    relative_frequency = {byte: count / total for byte, count in frequency.items()}
    
    h = 0
    for byte in relative_frequency.keys():
        p = relative_frequency[byte]
        h += p * math.log2(1 / p)
    
    return h

def create_compression_series(indices: list[int], symbs_saw: list[int]):
    bit_dep = 8
    max_bit_dep = bit_dep
    qnt_bits_m = 0
    comp = []

    for i in tqdm(range(len(symbs_saw)), desc="Calculating series", bar_format=bar_format):
        if indices[i] > 255:
            bit_dep = indices[i].bit_length()
        
        if(bit_dep > max_bit_dep):
            max_bit_dep = bit_dep
            
        qnt_bits_m +=  max_bit_dep
        comp.append(qnt_bits_m / (symbs_saw[i] -1))

    return comp

def plot_compression_series(comp: list[int], plot_title: str, output_path: str) -> None:
    qnt_symbs_saw = np.arange(1, len(comp) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(qnt_symbs_saw, comp, marker='o', linestyle='-')

    plt.xscale('log')

    plt.title(plot_title)
    plt.xlabel('symb (bytes)')
    plt.ylabel('Comprimento Médio (bits)')
    plt.grid(True, which="both", ls="--")

    plt.savefig(output_path)
