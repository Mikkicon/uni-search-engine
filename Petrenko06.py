"""
VARAIBLE BYTE ENCODING
"""


def count_bytes(dec):
    n = 0
    while dec != 0:
        dec >>= 8
        n += 1
    return n


def print_bytes(binary):
    size = len(binary) // 8
    if len(binary) % 8:
        size += 1
    reversed_bin = list(reversed(binary))
    result = []
    for byte in range(size):
        result.insert(0, list(reversed(reversed_bin[byte * 8 : (byte + 1) * 8])))
    print(result)


def VB_encode(n):
    bytess = []
    while True:
        bytess.insert(0, n % 128)
        if n < 128:
            break
        n //= 128
    bytess[-1] += 128
    # print("bytess", bytess)
    # print("Binary", list(map(lambda x: format(x, "08b"), bytess)))
    return bytess


def VB_decode(bytestream):
    nums = []
    n = 0
    for idx in range(len(bytestream)):
        if bytestream[idx] < 128:
            n = 128 * n + bytestream[idx]
        else:
            n = 128 * n + (bytestream[idx] - 128)
            nums = n
            n = 0
    return nums


def docIDs_intervals(in_docIDs):
    intervals = []
    docIDs = list(in_docIDs)
    if type(docIDs[0]) == str:
        docIDs = list(map(int, docIDs))
    head = docIDs[0]
    if head > 0:
        intervals.append(head)
    for doc_idx in range(len(docIDs) - 1):
        diff = docIDs[doc_idx + 1] - docIDs[doc_idx]
        intervals.append(diff)
    return intervals


"""
                term_id = int(term_str[0].split()[0])
                file_id = int(term_str[0].split()[1])
                a = (term_id).to_bytes(4, "little")
                b = (file_id).to_bytes(4, "little")
                # print("B", b)
                c = (term_str[1]["frequency"]).to_bytes(4, "little")
                # print("C", b)
                # print("sum", a + b + c)
                file.write(a + b + c)
"""


def compress(
    source_path, destination_path, compress_fn=lambda x: [int(y) for y in x.split()]
):
    source_file = open(source_path, "r")
    destination_file = open(destination_path, "wb")
    line = source_file.readline()
    output = b""
    while line:
        split_line = compress_fn(line)
        try:
            for token in split_line:
                encoded = VB_encode(token)
                for byte in encoded:
                    output += (byte).to_bytes(1, "little")
            print("Output:", output)
        except Exception as e:
            print(e, "in token: ", token)

        destination_file.write(output)
        output = b""
        line = source_file.readline()

    source_file.close()
    destination_file.close()


def decompress(source_path, destination_path):
    source_file = open(source_path, "rb")
    destination_file = open(destination_path, "w")
    byte = source_file.read(1)
    bytestream = []
    while byte:
        num = int.from_bytes(byte, "little")
        while not num & 128:
            bytestream.append(num)
            byte = source_file.read(1)
            num = int.from_bytes(byte, "little")
        bytestream.append(num)
        number = VB_decode(bytestream)
        # print("Decoded:", number)
        destination_file.write(str(number) + " ")
        bytestream = []
        byte = source_file.read(1)

    source_file.close()
    destination_file.close()


def compress_preproc(line):
    term_info = line.split()
    inted = list(map(int, term_info))
    intervals = docIDs_intervals(inted[2:])
    result = inted[:2] + intervals
    return result


if __name__ == "__main__":
    # interval = int(input("Input interval...\n"))
    interval = 214577
    # encode(interval)
    true_vb = "000011010000110010110001"
    print_bytes(true_vb)
    bytestream = VB_encode(interval)
    print("Encoded: ", bytestream)
    print("Decoded: ", VB_decode(bytestream))
    docIDs = "0 1 2 3 4 6 7 9 10 11 12 14 15 16 17 18 19 22 23 25 26 27 28 29 30 32 34 35 36 37 38 40 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 61 62 64 65 66 67 68 69 72 73 74 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 97 98 100 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 118 120 121 122 123 124 125 126 127 128 129 130 132 133 134 135 137 138 139 140 141 142 143 144 145 146 147 148 149 150 151 153 154 156 157 158 159 160 161 162 163 164 165 166 167 169 171 173 5000 6999 214577"
    docIDs = docIDs.split()
    i = docIDs_intervals(docIDs)
    compressed_i = []
    decompressed_i = []
    for x in i:
        compressed_i.extend(VB_encode(x))
    decompressed_i.append(VB_decode(compressed_i))
    source_path = "temp.txt"
    destination_path = "compressed.dat"
    decompressed_path = "decompressed.txt"
    print("Intervals: ", i)
    print("Compressed: ", compressed_i)
    print("Decompressed: ", decompressed_i)
    compress(source_path, destination_path, compress_preproc)
    decompress(destination_path, decompressed_path)
