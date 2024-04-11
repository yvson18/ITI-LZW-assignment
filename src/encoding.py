from utils import *

def encode(data: bytes, max_dict_len: int) -> list[int]:
    curr_dict_len = 256
    dictionary = {bytes([i]): i for i in range(curr_dict_len)} # Inicializa o dicionário com os 255 valores possíveis para 8 bits

    previous_phrase = bytes()
    indices = [] # Saída vazia
    symbs_saw = [] # Informações sobre a compressão
   
    qnt_symb = 0
    for symb_int in tqdm(data, desc="Encoding", bar_format=bar_format):
        qnt_symb += 1
        current_symb = bytes([symb_int])
        current_phrase = previous_phrase + current_symb

        if current_phrase in dictionary:
            previous_phrase = current_phrase
        else:
            indices.append(dictionary[previous_phrase]) # Adiciona o índice da última frase encontrada à saída
            symbs_saw.append(qnt_symb) 
           
            if curr_dict_len < max_dict_len:
                dictionary[current_phrase] = curr_dict_len # Adiciona a nova frase no dicionário
                curr_dict_len += 1
            previous_phrase = current_symb # Continua do símbolo atual que quebrou a sequência de frases encontradas
    
    if previous_phrase:
        indices.append(dictionary[previous_phrase])
        symbs_saw.append(qnt_symb)

    return indices, dictionary, symbs_saw

def encode_rd(data: bytes, max_dict_len: int) -> list[int]:
    curr_dict_len = 256
    dictionary = {bytes([i]): i for i in range(curr_dict_len)} # Inicializa o dicionário com os 255 valores possíveis para 8 bits

    previous_phrase = bytes()
    indices = [] # Saída vazia
    symbs_saw = []
    qnt_symb = 0
    for symb_int in tqdm(data, desc="Encoding", bar_format=bar_format):
        qnt_symb += 1
        current_symb = bytes([symb_int])
        current_phrase = previous_phrase + current_symb

        if current_phrase in dictionary:
            previous_phrase = current_phrase
        else:
            indices.append(dictionary[previous_phrase]) # Adiciona o índice da última frase encontrada à saída
            symbs_saw.append(qnt_symb) 
            if curr_dict_len > max_dict_len:
                curr_dict_len = 256
                dictionary = {bytes([i]): i for i in range(curr_dict_len)} # Reinicializa o dicionário com os 255 valores possíveis para 8 bits
                
            dictionary[current_phrase] = curr_dict_len # Adiciona a nova frase no dicionário
            curr_dict_len += 1
            previous_phrase = current_symb # Continua do símbolo atual que quebrou a sequência de frases encontradas

    if previous_phrase:
        indices.append(dictionary[previous_phrase])
        symbs_saw.append(qnt_symb) 

    return indices, dictionary, symbs_saw


def decode(indices: list[int], max_dict_len: int) -> bytes:
    curr_dict_len = 256
    dictionary = {i: bytes([i]) for i in range(curr_dict_len)}  # Inicializa o dicionário com os 255 valores possíveis para 8 bits

    data = bytearray()
    prev_phrase = bytes([indices[0]])
    data.extend(prev_phrase)

    for idx in tqdm(indices[1:], desc="Decoding", bar_format=bar_format):
        if idx < curr_dict_len: # Significa que é uma frase já vista no dicionário
            curr_phrase = dictionary[idx]
        else: # Situação especial quando a frase em "idx" é requisitada para decodificação mas ainda está incompleta (não vista no dicionário)
            curr_phrase = prev_phrase + prev_phrase[:1]

        data.extend(curr_phrase) # Adiciona na saída
        if curr_dict_len < max_dict_len:
            dictionary[curr_dict_len] = prev_phrase + curr_phrase[:1] # Adiciona no dicionário a frase anterior junto do primeiro símbolo da frase atual
            curr_dict_len += 1
        prev_phrase = curr_phrase

    return bytes(data), dictionary

def decode_rd(indices: list[int], max_dict_len: int) -> bytes:
    curr_dict_len = 256
    dictionary = {i: bytes([i]) for i in range(curr_dict_len)}  # Inicializa o dicionário com os 255 valores possíveis para 8 bits

    data = bytearray()
    prev_phrase = bytes([indices[0]])
    data.extend(prev_phrase)

    for idx in tqdm(indices[1:]):
        if idx < curr_dict_len: # Significa que é uma frase já vista no dicionário
            curr_phrase = dictionary[idx]
        else: # Situação especial quando a frase em "idx" é requisitada para decodificação mas ainda está incompleta (não vista no dicionário)
            curr_phrase = prev_phrase + prev_phrase[:1]

        data.extend(curr_phrase) # Adiciona na saída

        if curr_dict_len > max_dict_len:
            curr_dict_len = 256
            dictionary = {i: bytes([i]) for i in range(curr_dict_len)} # Reinicializa o dicionário com os 255 valores possíveis para 8 bits

        dictionary[curr_dict_len] = prev_phrase + curr_phrase[:1] # Adiciona no dicionário a frase anterior junto do primeiro símbolo da frase atual
        curr_dict_len += 1
        prev_phrase = curr_phrase

    return bytes(data), dictionary
