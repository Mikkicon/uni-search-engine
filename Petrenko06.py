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
    print("bytess", bytess)
    print("Binary", list(map(lambda x: format(x, "08b"), bytess)))
    return bytess


def VB_decode(bytestream):
    nums = []
    n = 0
    for idx in range(len(bytestream)):
        if bytestream[idx] < 128:
            n = 128 * n + bytestream[idx]
        else:
            n = 128 * n + (bytestream[idx] - 128)
            nums.append(n)
            n = 0
    return nums


def docIDs2intervals(docIDs):
    pass


def compress(source_path, destination_path):
    pass


# def prefix(binary):
#     offset = 1
#     binary_list = list(binary)
#     size = len(binary_list) // 8

#     print_bytes(binary_list)
#     binary_list.insert(-7, "1")
#     fst_char = binary_list.pop(-9)
#     if fst_char == "1":
#         binary_list = ["0"] * 7 + ["1"] + binary_list
# for byte in range(2, size):
#     binary_list.insert(-7 * byte - offset, "0")
#     offset += 1
# normalize_prefix()
# print("Binary list:")
# print_bytes(binary_list)
# print("Bin list len:", len(binary_list))
# return "".join(binary_list)


if __name__ == "__main__":
    # interval = int(input("Input interval...\n"))
    interval = 214577
    # encode(interval)
    true_vb = "000011010000110010110001"
    print_bytes(true_vb)
    bytestream = VB_encode(interval)
    print("Encoded: ", bytestream)
    print("Decoded: ", VB_decode(bytestream))
