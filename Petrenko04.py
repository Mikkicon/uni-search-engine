from Petrenko01 import write_dictionary
import BTrees


class Gramm3:
    def __init__(self, dictionary_path):
        with open(dictionary_path, "r") as target:
            self.dictionary = target.read().splitlines()

    def word_gramms(self, word):
        grams = []
        word = "$" + word + "$"
        for idx in range(len(word) - 2):
            grams.append(word[idx : idx + 3])
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
        with open(dictionary_path, "r") as target:
            self.dictionary = target.read().splitlines()


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


def task4_main(dictionary_path, dir_path, index_path, shift_index_path):
    # gram = Gramm3(dictionary_path)
    # gramms = gram.dict_to_gramm()
    # write_dictionary(gramms, index_path)

    shift = Shift_idx(dictionary_path)
    # shift.word_shifts("hello")
    shifts = shift.dict_to_shift()
    write_dictionary(shifts, shift_index_path)
