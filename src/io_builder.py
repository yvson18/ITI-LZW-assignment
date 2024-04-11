from utils import *

def write_file(indices, filename):
    bits_counter = 0
    current_byte = 0b0
    min_nb_bits, _ = get_nb_bits_and_bytes(indices)
    packed_bytes = bytearray([min_nb_bits])

    for idx in tqdm(indices, desc="Saving", bar_format=bar_format):
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

    with open(filename, 'wb') as file:
        file.write(packed_bytes)
    return

def read_file(filename):
    with open(filename, 'rb') as file:
        packed_bytes = file.read()

    indices = []
    bits_counter = 0
    current_byte = 0b0
    min_nb_bits = packed_bytes[0]  # Quantidade de bits que representa cada índice

    for byte in tqdm(packed_bytes[1:], desc="Reading", bar_format=bar_format):
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
