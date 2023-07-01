#! /usr/bin/env python
import os
import cv2
import argparse
import random

from face_detection import select_face, select_all_faces, face_detection
from face_swap import face_swap

HEIGHT = 3

def swap_two_photos(args):
    src_img = cv2.imread(args.src)
    dst_img = cv2.imread(args.dst)

    src_face = select_largest_faceBox(select_matching_faces(src_img, args.minsize))
    dst_face = select_largest_faceBox(select_matching_faces(dst_img, args.minsize))

    output = face_swap(src_face["face"], dst_face["face"], src_face["points"],
                       dst_face["points"], dst_face["shape"],
                       dst_img, args)

    write_output(output, args)

    if args.debug_window:
        show_images(dst_img, output)

def swap_one_photo(args):
    src_img = cv2.imread(args.src)
    src_faceBoxes = select_matching_faces(src_img, args.minsize)

    output = src_img
    dst_keys = shuffle_list(len(src_faceBoxes))
    for k, dst_face in enumerate(src_faceBoxes):
        src_face = src_faceBoxes[dst_keys[k]]
        output = face_swap(src_face["face"], dst_face["face"], src_face["points"],
                           dst_face["points"], dst_face["shape"],
                           output, args)
        # output = outline_face(output, dst_face)

    write_output(output, args)

    if args.debug_window:
        show_images(src_img, output)

def select_largest_faceBox(faceBoxes):
    result = faceBoxes[0]
    for face in faceBoxes:
        if face["shape"][HEIGHT] > result["shape"][HEIGHT]:
            result = face
    return result

def select_matching_faces(img, minsize, abort = True):
    faceBoxes = list(select_all_faces(img).values())
    if minsize:
        faceBoxes = list(filter(lambda face: face["shape"][HEIGHT] >= minsize, faceBoxes))

    if abort and len(list(faceBoxes)) == 0:
        print('Detect 0 Face !!!')
        exit(-1)

    return faceBoxes

def count_faces(args):
    src_img = cv2.imread(args.src)
    faces = select_matching_faces(src_img, args.minsize, abort = False)
    print(len(faces))

def outline_face(output, dst_face):
    left_top = (dst_face["shape"][0], dst_face["shape"][1])
    right_bottom =  (dst_face["shape"][0] + dst_face["shape"][2], dst_face["shape"][1] + dst_face["shape"][3])
    color = (255, k * (255 / len(dst_keys)), 0)
    return cv2.rectangle(output, left_top, right_bottom, color, 1)

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

def shuffle_list(count):
    if count == 1:
        return [0]

    result = list(range(count))
    random.shuffle(result)
    for i in range(count):
        if result[i] == i:
            return shuffle_list(count)
    return result

def parse_args():
    parser = argparse.ArgumentParser(description='FaceSwapApp')
    parser.add_argument('--src', required=True, help='Path for source image')
    parser.add_argument('--dst', required=False, help='Path for target image')
    parser.add_argument('--out', required=False, help='Path for storing output images')
    parser.add_argument('--count', required=False, action='store_true', help='Count and output number of faces in source image')
    parser.add_argument('--warp_2d', default=False, action='store_true', help='2d or 3d warp')
    parser.add_argument('--correct_color', default=False, action='store_true', help='Correct color')
    parser.add_argument('--minsize', required=False, type=int, help='Give the minimum height required for a face')
    parser.add_argument('--debug_window', default=False, action='store_true', help='Show debug window')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    if args.count:
        count_faces(args)
    elif args.dst:
        swap_two_photos(args)
    else:
        swap_one_photo(args)
