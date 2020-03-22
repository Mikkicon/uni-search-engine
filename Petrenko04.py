from Petrenko01 import write_dictionary
from pytrie import SortedStringTrie as Trie
import re


class Gramm:
    def __init__(self, open_file, gramm_size, dictionary_path):
        self.gramm_size = gramm_size
        if open_file:
            with open(dictionary_path, "r") as target:
                self.dictionary = target.read().splitlines()

    def word_gramms(self, word):
        grams = []
        word = "$" + word + "$"
        for idx in range(len(word) - (self.gramm_size - 1)):
            grams.append(word[idx : idx + self.gramm_size])
        return grams

    def dict_to_gramm(self):
        grams = {}

        for x in self.dictionary:
            x_grams = self.word_gramms(x)
            for y in x_grams:
                if y in grams:
                    if x not in grams[y]:
                        grams[y].append(x)
                else:
                    grams[y] = [x]
        gramms = [k + " " + " ".join(v) for k, v in grams.items()]
        return gramms


class Tree:
    def __init__(self, dictionary_path):
        print("Tree, dict path: ", dictionary_path)
        with open(dictionary_path, "r") as target:
            dictionary = target.read().splitlines()
        self.tree = pytrie.StringTrie(dictionary)


class Shift_idx:
    def __init__(self, dictionary_path):
        with open(dictionary_path, "r") as target:
            self.dictionary = target.read().splitlines()

    def word_shifts(self, word):
        shifts = []
        word = word + "$"
        for idx in range(len(word)):
            shifts.append(word[idx:] + word[:idx])
        return shifts

    def dict_to_shift(self):
        shifts = {}

        for x in self.dictionary:
            x_shifts = self.word_shifts(x)
            shifts[x] = x_shifts
        shifts = [k + " " + " ".join(v) for k, v in shifts.items()]
        return shifts


def find_gramm_words(gramms, index_path):
    gramm_word = dict.fromkeys(gramms)
    with open(index_path) as gramm_idx:
        line = gramm_idx.readline()
        while line:
            tokens = line.split()
            if tokens[0] in gramms:
                gramm_word[tokens[0]] = tokens[1:]
            line = gramm_idx.readline()
    return gramm_word


def fuzzy_word_search(query, gramm_size, gram, index_path):
    opt_query = re.sub("(\*" + ((gramm_size - 1) * "\w") + "\*)", "*", query)
    gramms = list(filter(lambda gram: "*" not in gram, gram.word_gramms(opt_query)))
    matching_words = find_gramm_words(gramms, index_path)
    matching_sets = list(map(frozenset, matching_words.values()))
    result = matching_sets[0].intersection(matching_sets[1])
    for set_idx in range(2, len(matching_sets)):
        result = result.intersection(matching_sets[set_idx])
    return result


def task4_main(dictionary_path, dir_path, index_path, shift_index_path):
    gramm_size = 2
    gram = Gramm(False, gramm_size, dictionary_path)
    # gramms = gram.dict_to_gramm()
    # write_dictionary(gramms, index_path)

    # shift = Shift_idx(dictionary_path)
    # shift.word_shifts("hello")
    # shifts = shift.dict_to_shift()
    # write_dictionary(shifts, shift_index_path)
    query = input("Input a search word with joker...\n")

    while query:
        result = fuzzy_word_search(query, gramm_size, gram, index_path)
        print(result)
        query = input("Input a search word with joker...\n")


if __name__ == "__main__":
    pass
