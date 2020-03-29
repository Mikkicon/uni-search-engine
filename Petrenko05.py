from pathlib import Path
from util import constants
import re
import os


class BSBI:
    term_id = 0
    current_size = 0
    block = {}
    termid_term = {}
    term_termid = {}

    def __init__(self, block_size, output_path, merge_path):
        self.block_size = block_size
        self.output_path = output_path
        self.merge_path = merge_path

    def parse_block(self, current_file, file_idx):
        try:
            with open(current_file, "r") as f:
                for line in f:
                    local_lines = (
                        re.sub(constants["regex_splitter"], "", line).lower().split()
                    )
                    for word in local_lines:
                        try:
                            if word not in self.term_termid:
                                self.term_termid[word] = self.term_id
                                self.termid_term[self.term_id] = word
                                block_idx = str(self.term_id) + " " + str(file_idx)
                                self.block[block_idx] = {"frequency": 1}
                                self.term_id += 1
                            else:
                                block_idx = (
                                    str(self.term_termid[word]) + " " + str(file_idx)
                                )
                                if block_idx not in self.block:
                                    self.block[block_idx] = {"frequency": 1}
                                else:
                                    self.block[block_idx]["frequency"] += 1
                        except Exception as e:
                            print("Exception ", e, " occured in ", current_file)

        except Exception as e:
            print("Exception ", e, " occured in ", current_file)

    def comparator(self, x):
        keys = x[0].split()
        # return int(str(keys[0]) + str(keys[1]))
        return (int(keys[0]), int(keys[1]))

    def BSBI_invert(self):
        self.block = sorted(list(self.block.items()), key=self.comparator)

    def write_block(self, block_idx):
        with open(self.output_path + "/block" + str(block_idx) + ".dat", "w+b") as file:
            # for term_str in [
            #     (0, {"key": 12}),
            #     (1, {"key": 3}),
            #     (2, {"key": 43}),
            #     (4, {"key": 0}),
            # ]:
            # print(block)
            for term_str in self.block:
                term_id = int(term_str[0].split()[0])
                file_id = int(term_str[0].split()[1])
                a = (term_id).to_bytes(4, "little")
                b = (file_id).to_bytes(4, "little")
                # print("B", b)
                c = (term_str[1]["frequency"]).to_bytes(4, "little")
                # print("C", b)
                # print("sum", a + b + c)
                file.write(a + b + c)

    def write_block_string(self, block_idx):
        with open(
            self.output_path + "/block_str" + str(block_idx) + ".txt", "w+"
        ) as file:
            for term_str in self.block:
                term_id = int(term_str[0].split()[0])
                file_id = int(term_str[0].split()[1])
                a = (term_id).to_bytes(4, "little")
                b = (file_id).to_bytes(4, "little")
                # print("B", b)
                c = (term_str[1]["frequency"]).to_bytes(4, "little")
                # print("C", b)
                # print("sum", a + b + c)
                file.write(
                    str(term_id)
                    + " "
                    + str(file_id)
                    + " "
                    + str(term_str[1]["frequency"])
                    + "\n"
                )

    def write_termid_term(self):

        input(self.output_path + "/termid_term.txt")
        with open(self.output_path + "/termid_term.txt", "w+") as file:
            result = [str(k) + " " + str(v) + "\n" for k, v in self.termid_term.items()]
            file.writelines(result)

    def read_termid_term(self):
        if self.termid_term:
            return
        with open(self.output_path + "/termid_term.txt", "r") as f:
            for line in f:
                key, value = line.split()
                self.termid_term[int(key)] = value
        print("Red")

    def read(self, filename):
        if not self.termid_term:
            self.read_termid_term()
        print(sorted(self.termid_term.items())[:10])
        try:
            with open(filename, "rb") as f:
                result = ""
                bytess = f.read(12)
                while bytess:
                    (term_id, doc_id, frequency) = self.term_from_bytes(bytess)
                    bytess = f.read(12)
                    print(
                        "{:^20} doc:{:^4} id:{:^4}".format(
                            self.termid_term[term_id], doc_id, frequency
                        )
                    )
                    print("{:30}".format("_" * 40))
        except KeyError as ke:
            print("KeyError Exception:", ke)

    def term_from_bytes(self, bytess):
        term_id = int.from_bytes(bytess[:4], "little")
        doc_id = str(int.from_bytes(bytess[4:8], "little"))
        frequency = str(int.from_bytes(bytess[8:], "little"))
        return (term_id, doc_id, frequency)

    def merge_blocks(self):
        file_paths = [
            x
            for x in Path(self.output_path).rglob("*.dat")
            if self.merge_path not in str(x)
        ]
        # confirm = input("Blocks will be merged to " + dest_path)
        blocks = [open(x, "rb") for x in file_paths]
        out_buffer = []
        dest_file = open(self.merge_path, "w+")
        dest_file.write("")
        counter = 0
        in_buffer = self.fill_buffer(blocks)
        head = min(in_buffer.values(), key=lambda x: x["tuple"][0])["tuple"]
        current_termID = head[0]
        empty_blocks = []
        while in_buffer:

            if current_termID == 0:
                print("Yes")
            if current_termID in [x["tuple"][0] for x in in_buffer.values()]:
                for block_name, val in in_buffer.items():
                    if current_termID == val["tuple"][0]:
                        out_buffer.append(val["tuple"])
                for (buff_key, buff_val), block in zip(in_buffer.items(), blocks):
                    if current_termID == buff_val["tuple"][0]:
                        counter += 1
                        term_bytes = block.read(12)
                        if not term_bytes:
                            empty_blocks.append(buff_key)
                        else:
                            in_buffer[block.name] = {
                                "tuple": self.term_from_bytes(term_bytes),
                                "block": block,
                            }
                for key in empty_blocks:
                    del in_buffer[key]
                empty_blocks = []
            else:
                # [(termID, docID, freq), ...]
                frequency_sum = sum([int(x[2]) for x in out_buffer])
                docIDs = [int(x[1]) for x in out_buffer]
                docIDs.sort()
                output = (
                    str(current_termID)
                    + " "
                    + str(frequency_sum)
                    + " "
                    + " ".join([str(x) for x in docIDs])
                    + "\n"
                )
                dest_file.write(output)
                out_buffer = []
                head = min(in_buffer.values(), key=lambda x: x["tuple"][0])["tuple"]
                current_termID = head[0]
            counter = 0
            print(current_termID)
            print(list(map(lambda x: x["tuple"], in_buffer.values())), "\n")
        dest_file.close()
        for x in blocks:
            x.close()

    def fill_buffer(self, blocks):
        in_buffer = {}
        for block in blocks:
            # in_buffer[block.name] = " ".join(list(map(str(self.term_from_bytes(block.read(12))))))
            in_buffer[block.name] = {
                "tuple": self.term_from_bytes(block.read(12)),
                "block": block,
            }
        return in_buffer

    def main(self, source_dir):
        user_input = input("Re-write existing blocks? [y] \n")
        if user_input.lower() == "y":
            block_idx = 0
            file_idx = 0
            # files = (x for x in Path(".").rglob("*.[tT][xX][tT]"))
            files = [x for x in Path(source_dir).rglob("*.[tT][xX][tT]")]
            total_size = sum([os.stat(x).st_size for x in files])
            self.block_size = total_size // 10
            total_cap = 0

            for x in files:
                if self.current_size >= self.block_size:
                    self.BSBI_invert()
                    self.write_block(block_idx)
                    self.write_block_string(file_idx)
                    self.current_size = 0
                    self.block = {}
                    block_idx += 1
                else:
                    self.parse_block(x, file_idx)
                self.current_size += os.stat(x).st_size
                print(file_idx)
                file_idx += 1
            self.write_termid_term()
        self.merge_blocks()


def task5_main(dictionary_path, dir_path):
    # 1. Формуємо по документам пари “termID-docID”
    #    [ 12 –байтів (4+4+4) записи (термін, документ, частота) ]
    #    накопичуємо їх в пам’яті
    #    поки не буде заповнений блок фіксованого розміру.
    #
    # 2. Блок інвертується і записується на диск:
    #    [ Визначимо Block ~ 10M таких записів ]
    #    Сортуються пари “termID-docID”
    #    Всі пари “termID-docID” з однаковим ідентифікатором termID
    #    формують інвертований список
    #
    # 3. Зливаємо десяти блоків в один великий
    # result = (2147483647).to_bytes(4, "little")
    # print(result)
    # result = int.from_bytes(result, "little")
    # print(result)
    b = BSBI(1000000, "./test_result_files", "merged_blocks.dat")
    user_ipt = input("Read [r] or write [w]?... \n")
    if user_ipt == "r":
        b.read("test_result_files/block0.dat")
    elif user_ipt == "w":
        b.main("./test_files/gutenberg/1/0/0")
    else:
        print("Incorrect input")


if __name__ == "__main__":
    task5_main()
