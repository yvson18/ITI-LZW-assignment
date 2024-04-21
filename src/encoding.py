from utils import *

class EncodeFeedbackInfo:
    def __init__(self, curr_dict_len, dictionary, symbs_saw, qnt_symb):
        self.curr_dict_len = curr_dict_len
        self.dictionary = dictionary
        self.symbs_saw = symbs_saw
        self.qnt_symb = qnt_symb

    def __iter__(self):
        yield self.curr_dict_len
        yield self.dictionary
        yield self.symbs_saw
        yield self.qnt_symb

def encode(files: list[str], max_dict_len: int, allow_rd: bool):
    indices_per_file = []

    curr_dict_len = 256
    dictionary = {bytes([i]): i for i in range(curr_dict_len)} # Inicializa o dicionário com os 255 valores possíveis para 8 bits
    symbs_saw = [] # Informações sobre a compressão
    qnt_symb = 0
    enc_fb_info = EncodeFeedbackInfo(curr_dict_len, dictionary, symbs_saw, qnt_symb)

    for file_idx, file in enumerate(files):
        with open(file, 'rb') as f:
            data = f.read()

        indices, enc_fb_info = encode_bytes(data, max_dict_len, file_idx, allow_rd, enc_fb_info)
        indices_per_file.append(indices)

    return indices_per_file, enc_fb_info

def encode_bytes(data: bytes, max_dict_len: int, file_idx: int, allow_rd: bool, enc_fb_info: EncodeFeedbackInfo) -> list[int]:
    curr_dict_len, dictionary, symbs_saw, qnt_symb = enc_fb_info
    indices = [] # Saída vazia
    previous_phrase = bytes() # Necessário pois indica EOF do arquivo anterior

    for symb_int in tqdm(data, desc=f"Encoding file #{file_idx+1}", bar_format=bar_format):
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
            else: # Caso o tamanho chegue o limite máximo
                if allow_rd: # E se a estratégia RD for permitida
                    curr_dict_len = 256
                    dictionary = {bytes([i]): i for i in range(curr_dict_len)} # Reinicia o dicionário com os 255 valores possíveis para 8 bits
                    dictionary[current_phrase] = curr_dict_len # Adiciona a nova frase no dicionário
                    curr_dict_len += 1

            previous_phrase = current_symb # Continua do símbolo atual que quebrou a sequência de frases encontradas

    if previous_phrase:
        indices.append(dictionary[previous_phrase])
        symbs_saw.append(qnt_symb)

    return indices, EncodeFeedbackInfo(curr_dict_len, dictionary, symbs_saw, qnt_symb)

class DecodeFeedbackInfo:
    def __init__(self, curr_dict_len, dictionary):
        self.curr_dict_len = curr_dict_len
        self.dictionary = dictionary

    def __iter__(self):
        yield self.curr_dict_len
        yield self.dictionary

def decode(indices_per_file, filenames: list[str], max_dict_len: int, allow_rd: bool):
    datas_per_file = []

    curr_dict_len = 256
    dictionary = {i: bytes([i]) for i in range(curr_dict_len)}  # Inicializa o dicionário com os 255 valores possíveis para 8 bits
    dec_fb_info = DecodeFeedbackInfo(curr_dict_len, dictionary)

    for file_idx, filename in enumerate(filenames):
        data, dec_fb_info = decode_bytes(indices_per_file[file_idx], max_dict_len, file_idx, allow_rd, dec_fb_info)
        datas_per_file.append(data)
        with open(filename, 'wb') as f:
            f.write(data)
            print(f"Decompressed {filename}")

    return datas_per_file, dec_fb_info

def decode_bytes(indices: list[int], max_dict_len: int, file_idx: int, allow_rd: bool, dec_fb_info: DecodeFeedbackInfo) -> bytes:
    curr_dict_len, dictionary = dec_fb_info

    data = bytearray()
    prev_phrase = dictionary[indices[0]] # Necessário por causa do EOF do arquivo anterior
    data.extend(prev_phrase)

    for idx in tqdm(indices[1:], desc=f"Decoding file #{file_idx+1}", bar_format=bar_format):
        if idx < curr_dict_len: # Significa que é uma frase já vista no dicionário
            curr_phrase = dictionary[idx]
        else: # Situação especial quando a frase em "idx" é requisitada para decodificação mas ainda está incompleta (não vista no dicionário)
            curr_phrase = prev_phrase + prev_phrase[:1]

        data.extend(curr_phrase) # Adiciona na saída
        if curr_dict_len < max_dict_len:
            dictionary[curr_dict_len] = prev_phrase + curr_phrase[:1] # Adiciona no dicionário a frase anterior junto do primeiro símbolo da frase atual
            curr_dict_len += 1
        else: # Caso o tamanho chegue o limite máximo
            if allow_rd: # E se a estratégia RD for permitida
                curr_dict_len = 256
                dictionary = {i: bytes([i]) for i in range(curr_dict_len)} # Reinicia o dicionário com os 255 valores possíveis para 8 bits
                dictionary[curr_dict_len] = prev_phrase + curr_phrase[:1] # Adiciona no dicionário a frase anterior junto do primeiro símbolo da frase atual
                curr_dict_len += 1

        prev_phrase = curr_phrase

    return bytes(data), DecodeFeedbackInfo(curr_dict_len, dictionary)

def encode_rc(data: bytes, max_dict_len: int) -> list[int]:
    curr_dict_len = 256
    dictionary = {bytes([i]): i for i in range(curr_dict_len)} # Inicializa o dicionário com os 255 valores possíveis para 8 bits

    previous_phrase = bytes()
    
    indices = [] # Saída vazia
    symbs_saw = [] # Informações sobre a compressão
    
    code_len = 0
    qnt_symb = 0
    qnt_reiniciar = 1
    last_comp_medio = 8
    current_comp_medio = 0
        
    for symb_int in tqdm(data, desc="Encoding", bar_format=bar_format):
        
        current_symb = bytes([symb_int])
        current_phrase = previous_phrase + current_symb
        qnt_symb += 1
            
        if current_phrase in dictionary:
            previous_phrase = current_phrase
        else:
            indices.append(dictionary[previous_phrase]) # Adiciona o índice da última frase encontrada à saída
            symbs_saw.append(qnt_symb)

            # Adiciona a nova frase no dicionário caso o dict não esteja cheio
            if curr_dict_len < max_dict_len:
                dictionary[current_phrase] = curr_dict_len 
                curr_dict_len += 1

            # code len
            if(dictionary[previous_phrase] > 255):
                    code_len += dictionary[previous_phrase].bit_length()
            else:
                code_len += 8

            # monitorar compressão a cada 100 symb se não estiver comprimindo reinicia o dict tolerância de 10⁻4 de diff entre ultima leitura e leitura atual   
            if (qnt_reiniciar > 0):
                if (qnt_symb % 100 == 0):
                    current_comp_medio = code_len / (qnt_symb - 1)
                    if ((last_comp_medio - current_comp_medio) < 0.0001):
                        curr_dict_len = 256
                        dictionary = {bytes([i]): i for i in range(curr_dict_len)}
                        qnt_reiniciar -= 1 # evita o dict reiniciar várias vezes
                        where_rc = len(indices)
                    last_comp_medio = current_comp_medio
            
            previous_phrase = current_symb # Continua do símbolo atual que quebrou a sequência de frases encontradas
    
    if previous_phrase:
        indices.append(dictionary[previous_phrase])
        symbs_saw.append(qnt_symb)

    return indices, dictionary, symbs_saw, where_rc

def decode_rc(indices: list[int], max_dict_len: int, where_rc: int):
    data_1, _ = decode(indices[:where_rc], max_dict_len)
    data_2, _ = decode(indices[where_rc:], max_dict_len)

    return data_1 + data_2
