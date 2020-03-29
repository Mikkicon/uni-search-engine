import Petrenko01
import Petrenko02
import re
import json
from util import constants


class DoubleIndex:
    def __init__(self, double_dictionary_path, dir_path, double_index_path):
        self.dictionary = []
        self.coordinates_dictionary = {}
        self.dictionary_path = double_dictionary_path
        self.index_path = double_index_path
        self.files_list = Petrenko01.get_files_names(dir_path)

    def main(self):
        all_words = self.parse_files_to_dict_return_word_count()
        Petrenko01.write_dictionary(self.dictionary, self.dictionary_path)
        col_size = Petrenko01.get_collection_size(self.files_list)

        print("Collection size: ", col_size)
        print("Dictionary size: ", len(self.dictionary))
        print("Total words: ", all_words)

    # ["file.txt", "file0.txt"]     ->     word_amount
    # populate self.dictionary
    def parse_files_to_dict_return_word_count(self):
        total_words = 0
        for file_idx in range(len(self.files_list)):
            try:
                cur_file = self.files_list[file_idx]
                print(cur_file, " file...")
                total_words += self.double_index_from_file(cur_file)
            except Exception as e:
                print("Exception in parse_files_to_dict_return_word_count: ", e)
        return total_words

    # "file.txt" (foo bar baz ...)  ->   (foo bar
    #                                     bar baz
    #                                     ...)
    def double_index_from_file(self, file):
        total_words = 0
        local_words = []
        with open(file, "r") as o:
            for line in o:
                local_words = (
                    re.sub(constants["regex_splitter"], "", line).lower().split()
                )
                for word_idx in range(len(local_words) - 1):
                    total_words += 1
                    word_pair = local_words[word_idx] + " " + local_words[word_idx + 1]
                    if word_pair not in self.dictionary:
                        self.dictionary.append(word_pair)
        print("Amount of words in " + file + ": ", total_words)
        return total_words


# ======================================================================================================


class CoordIndex:

    # to, 993427:
    # (1, 6: (7, 18, 33, 72, 86, 231);
    # 2, 5: (1, 17, 74, 222, 255);
    # 4, 5: (8, 16, 190, 429, 433);
    # 5, 2: (363, 367);
    # 7, 3: (13, 23, 191); . . .)

    def __init__(self, dir_path, index_path, constants):
        self.dictionary = []
        self.coordinates_dictionary = {}
        self.index_path = index_path
        self.files_list = Petrenko01.get_files_names(dir_path)

    def update_coord_dict(self, word, cur_idx, file_idx, line):

        if word not in self.coordinates_dictionary:
            self.update_coord_dict_new(file_idx, cur_idx, word)
        else:
            self.update_coord_dict_existing(file_idx, cur_idx, word)

    def update_coord_dict_new(self, file_idx, word_idx, word):
        self.coordinates_dictionary[word] = {
            "total": 1,
            "files": {file_idx: {"total_in_file": 1, "indices": [word_idx]}},
        }

    def update_coord_dict_existing(self, file_idx, word_idx, word):
        cur_wrd = self.coordinates_dictionary[word]
        cur_wrd["total"] += 1
        if file_idx not in cur_wrd["files"]:
            cur_wrd["files"][file_idx] = {"total_in_file": 1, "indices": [file_idx]}
        else:
            cur_wrd["files"][file_idx]["total_in_file"] += 1
            cur_wrd["files"][file_idx]["indices"].append(word_idx)

    def read_file_with_coordinate_index(self, file_path, file_idx):
        current_idx = 0
        try:
            with open(file_path, "r") as f:
                line = f.readline()
                lcl_char_idx = 0
                while line:
                    token_list = (
                        re.sub(constants["regex_splitter"], "", line).lower().split()
                    )
                    # print("Line: ", line, " has len: ", len(line))

                    lcl_char_idx = 0
                    for word in token_list:
                        self.update_coord_dict(
                            word, current_idx + lcl_char_idx, file_idx, line
                        )
                        lcl_char_idx += len(word) + 1
                        # print(current_idx + lcl_char_idx)
                    current_idx = f.tell()
                    line = f.readline()
        except Exception as e:
            print("Exception ", e, " occured in ", file_path)

    # і координатний інвертований індекс по колекції документів.

    # to, 993427:
    # (1, 6: (7, 18, 33, 72, 86, 231);
    # 2, 5: (1, 17, 74, 222, 255);
    # 4, 5: (8, 16, 190, 429, 433);
    # 5, 2: (363, 367);
    # 7, 3: (13, 23, 191); . . .)

    def dict_item_to_string(self, key, value):
        string = str(key) + ", " + str(value["total"]) + ": \n"
        string += "("
        for (file_idx, file_info) in value["files"].items():
            string += str(file_idx) + ", "
            string += str(file_info["total_in_file"])
            string += ": (" + ", ".join(list(map(str, file_info["indices"]))) + ");\n"
        string = string[:-1] + ")\n"
        return string

    def coordinates_dict_to_str_list(self):
        str_list = []
        for (key, value) in self.coordinates_dictionary.items():
            str_list.append(self.dict_item_to_string(key, value))
        return str_list

    def invert_index(self):
        merged_lists = []
        red_sorted_lists = []

        for file_idx in range(len(self.files_list)):
            self.read_file_with_coordinate_index(self.files_list[file_idx], file_idx)

        with open(self.index_path, "w") as target:
            json.dump(self.coordinates_dictionary, target)

        # index_list = self.coordinates_dict_to_str_list()
        # with open(self.index_path, "w") as target:
        #     target.writelines(index_list)
        print("Merged")

    def phrasal_search(self, phrase):
        if not len(phrase):
            return
        token_list = re.sub(constants["regex_splitter"], "", phrase).lower().split()
        plausable_files = self.get_token_occurrences(token_list)
        keys = list(plausable_files.keys())
        if len(keys) and len(plausable_files[keys[0]]["indices"]) > 0:

            print(
                "'",
                phrase,
                "' is in files: ",
                keys,
                "\nAnd the text around the first occurence is:",
            )
            for file_key in keys:
                file_key = int(file_key)
                with open(self.files_list[file_key]) as target:
                    result = target.read()
                    try:
                        for index_idx in range(
                            len(plausable_files[keys[file_key]]["indices"])
                        ):
                            phrase_idx = plausable_files[keys[file_key]]["indices"][
                                index_idx
                            ]
                            print(
                                "FILE " + self.files_list[file_key],
                                "INDEX: " + str(phrase_idx),
                                "\n",
                                result[phrase_idx - 50 : phrase_idx + 50],
                                "\n",
                            )
                    except IndexError as er:
                        pass
        else:
            print("'", phrase, "' were not found.")

    def get_token_occurrences(self, token_list):
        with open(self.index_path, "r") as target:
            dictionary = json.load(target)
        occurrences = {}
        for token in token_list:
            if token not in dictionary:
                return {}
            else:
                occurrences[token] = dictionary[token]
        del dictionary
        plausable_files = dict(occurrences[token_list[0]]["files"])
        occurrences.pop(token_list[0])
        prev_token = token_list[0]
        accum_len = len(prev_token)
        for token in occurrences:
            self.filter_following_tokens(
                plausable_files, occurrences[token]["files"], accum_len
            )
            # self.filter_close_tokens(
            #     plausable_files, occurrences[token]["files"], accum_len, 100
            # )
            accum_len += len(token) + 1
        # print(plausable_files)
        return plausable_files

    #       {"0": {"total_in_file": 1, "indices": [6282],
    #       "5": {"total_in_file": 1, "indices": [5]},
    #       +
    #       {"0": {"total_in_file": 1, "indices": [6288]}}}
    #       \/
    #       {"0": {"total_in_file": 1, "indices": [6282]}
    def filter_following_tokens(self, plausable_files, current_files, word_len):
        temp_dict = dict(plausable_files)
        for file in temp_dict:
            if file in current_files:
                self.find_adj_words(
                    plausable_files[file]["indices"],
                    current_files[file]["indices"],
                    word_len,
                )
                if not len(plausable_files[file]["indices"]):
                    del plausable_files[file]
            else:
                plausable_files.pop(file)

    def filter_close_tokens(self, plausable_files, current_files, word_len, radius):
        temp_dict = dict(plausable_files)
        for file in temp_dict:
            if file in current_files:
                self.find_proximity_words(
                    plausable_files[file]["indices"],
                    current_files[file]["indices"],
                    word_len,
                    radius,
                )
                if not len(plausable_files[file]["indices"]):
                    del plausable_files[file]
            else:
                plausable_files.pop(file)

    # In the
    # [6, 23, 543,43],
    # [1, 26, 765] -> 23,26 23+2 = 25 26

    def find_proximity_words(self, indices_list1, indices_list2, word_len, radius):
        i = j = 0
        # Copy data to temp arrays L[] and R[]
        while i < len(indices_list1) and j < len(indices_list2):
            adj_word_dist = indices_list2[j] - (indices_list1[i] + word_len)
            # ["In the", "In, the"]
            # ____/\________/_\___
            if adj_word_dist <= radius and adj_word_dist > 0:
                i += 1
                j += 1
            elif adj_word_dist <= 0:
                indices_list2.pop(j)
            elif adj_word_dist > 2:
                indices_list1.pop(i)

        del indices_list1[i:]
        del indices_list2[j:]
        print("merged indices")

    # In the
    # [6, 23, 543,43],
    # [1, 26, 765] -> 23,26 23+2 = 25 26

    def find_adj_words(self, indices_list1, indices_list2, word_len):
        i = j = 0
        # Copy data to temp arrays L[] and R[]
        while i < len(indices_list1) and j < len(indices_list2):
            adj_word_dist = indices_list2[j] - (indices_list1[i] + word_len)
            # ["In the", "In, the"]
            # ____/\________/_\___
            if adj_word_dist <= 2 and adj_word_dist > 0:
                i += 1
                j += 1
            elif adj_word_dist <= 0:
                indices_list2.pop(j)
            elif adj_word_dist > 2:
                indices_list1.pop(i)

        del indices_list1[i:]
        del indices_list2[j:]
        print("merged indices")


def task3_main(
    double_dictionary_path, dir_path, coordinate_index_path, double_index_path
):
    print(double_dictionary_path, dir_path, coordinate_index_path, double_index_path)
    di = DoubleIndex(double_dictionary_path, dir_path, double_index_path)
    rebuild_d_index = input("Rebuild double index?")
    if len(rebuild_d_index) > 0:
        di.main()
    task3 = CoordIndex(dir_path, coordinate_index_path, constants)
    rebuild_index = input(constants["input_rebuild_index_text"])
    if len(rebuild_index) > 0:
        task3.invert_index()
    phrase = input("Please input phrase to search in Google...\n")
    task3.phrasal_search(phrase)
    # task3.dist_phrasal_search(phrase)
