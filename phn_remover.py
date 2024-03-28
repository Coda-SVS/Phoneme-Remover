import copy
import glob
import os
from typing import Dict, List, Literal, Union

ROOT_PATH = os.path.dirname(__file__)
OUTPUT_PATH = os.path.join(ROOT_PATH, "out")


def read_user_options() -> Dict[str, str]:
    options = {
        "phns": "",
        "cat": "",
        "path": "",
    }

    value = input("제거할 음소의 목록을 입력해주세요 (2개 이상일 경우, 공백으로 구분): ")
    value = value.split(" ")
    value = [v.strip() for v in value]
    options["phns"] = value

    while True:
        print()
        value = input(
            (
                "이후 음소에 병합은 'r'\n"
                "이전 음소에 병합은 'm'\n"
                "이전 음소의 기호로 변환은 'e'\n"
                "알맞은 옵션을 입력해주세요: "
            )
        )
        value = value.strip().lower()
        if value in "rme":
            break
        else:
            print("올바르지 않은 값입니다.\n")
    options["cat"] = value

    while True:
        print()
        value = input("파일 또는 폴더의 경로를 입력해주세요: ")
        value = value.strip(" \"'\n\t")
        value = os.path.realpath(value)
        if os.path.exists(value):
            if os.path.isfile(value) and value.endswith(".lab"):
                print("해당 경로는 파일입니다.")
                options["path"] = value
                break
            elif os.path.isdir(value):
                print("해당 경로는 폴더입니다. (하위 경로의 모든 .lab 파일이 수정됩니다.)")
                options["path"] = value
                break
        else:
            print("올바르지 않은 경로입니다.")

    return options


def lab_read(path: str) -> List[Union[int, int, str]]:
    lab = []
    with open(path, "rt", encoding="utf-8") as f:
        buf = f.readlines()
        for line in buf:
            line = line.strip()
            line_segs = line.split(" ")
            start_time = int(line_segs[0])
            end_time = int(line_segs[1])
            phn = " ".join(line_segs[2:]).strip()
            lab.append([start_time, end_time, phn])
    return lab


def lab_write(path: str, lab: List[Union[int, int, str]]):
    lab_text_lines = []
    for line in lab:
        lab_text_lines.append(f"{line[0]} {line[1]} {line[2]}")

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wt", encoding="utf-8") as f:
        f.write("\n".join(lab_text_lines))


def lab_edit(lab: List[Union[int, int, str]], phns: List[str], edit_option: Literal["r", "m", "e"]):
    new_lab = []

    if edit_option == "r":  # 이후 음소에 병합
        prev_target_line = None
        for curr_line in lab:
            if curr_line[2] in phns and prev_target_line is None:
                prev_target_line = curr_line
            else:
                new_line = copy.deepcopy(curr_line)
                if prev_target_line is not None:
                    new_line[0] = prev_target_line[0]
                    prev_target_line = None
                new_lab.append(new_line)

        if prev_target_line is not None:
            print(f"[{prev_target_line[2]}] 이후 음소를 사용할 수 없으므로, 라벨이 제거되었습니다.")

    elif edit_option == "m":  # 이전 음소에 병합
        prev_new_line = None
        for curr_line in lab:
            if curr_line[2] in phns:
                if prev_new_line is None:
                    print(f"[{curr_line[2]}] 이전 음소를 사용할 수 없으므로, 라벨이 제거되었습니다.")
                else:
                    prev_new_line[1] = curr_line[1]
            else:
                new_line = copy.deepcopy(curr_line)
                new_lab.append(new_line)
                prev_new_line = new_line

    elif edit_option == "e":  # 이전 음소의 기호로 변환
        prev_new_line = None
        for curr_line in lab:
            new_line = copy.deepcopy(curr_line)

            if curr_line[2] in phns:
                if prev_new_line is None:
                    print(f"[{curr_line[2]}] 이전 음소를 사용할 수 없으므로, 라벨이 제거되었습니다.")
                else:
                    new_line[2] = prev_new_line[2]
                    new_lab.append(new_line)
            else:
                new_lab.append(new_line)
                prev_new_line = new_line

    return new_lab


def process(fpaths: List[str], dir_name: str, phns: List[str], edit_option: Literal["r", "m", "e"]):
    for fpath in fpaths:
        print(f"작업 중... 경로: [{fpath}]")
        lab = lab_read(fpath)
        if dir_name:
            dpath_tree = fpath.split(dir_name)[1].lstrip(os.path.sep)
            dist_path = os.path.join(OUTPUT_PATH, dpath_tree)
        else:
            dist_path = os.path.join(OUTPUT_PATH, os.path.basename(fpath))
        lab = lab_edit(lab, phns, edit_option)
        lab_write(dist_path, lab)
        print(f"저장됨. 경로: [{dist_path}]")


def main():
    options = read_user_options()
    # options = {
    #     "path": os.path.realpath("test"),
    #     "phns": [""],
    #     "cat": "",
    # }

    path = options["path"]
    target_phonemes = options["phns"]
    concatenate_option = options["cat"]

    if os.path.isdir(path):
        fpaths = glob.glob(os.path.join(glob.escape(path), "*.lab"), recursive=True)
        fpaths += glob.glob(os.path.join(glob.escape(path), "**", "*.lab"), recursive=True)

        directory_name = os.path.basename(path)
        process(fpaths, directory_name, target_phonemes, concatenate_option)
    else:
        process([path], "", target_phonemes, concatenate_option)

    print("done.")


if __name__ == "__main__":
    main()
