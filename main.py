from Petrenko01 import task1_main
from Petrenko02 import task2_main
from Petrenko03 import task3_main
from Petrenko04 import task4_main
from Petrenko05 import task5_main
from matrix02 import matrix_main
from util import constants


if __name__ == "__main__":
    n = input("For testnet press enter, otherwise - write something...\n")
    paths_keys = [
        "dictionary_path",
        "double_dictionary_path",
        "coordinate_index_path",
        "double_index_path",
        "gramm_index_path",
        "shift_index_path",
        "dir_path",
        "index_path",
    ]
    paths = {}
    if len(n):
        for path in paths_keys:
            paths[path] = "results/" + constants[path]
    else:
        for path in paths_keys:
            paths[path] = "results/" + constants["test_" + path]
    try:
        task_num = int(input("Input the task number..."))
    except Exception as e:
        print("Exception: ", e)
    else:
        if task_num == 1:
            task1_main(paths["dictionary_path"], paths["dir_path"])
        elif task_num == 2:
            task2_main(paths["dictionary_path"], paths["dir_path"], paths["index_path"])
            upd_mtx = input("Should I re-write matrix?\n")
            if len(upd_mtx) > 0:
                matrix_main(paths["dictionary_path"], paths["dir_path"])
        elif task_num == 3:
            task3_main(
                paths["double_dictionary_path"],
                paths["dir_path"],
                paths["coordinate_index_path"],
                paths["double_index_path"],
            )
        elif task_num == 4:
            task4_main(
                paths["dictionary_path"],
                paths["dir_path"],
                paths["gramm_index_path"],
                paths["shift_index_path"],
            )
        elif task_num == 5:
            task5_main(paths["dictionary_path"], paths["dir_path"])

        else:
            print("No such task.")

