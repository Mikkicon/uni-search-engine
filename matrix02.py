from Petrenko01 import parse_files, get_dictionary_contents, get_files_names
from util import constants
import re
import json


def create_matrix_with_size(files_list, dict_len):
    count_files = len(files_list)
    matrix = [[0] * count_files for _ in range(dict_len)]
    return matrix


def is_to_be_added_and_where(word, dictionary, visited):
    for dict_index in range(len(dictionary)):
        if word == dictionary[dict_index] and not (word in visited):
            return True, dict_index
    return False, -1


def build_incident_matrix(matrix, files_list, dictionary):
    if len(files_list) < 1:
        return
    try:
        for file_idx in range(len(files_list) - 1):
            update_matrix_w_file(files_list[file_idx], dictionary, matrix, file_idx)
    except Exception as e:
        print("Exception occured in file " + str(files_list[file_idx]) + ":", e)


def update_matrix_w_file(file_name, dictionary, matrix, file_index):
    print("Update matrx with file ", file_name, " ")
    visited = []
    with open(file_name, "r") as f:
        for line in f:
            local_lines = re.sub(constants["regex_splitter"], "", line).lower().split()
            for word in local_lines:
                is_add, index = is_to_be_added_and_where(word, dictionary, visited)
                if is_add:
                    matrix[index][file_index] = 1
                    visited.append(word)


def matrix_to_json(matrix, dictionary):
    print("Writing matrix ", matrix[:10], "...", end=" ")
    result = {}
    if len(matrix) != len(dictionary):
        return
    for idx in range(len(dictionary)):
        result[dictionary[idx]] = matrix[idx]
    print("json ", result[dictionary[0]], " to file...")
    return result


def write_matrix(dictionary, matrix):
    print("Writing ", dictionary[:10], " to ", constants["matrix_path"])
    proceed = input("Proceed to writing?")
    if len(proceed):
        print('onstants["matrix_path"', constants["matrix_path"])
        with open(constants["matrix_path"], "w") as target:
            json_from_matrix = matrix_to_json(matrix, dictionary)
            # print("json_from_matrix", json_from_matrix)
            json.dump(json_from_matrix, target)


def matrix_main(dictionary_path, dir_path):
    dictionary = get_dictionary_contents(dictionary_path)
    files_list = get_files_names(dir_path)
    matrix = create_matrix_with_size(files_list, len(dictionary))
    build_incident_matrix(matrix, files_list, dictionary)
    write_matrix(dictionary, matrix)

