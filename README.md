# FaceSwap
Swap face between two photos for Python 3 with OpenCV and dlib.

## Swap faces between photos
```sh
python main.py --src imgs/face.jpg --dst imgs/person.jpg --out results/person_with_face.jpg --correct_color
```

### Swap all faces in one photo
```sh
python main.py --src imgs/faces.jpg --out results/people.jpg --correct_color
```

## Install
### Requirements
* `pip3 install -r requirements.txt`

Note: See [requirements.txt](requirements.txt) for more details.

### Git Clone
```sh
git clone https://github.com/wuhuikai/FaceSwap.git
```

### Swap Your Face
```sh
python main.py ...
```
Note: Run **python main.py -h** for more details.

### Real-time camera
```sh
python main_video.py --src_img imgs/test7.jpg --show --correct_color --save_path {*.avi}
```

### Video
```sh
python main_video.py --src_img imgs/test7.jpg --video_path {video_path} --show --correct_color --save_path {*.avi}
```

### Continuously process all files from URL
```sh
python process.py --url http://example.com/images.json
```
