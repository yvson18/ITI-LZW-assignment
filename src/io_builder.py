from utils import *

def write_bytes(min_nb_bits: int, file_idx: int, indices: list[int], enable_tqdm: bool = True):
    bits_counter = 0
    current_byte = 0b0
    packed_bytes = bytearray()

    for idx in tqdm(indices, desc=f"Writing bytes of file #{file_idx+1}", bar_format=bar_format, disable=not enable_tqdm):
        nb_bits = idx.bit_length()
        for i in range(min_nb_bits-1, -1, -1): # Itera sobre cada bit do índice da esquerda para direita, começando do mínimo número de bits
            if i < nb_bits: # Caso o número de bits do índice seja menor do que o mínimo necessário, o bit "i" é tratado como 0, que não faz diferença no OR
                current_byte |= ((idx >> i) & 1) # Constroi o byte com cada bit restante dos elementos anteriores e o atual
            bits_counter += 1
            # print(bin(current_byte))
            if bits_counter == 8: # Se completou o byte
                # print("salvou")
                packed_bytes.append(current_byte) # Salva o byte
                current_byte = 0 # Reinicia o byte
                bits_counter = 0
            else:
                current_byte <<= 1  # Constroi o byte com cada bit restante dos elementos anteriores e o atual
        # print(bin(current_byte))
        # print()

    # print(bin(current_byte))
    # print()
    if bits_counter > 0: # Se ainda existem bits sobrando, preenche com 0 até completar o byte
        current_byte >>= 1 # Necessário pois o último bit do último índice não precisa do shift para preparar a operação OR com o primeiro bit do próximo índice
        current_byte <<= (8 - bits_counter)
        packed_bytes.append(current_byte)
        # print(bin(current_byte))

    # print(packed_bytes)
    # for p in packed_bytes:
    #     print(p)
    return packed_bytes

def write_file(indices_per_file, filepaths, allow_rd: bool):
    min_nb_bits = max(get_nb_bits_and_bytes(indices)[0] for indices in indices_per_file)
    nb_files = len(filepaths)
    packed_bytes = bytearray([min_nb_bits, allow_rd, nb_files])
    all_files_bytes = bytearray()

    for file_idx, filepath in enumerate(filepaths):
        p_bytes = write_bytes(min_nb_bits, file_idx, indices_per_file[file_idx])
        all_files_bytes.extend(p_bytes)
        name, ext = get_filename_and_ext(filepath)
        filename = name + ext
        filename_utf8 = filename.encode("utf-8")
        packed_bytes.append(len(filename_utf8)) # Número de bytes que o filename leva
        packed_bytes.extend(filename_utf8) # Filename em bytes
        qnt_bytes_in_4_bytes = write_bytes(32, 1, [len(p_bytes)], False)
        packed_bytes.extend(qnt_bytes_in_4_bytes) # Quantidade de bytes codificados para o arquivo

    packed_bytes.extend(all_files_bytes)

    out_filename, _ = get_filename_and_ext(filepaths[0])    
    if nb_files > 1:
        out_filename += "_merged"
    out_file = out_filename + ".lzey"

    with open(out_file, 'wb') as file:
        file.write(packed_bytes)

    print(f"Data compressed to {out_file}")
    return

def read_bytes(min_nb_bits: int, file_idx: int, packed_bytes, enable_tqdm: bool = True):
    indices = []
    bits_counter = 0
    current_byte = 0b0

    for byte in tqdm(packed_bytes, desc=f"Reading bytes of file {file_idx+1}", bar_format=bar_format, disable=not enable_tqdm):
        # print(to_fixed_bits(byte, 8))
        for i in range(8): # Para iterar por cada posição do byte
            current_bit = (byte >> (7 - i)) & 1 # Coloca o bit da posição "i" em current_bit[LSB]
            current_byte |= current_bit << ((min_nb_bits - 1) - bits_counter) # Coloca o bit atual em current_byte[bits_counter]
            bits_counter += 1
            if bits_counter == min_nb_bits: # Se o "byte" está completo
                # print(f"{bin(current_byte)=}")
                # print()
                indices.append(from_fixed_bits(current_byte, min_nb_bits)) # Salva o "byte"
                current_byte = 0  # Reinicia o "byte"
                bits_counter = 0

    # Bits restantes são extras para completar o último byte, não fazendo parte dos índices
    return indices

def extract(arr, nb_elems):
    if not hasattr(extract, 'last_index'):
        extract.last_index = 0
    if not hasattr(extract, 'arr'):
        extract.arr = arr
    if arr != extract.arr:
        extract.arr = arr
        extract.last_index = 0
    start_index = extract.last_index
    end_index = start_index + nb_elems
    extract.last_index = end_index
    if start_index >= len(arr):
        print("No more elements to extract")
    return arr[start_index:end_index]

def read_file(filename):
    with open(filename, 'rb') as file:
        packed_bytes = file.read()

    nb_bytes_per_file = []
    filenames = []
    min_nb_bits = read_bytes(8, 1, extract(packed_bytes, 1), False)[0] # Quantidade de bits que representa cada índice
    allow_rd = bool(read_bytes(8, 1, extract(packed_bytes, 1), False)[0]) # Usar ou não estratégia RD para descomprimir os arquivos
    nb_files = read_bytes(8, 1, extract(packed_bytes, 1), False)[0] # Número de arquivos comprimidos
    for _ in range(nb_files):
        len_filename = read_bytes(8, 1, extract(packed_bytes, 1), False)[0]
        file = extract(packed_bytes, len_filename).decode("utf-8")
        filenames.append(file)
        qnt_bytes_in_4_bytes = extract(packed_bytes, 4)
        nb_bytes_per_file.append(read_bytes(32, 1, qnt_bytes_in_4_bytes, False)[0])

    indices_per_file = []
    for file_idx, file in enumerate(filenames):
        p_bytes = extract(packed_bytes, nb_bytes_per_file[file_idx])
        indices = read_bytes(min_nb_bits, file_idx, p_bytes)
        indices_per_file.append(indices)

    return indices_per_file, filenames, allow_rd
