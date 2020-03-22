# По заданій колекції документів побудувати:

# матрицю інцидентності "термін-документ"
# інвертований індекс
# Обгрунтуйте обрані структури збереження даних в розрізі їх ефективності при збільшенні об'ємів даних.

from Petrenko01 import parse_files, get_dictionary_contents, get_files_names
from matrix02 import matrix_main
from util import constants
import re
import json


def task2_main(dictionary_path, dir_path, index_path):
    main(dictionary_path, dir_path, index_path)


def main(dictionary_path, dir_path, index_path):
    slovo = ""
    # matrix_main(dictionary_path, dir_path)
    rebuild_index = input(constants["input_rebuild_index_text"])
    if len(rebuild_index) > 0:
        invert_index(dir_path, index_path)
    user_input = input(constants["input_search_text"])
    while len(user_input) > 0:
        result = bool_search(index_path, user_input)
        result = [int(x) for x in list(result)]
        result.sort()
        if result is not None and len(result):
            print("'", user_input, "' are in files: ", result)
        else:
            print("'", user_input, "' were not found.")
        user_input = input(constants["input_search_text"])


def invert_index(dir_path, index_path):
    merged_lists = []
    files_list = get_files_names(dir_path)
    red_sorted_lists = []
    for file_idx in range(len(files_list)):
        lcl_res = read_file_with_index(files_list[file_idx], file_idx)
        lcl_res.sort()
        red_sorted_lists.append(lcl_res)
    for sorted_list in red_sorted_lists:
        merge_2_list_in_1_list(merged_lists, sorted_list)

    result = merged_list_to_invert_idx(merged_lists)
    with open(index_path, "w") as target:
        target.writelines(result)
    print("Merged")


def read_file_with_index(file_path, file_idx):
    visited = []
    result = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                local_lines = (
                    re.sub(constants["regex_splitter"], "", line).lower().split()
                )
                for word in local_lines:
                    if word not in visited:
                        visited.append(word)
                        result.append((word, file_idx))
    except Exception as e:
        print("Exception ", e, " occured in ", file_path)
    return result


def merge_2_list_in_1_list(merged_list, list2):
    i = j = 0
    while i < len(merged_list) and j < len(list2):
        while i < len(merged_list) and merged_list[i][0] <= list2[j][0]:
            i += 1
        else:
            merged_list.insert(i, list2[j])
            j += 1
            i += 1
    while j < len(list2):
        merged_list.append(list2[j])
        j += 1


def merged_list_to_invert_idx(merged_list):
    invert_index = []
    same_word_counter = 1
    files_where_word_occurs = []
    index = 0
    while index < len(merged_list) - 1:
        files_where_word_occurs.append(str(merged_list[index][1]))
        while merged_list[index][0] == merged_list[index + same_word_counter][0]:
            files_where_word_occurs.append(
                str(merged_list[index + same_word_counter][1])
            )
            same_word_counter += 1
        invert_index.append(
            str(merged_list[index][0])
            + " "
            + str(same_word_counter)
            + " "
            + " ".join(files_where_word_occurs)
            + " "
            + "\n"
        )
        index = index + same_word_counter
        same_word_counter = 1
        files_where_word_occurs.clear()

    return invert_index


def bool_search(index_path, user_input="aaron AND behold"):
    user_input_list = user_input.split(" ")
    state = set()
    current_predicate = ""
    for term in user_input_list:

        if term == "AND" or term == "OR" or term == "NOT":
            current_predicate = term

        elif len(current_predicate) and current_predicate == "AND":
            term_file_list = search_index_for_word(term, index_path)
            if len(term_file_list) < 1:
                pass
            print(term, " : ", term_file_list[1:-1])
            state = state & set(term_file_list[1:-1])
            current_predicate = ""

        elif len(current_predicate) and current_predicate == "OR":
            term_file_list = search_index_for_word(term, index_path)
            if len(term_file_list) < 1:
                pass
            print(term, " : ", term_file_list[1:-1])
            state = state | set(term_file_list[1:-1])
            current_predicate = ""

        elif len(current_predicate) and current_predicate == "NOT":
            term_file_list = search_index_for_word(term, index_path)
            if len(term_file_list) < 1:
                pass
            print(term, " : ", term_file_list[1:-1])
            state -= set(term_file_list[1:-1])
            current_predicate = ""

        else:
            term_file_list = search_index_for_word(term, index_path)
            if len(term_file_list) < 1:
                pass
            print(term, " : ", term_file_list[1:-1])
            state = set(term_file_list[1:-1])
    return state


def search_index_for_word(user_input, index_path):
    with open(index_path, "r") as target:
        for line in target:
            line_items = line.split(" ")
            word = line_items[0]
            if word == user_input.lower():
                return line_items[1:]
    return ""

