import shutil
import os
import hashlib
from pathlib import Path

BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)

    return hasher.hexdigest()


def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes


def determine_actions(src_hashes, dst_hashes, src_folder, dst_folder):
    for sha, filename in src_hashes.items():
        # 파일이 없으면 원본 파일을 복사
        if sha not in dst_hashes:
            sorcepath = Path(src_folder) / filename
            destpath = Path(dst_folder) / filename
            yield ("copy", sorcepath, destpath)
        # 파일명이 다르면 파일이름을 변경(이동으로)
        elif dst_hashes[sha] != filename:
            olddestpath = Path(dst_folder) / dst_hashes[sha]
            newdestpath = Path(dst_folder) / filename
            yield ("move", olddestpath, newdestpath)

    # 대상 폴더에 있는 파일이 원본에 없으면 삭제
    for sha, filename in dst_hashes.items():
        if sha not in src_hashes:
            yield ("delete", Path(dst_folder) / filename)


def sync(source, dest):
    # 명령형 셀 1달계 : 입력 수집
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # 명령형 셀 2단계 : 함수형 핵 호출
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # 명령형 셀 3단계 : 출력
    for action, *paths in actions:
        if action == "copy":
            shutil.copyfile(*paths)
        elif action == "move":
            shutil.move(*paths)
        elif action == "delete":
            os.remove(paths[0])
