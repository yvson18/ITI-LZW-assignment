from utils import *
from encoding import *
from io_builder import *

# import tempfile
# import subprocess

# def write_indices_to_file(filename, indices):
#     with tempfile.NamedTemporaryFile(mode='w', suffix='.lzey_temp', delete=False) as temp_file:
#         indices_line = ' '.join(map(str, indices))
#         temp_file.write(indices_line)
#         temp_filename = temp_file.name
#         print("Created ", temp_filename)
#     subprocess.run(['./io_builder.exe', '-w', '-f', filename, '-i', temp_filename])
#     os.remove(temp_filename)

# def read_indices_from_file(filename):
#     result = subprocess.run(['./io_builder.exe', '-r', '-f', filename], capture_output=True, text=True)
#     output = result.stdout.strip()
#     indices = list(map(int, output.split()))
#     return indices

# def compress(file, max_dict_len):
#     with open(file, 'rb') as f:
#         data = f.read()
#     indices, _ = encode(data, max_dict_len)
#     write_indices_to_file(file, indices)
#     return

# def decompress(file, max_dict_len):
#     indices = read_indices_from_file(file)
#     data, _ = decode(indices, max_dict_len)
#     filename, _ = get_filename_and_ext(file)
#     with open(f"{filename}2", 'wb') as f:
#         f.write(data)
#     return

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
