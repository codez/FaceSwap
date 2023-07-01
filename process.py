import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.request

ORIGNALS_DIR = ''
SWAPPED_DIR = ''
NO_FACES_DIR = ''
MINSIZE = None
DEBUG = False

def process_images(args):
    sys.stdout.write(".")
    sys.stdout.flush()

    original_files = fetch_local_files(ORIGINALS_DIR)
    no_faces_files = fetch_local_files(NO_FACES_DIR)
    missing_files = fetch_missing_files(args.url, original_files + no_faces_files)

    for file in missing_files:
        download_file(args.url, file)
        count = count_faces(file)
        print(f'{file} has {count} face(s)')
        if count == 0:
            shutil.move(original_path(file), NO_FACES_DIR)
        elif count == 1:
            if len(original_files) > 0:
                swap_other_face(file, random.choice(original_files))
        else:
            swap_file_faces(file)

    if (len(missing_files) > 0):
        write_index()

def fetch_missing_files(url, local_files):
    response = urllib.request.urlopen(url)
    remoteFiles = list(json.loads(response.read().decode()).values())[0]
    return sorted(set(remoteFiles).difference(set(local_files)))

def fetch_local_files(folder):
    return list(filter(lambda file: is_image(folder, file), os.listdir(folder)))

def is_image(folder, file):
    lower = file.lower()
    return os.path.isfile(os.path.join(folder, file)) and \
        (lower.endswith(".jpg") or lower.endswith('.jpeg'))

def download_file(url, file):
    response = urllib.request.urlopen(f'{url}/{file}')
    outFile = open(original_path(file), "wb")
    outFile.write(response.read())

def count_faces(file):
    return int(subprocess.check_output(swap_command(file, ['--count'])))

def swap_other_face(dest, source):
    subprocess.call(swap_command(source, ['--dst', original_path(dest), '--correct_color', '--out', swapped_path(dest)]))

def swap_file_faces(file):
    subprocess.call(swap_command(file, ['--correct_color', '--out', swapped_path(file)]))

def swap_command(source, args):
    command = ['python3', 'main.py', '--src', original_path(source)]
    command.extend(args)
    if MINSIZE is not None:
      command.extend(['--minsize', str(MINSIZE)])
    if DEBUG:
        print(command)
    return command

def write_index():
    file = open(os.path.join(SWAPPED_DIR, 'index.txt'), "w")
    file.write("\n".join(sorted(fetch_local_files(SWAPPED_DIR))))
    file.close()

def original_path(file):
    return os.path.join(ORIGINALS_DIR, file)

def swapped_path(file):
    return os.path.join(SWAPPED_DIR, file)

def mkdir_p(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FaceSwapProcess')
    parser.add_argument('--url', required=True, help='URL where to get images')
    parser.add_argument('--interval', required=False, type=int, default=15, help='Polling interval in seconds')
    parser.add_argument('--minsize', required=False, type=int, help='Minimum size of faces')
    parser.add_argument('--originals',required=False,  default='originals', help='Directory to store original files')
    parser.add_argument('--swapped', required=False, default='swapped', help='Directory to store files with swapped faces')
    parser.add_argument('--no_faces', required=False, default='none', help='Directory to store files without faces')
    parser.add_argument('--debug', required=False, default=False, action='store_true' help='Print more debugging infos')
    args = parser.parse_args()

    ORIGINALS_DIR = args.originals
    SWAPPED_DIR = args.swapped
    NO_FACES_DIR = args.no_faces
    MINSIZE = args.minsize
    DEBUG = args.debug

    mkdir_p(ORIGINALS_DIR)
    mkdir_p(SWAPPED_DIR)
    mkdir_p(NO_FACES_DIR)

    try:
        while True:
            if DEBUG:
                process_images(args)
            else:
                try:
                    process_images(args)
                except Exception as e:
                    print("Error: ", e)

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("interrupted")
        exit()

