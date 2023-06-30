#! /usr/bin/env python
import os
import cv2
import argparse
import random

from face_detection import select_face, select_all_faces, face_detection
from face_swap import face_swap

def swap_two_photos(args):
    # Read images
    src_img = cv2.imread(args.src)
    dst_img = cv2.imread(args.dst)

    # Select src face
    src_points, src_shape, src_face = select_face(src_img)
    # Select dst face
    dst_faceBoxes = select_all_faces(dst_img)

    if dst_faceBoxes is None:
        print('Detect 0 Face !!!')
        exit(-1)

    output = dst_img
    for k, dst_face in dst_faceBoxes.items():
        output = face_swap(src_face, dst_face["face"], src_points,
                           dst_face["points"], dst_face["shape"],
                           output, args)

    write_output(output, args)

    ##For debug
    if args.debug_window:
        show_images(dst_img, output)

def swap_one_photo(args):
    # Read images
    src_img = cv2.imread(args.src)

    # Select src faces
    src_faceBoxes = select_all_faces(src_img)

    if src_faceBoxes is None:
        print('Detect 0 Face !!!')
        exit(-1)

    output = src_img
    dst_keys = shuffle_list(list(src_faceBoxes.keys()))
    for k, dst_face in src_faceBoxes.items():
        src_face = src_faceBoxes[dst_keys[k]]
        output = face_swap(src_face["face"], dst_face["face"], src_face["points"],
                           dst_face["points"], dst_face["shape"],
                           output, args)

    write_output(output, args)

    ##For debug
    if args.debug_window:
        show_images(src_img, output)

def count_faces(args):
    # Read image
    src_img = cv2.imread(args.src)

    faces = face_detection(src_img)

    print(len(faces))

def write_output(output, args):
    dir_path = os.path.dirname(args.out)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    cv2.imwrite(args.out, output)

def show_images(src_img, output):
    cv2.imshow("From", src_img)
    cv2.imshow("To", output)
    cv2.waitKey(0)

    cv2.destroyAllWindows()

def shuffle_list(keys):
    result = list(keys)
    random.shuffle(result)
    length = len(result)
    for i in range(length):
        if result[i] == keys[i]:
            return shuffle_list(keys)
    return result

def resize(args):
    src_img = cv2.imread(args.src)
    factor = int(args.resize) / max(src_img.shape)
    output = cv2.resize(src_img, None, fx = factor, fy = factor)
    write_output(output, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='FaceSwapApp')
    parser.add_argument('--src', required=True, help='Path for source image')
    parser.add_argument('--dst', required=False, help='Path for target image')
    parser.add_argument('--out', required=False, help='Path for storing output images')
    parser.add_argument('--count', required=False, action='store_true', help='Count and output number of faces in source image')
    parser.add_argument('--warp_2d', default=False, action='store_true', help='2d or 3d warp')
    parser.add_argument('--correct_color', default=False, action='store_true', help='Correct color')
    parser.add_argument('--resize', required=False, help='Give the maximum dimension to resize to')
    parser.add_argument('--debug_window', default=False, action='store_true', help='Show debug window')
    args = parser.parse_args()

    if args.count:
        count_faces(args)
    elif args.resize:
        resize(args)
    elif args.dst:
        swap_two_photos(args)
    else:
        swap_one_photo(args)
