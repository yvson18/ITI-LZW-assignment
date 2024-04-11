#include <iostream>
#include <vector>
#include <fstream>
#include <cstdint>

std::vector<uint32_t> read_indices_from_file(const std::string& filename)
{
    std::ifstream infile(filename);
    if (!infile.is_open())
    {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return {};
    }

    std::vector<uint32_t> indices;
    uint32_t index;
    while (infile >> index)
    {
        indices.push_back(index);
    }

    infile.close();
    return indices;
}

std::string parse_filename(const std::string& filename)
{
    std::string output_filename = filename;
    size_t dot_pos = output_filename.find_last_of('.');
    
    if (dot_pos == std::string::npos || dot_pos == 0)
    {
        output_filename += ".lzey";
    }
    else
    {
        output_filename = output_filename.substr(0, dot_pos) + ".lzey";
    }

    return output_filename;
}

uint8_t get_nb_bits(const std::vector<uint32_t>& indices)
{
    uint8_t min_nb_bits = 0;
    for (uint32_t idx : indices)
    {
        uint8_t num_bits = 32 - __builtin_clz(idx); // 32 bits que uint32_t reserva - qnt de 0 do início até o primeiro bit 1 do índice
        if (num_bits > min_nb_bits)
        {
            min_nb_bits = num_bits;
        }
    }
    return min_nb_bits;
}

void write_file(const std::vector<uint32_t>& indices, const std::string& filename)
{
    uint8_t min_nb_bits = get_nb_bits(indices);

    std::vector<uint8_t> packed_bytes;
    int bits_counter = 0;
    uint8_t current_byte = 0;

    packed_bytes.push_back(min_nb_bits);

    for (uint32_t idx : indices)
    {
        int8_t nb_bits = 32 - __builtin_clz(idx); // 32 bits que uint32_t reserva - qnt de 0 do início até o primeiro bit 1 do índice
        for (int8_t i = min_nb_bits - 1; i >= 0; i--)
        {
            if (i < nb_bits)
            {
                current_byte |= ((idx >> i) & 1);
            }
            bits_counter++;
            if (bits_counter == 8)
            {
                packed_bytes.push_back(current_byte);
                current_byte = 0;
                bits_counter = 0;
            } else
            {
                current_byte <<= 1;
            }
        }
    }

    if (bits_counter > 0)
    {
        current_byte >>= 1;
        current_byte <<= (8 - bits_counter);
        packed_bytes.push_back(current_byte);
    }

    std::string output_filename = parse_filename(filename);

    std::ofstream outfile(output_filename, std::ios::out | std::ios::binary);
    outfile.write(reinterpret_cast<const char*>(&packed_bytes[0]), packed_bytes.size());
    outfile.close();
    
    std::cout << "Saved to '" << output_filename << "'." << std::endl;
}

std::vector<uint32_t> read_file(const std::string& filename)
{
    std::ifstream infile(filename, std::ios::in | std::ios::binary);
    std::vector<uint8_t> packed_bytes((std::istreambuf_iterator<char>(infile)), std::istreambuf_iterator<char>());
    infile.close();

    std::vector<uint32_t> indices;
    int bits_counter = 0;
    uint32_t current_idx = 0;
    uint8_t min_nb_bits = packed_bytes[0];

    size_t s = packed_bytes.size();
    for (size_t i = 1; i < s; i++)
    {
        uint8_t byte = packed_bytes[i];
        for (int8_t i = 7; i >= 0; i--)
        {
            uint32_t current_bit = (byte >> i) & 1;
            current_idx |= current_bit << ((min_nb_bits - 1) - bits_counter);
            bits_counter++;
            if (bits_counter == min_nb_bits)
            {
                indices.push_back(current_idx);
                current_idx = 0;
                bits_counter = 0;
            }
        }
    }
    return indices;
}

int main(int argc, char** argv)
{
    if(argc < 4)
    {
        std::cerr << "Usage:" << std::endl;
        std::cerr << argv[0] << " -w -f filename -i temp_filename" << std::endl;
        std::cerr << argv[0] << " -r -f filename" << std::endl;
        return 1;
    }
    std::string mode = argv[1];
    std::string filename = argv[3];
    std::vector<uint32_t> indices;

    if(mode == "-w")
    {
        std::string temp_filename = argv[5];
        indices = read_indices_from_file(temp_filename);
        write_file(indices, filename);
    }
    else if(mode == "-r")
    {
        indices = read_file(filename);
        for (uint32_t index : indices)
        {
            std::cout << index << " ";
        }
        std::cout << std::endl;
    }

    return 0;
}