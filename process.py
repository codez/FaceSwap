import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.request

SOURCE_DIR = ''
ORIGINALS_DIR = ''
SWAPPED_DIR = ''
NO_FACES_DIR = ''
REMOTE_URL = None
MINSIZE = None
DEBUG = False

def check_files():
    sys.stdout.write(".")
    sys.stdout.flush()

    original_files = list_local_files(ORIGINALS_DIR)
    source_files = list_local_files(SOURCE_DIR)

    if REMOTE_URL:
        no_faces_files = list_local_files(NO_FACES_DIR)
        fetch_missing_remote_files(original_files + no_faces_files + source_files)
        source_files = list_local_files(SOURCE_DIR)

    process_source_images(source_files, original_files)

    if (len(source_files) > 0):
        write_index()

def process_source_images(source_files, existing_files):
    for file in source_files:
        file_path = source_path(file)
        count = count_faces(file_path)
        print(f'{file} has {count} face(s)')
        if count == 0:
            shutil.move(file_path, NO_FACES_DIR)
        elif count == 1:
            if len(existing_files) > 0:
                shutil.move(file_path, ORIGINALS_DIR)
                swap_other_face(file, random.choice(existing_files))
        else:
            shutil.move(file_path, ORIGINALS_DIR)
            swap_file_faces(file)

def list_local_files(folder):
    return list(filter(lambda file: is_image(folder, file), os.listdir(folder)))

def is_image(folder, file):
    lower = file.lower()
    return os.path.isfile(os.path.join(folder, file)) and \
        (lower.endswith(".jpg") or lower.endswith('.jpeg'))

def fetch_missing_remote_files(local_files):
    remote_files = list_remote_files()
    missing_files = sorted(set(remote_files).difference(set(local_files)))
    for file in missing_files:
        download_file(file)

def list_remote_files():
    response = urllib.request.urlopen(REMOTE_URL)
    return list(json.loads(response.read().decode()).values())[0]

def download_file(file):
    response = urllib.request.urlopen(f'{REMOTE_URL}/{file}')
    outFile = open(source_path(file), "wb")
    outFile.write(response.read())

def count_faces(file):
    return int(subprocess.check_output(swap_command(file, ['--count'])))

def swap_other_face(dest, source):
    subprocess.call(swap_command(
        original_path(source),
        ['--dst', original_path(dest),
         '--correct_color',
         '--out', swapped_path(dest)]
    ))

def swap_file_faces(file):
    subprocess.call(swap_command(
        original_path(file),
        ['--correct_color',
         '--out', swapped_path(file)]
    ))

def swap_command(source, args):
    command = ['python3', 'main.py', '--src', source]
    command.extend(args)
    if MINSIZE is not None:
      command.extend(['--minsize', str(MINSIZE)])
    if DEBUG:
        print(command)
    return command

def write_index():
    file = open(os.path.join(SWAPPED_DIR, 'index.txt'), "w")
    file.write("\n".join(sorted(list_local_files(SWAPPED_DIR))))
    file.close()

def source_path(file):
    return os.path.join(SOURCE_DIR, file)

def original_path(file):
    return os.path.join(ORIGINALS_DIR, file)

def swapped_path(file):
    return os.path.join(SWAPPED_DIR, file)

def setup_dirs():
    mkdir_p(SOURCE_DIR)
    mkdir_p(ORIGINALS_DIR)
    mkdir_p(SWAPPED_DIR)
    mkdir_p(NO_FACES_DIR)

def mkdir_p(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def parse_args():
    parser = argparse.ArgumentParser(description='FaceSwapProcess')
    parser.add_argument('--url', required=False, help='URL where to get images')
    parser.add_argument('--source', required=False, default='source', help='Folder where to look for new images')
    parser.add_argument('--interval', required=False, type=int, default=30, help='Polling interval in seconds')
    parser.add_argument('--minsize', required=False, type=int, help='Minimum size of faces')
    parser.add_argument('--originals',required=False,  default='originals', help='Directory to store original files')
    parser.add_argument('--swapped', required=False, default='swapped', help='Directory to store files with swapped faces')
    parser.add_argument('--no_faces', required=False, default='none', help='Directory to store files without faces')
    parser.add_argument('--debug', required=False, default=False, action='store_true', help='Print more debugging infos')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    REMOTE_URL = args.url
    SOURCE_DIR = args.source
    ORIGINALS_DIR = args.originals
    SWAPPED_DIR = args.swapped
    NO_FACES_DIR = args.no_faces
    MINSIZE = args.minsize
    DEBUG = args.debug

    setup_dirs()

    try:
        while True:
            if DEBUG:
                check_files()
            else:
                try:
                    check_files()
                except Exception as e:
                    print("Error: ", e)

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("interrupted")
        exit()

