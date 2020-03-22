# Написати програму, що по заданій колекції текстових файлів будує словник термінів.

# Текстові файли подаються на вхід в будь-якому форматі.
# Розмір текстових файлів не менше 150 К.
# Кількість текстових файлів не менше 10.

# Словник термінів зберегти на диск.
# Оцінити розмір колекції, загальну кількість слів в колекції та розмір словника.
# В якості структури даних використати масив.

# За бажанням:
# Зробити дві версії в одній в якості структури даних масив, а в іншій використати колекції.
# Випробувати декілька форматів збереження словника
# (серіалізація словника, збереження в текстовий файл і т.д.) і порівняти результати.

import sys
import re
import os
from util import constants


def get_files_names(dir_path):
    onlyfiles = [
        dir_path + "/" + f
        for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f)) and f != ".DS_Store"
    ]
    return onlyfiles


def get_dictionary_contents(dictionary_path):
    if not os.path.exists(dictionary_path):
        with open(dictionary_path, "w") as dictionary:
            return []
    else:
        with open(dictionary_path, "r+") as dictionary:
            return dictionary.read().splitlines()


def parse_files(files_list, dictionary):
    total_words = 0
    for file_idx in range(len(files_list)):
        try:
            print(files_list[file_idx], " file...")
            total_words += index_file_to_dictionary(files_list[file_idx], dictionary)
        except Exception as e:
            print(e)
    return total_words


def index_file_to_dictionary(file, dictionary):
    total_words = 0
    local_lines = []
    with open(file, "r") as o:
        for line in o:
            local_lines = re.sub(constants["regex_splitter"], "", line).lower().split()
            for word in local_lines:
                total_words += 1
                if word not in dictionary:
                    dictionary.append(word)
    print("Amount of words in " + file + ": ", total_words)
    return total_words


def get_collection_size(files_list):
    col_size = 0
    for file in files_list:
        col_size += os.stat(file).st_size
    return col_size


def write_dictionary(dictionary, dictionary_path):
    print("Writing ", dictionary[:3], " to ", dictionary_path)
    proceed = input("Proceed to writing?")
    if len(proceed):
        with open(dictionary_path, "w+") as f:
            f.write("\n".join(dictionary))
    else:
        pass


def task1_main(dictionary_path, dir_path):
    files_list = get_files_names(dir_path)

    # dictionary = get_dictionary_contents(dictionary_path)
    dictionary = []
    result = parse_files(files_list, dictionary)
    write_dictionary(dictionary, dictionary_path)
    col_size = get_collection_size(files_list)

    print("Collection size: ", col_size, "B")
    print("Dictionary size: ", len(dictionary), "words")
    print("Total words: ", result, "amount")
