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

    def __init__(self, block_size, output_path):
        self.block_size = block_size
        self.output_path = output_path

    def parse_block(self, current_file, file_idx):
        try:
            with open(current_file, "r") as f:
                for line in f:
                    local_lines = (
                        re.sub(constants["regex_splitter"], "", line).lower().split()
                    )
                    for word in local_lines:
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

    def comparator(self, x):
        return int(str(x[0].split()[0]) + str(x[0].split()[1]))

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

    def read(self, filename):
        if not self.termid_term:
            self.read_termid_term()
        print(sorted(self.termid_term.items())[:10])
        with open(filename, "rb") as f:
            result = ""
            bytess = f.read(4)
            while bytess:
                term_id = int.from_bytes(bytess, "little")
                bytess = f.read(4)
                doc_id = str(int.from_bytes(bytess, "little"))
                bytess = f.read(4)
                frequency = str(int.from_bytes(bytess, "little"))
                bytess = f.read(4)
                print(self.termid_term[term_id] + " " + doc_id + " " + frequency)

    def merge_blocks(self, output_path, index):
        pass

    def main(self, source_dir):
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
        self.merge_blocks(self.output_path, block_idx)


def task5_main():
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
    b = BSBI(1000000, "./test_result_files")
    user_ipt = input("Read [r] or write [w]?... \n")
    if user_ipt == "r":
        b.read("test_result_files/block0.txt")
    elif user_ipt == "w":
        b.main("./test_files/gutenberg/1/0/0/0")
    else:
        print("Incorrect input")


if __name__ == "__main__":
    task5_main()
