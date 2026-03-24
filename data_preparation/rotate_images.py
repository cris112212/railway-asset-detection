import math
from PIL import Image
import numpy as np
import os


def rotate_point(cx, cy, angle, px, py):
    """Rotate a point around a given center."""
    s, c = math.sin(angle), math.cos(angle)
    px -= cx
    py -= cy
    xnew = px * c - py * s
    ynew = px * s + py * c
    return xnew + cx, ynew + cy


def get_rotated_image_size(w, h, angle):
    """Calculate the size of the image after rotation and expansion."""
    radians = math.radians(angle)
    sin_angle = abs(math.sin(radians))
    cos_angle = abs(math.cos(radians))
    new_w = int(h * sin_angle + w * cos_angle)
    new_h = int(h * cos_angle + w * sin_angle)
    return new_w, new_h


def rotate_bbox(bbox, angle, original_size):
    """Rotates the bounding box coordinates."""
    cx, cy, w, h = bbox
    angle_rad = math.radians(angle)
    points = np.array([
        [cx - w / 2, cy - h / 2],
        [cx + w / 2, cy - h / 2],
        [cx + w / 2, cy + h / 2],
        [cx - w / 2, cy + h / 2]
    ])
    center = original_size / 2
    new_points = np.array([rotate_point(center, center, angle_rad, *point) for point in points])
    min_x, min_y = new_points.min(axis=0)
    max_x, max_y = new_points.max(axis=0)
    new_w = max_x - min_x
    new_h = max_y - min_y
    new_cx = min_x + new_w / 2
    new_cy = min_y + new_h / 2
    return new_cx, new_cy, new_w, new_h


def save_rotated_images_bboxes(image_path, bboxes, image_output_folder, bbox_output_folder, step):
    image = Image.open(image_path)
    original_image_name = os.path.splitext(os.path.basename(image_path))[0]
    original_w, original_h = image.size

    for angle in range(0, 360, step):
        new_img_w, new_img_h = get_rotated_image_size(original_w, original_h, angle)
        rotated_image = image.rotate(angle, expand=True)
        rotated_image_resized = rotated_image.resize((640, 640))
        rotated_image_path = os.path.join(image_output_folder, f"{original_image_name}_rotated_{angle}.tif")
        rotated_image_resized.save(rotated_image_path, format='TIFF')

        if not bboxes:
            continue

        offset_x = (new_img_w - original_w) / 2
        offset_y = (new_img_h - original_h) / 2
        bbox_file_path = os.path.join(bbox_output_folder, f"{original_image_name}_rotated_{angle}.txt")
        with open(bbox_file_path, 'w') as file:
            for bbox in bboxes:
                class_id, cx, cy, w, h = bbox
                cx, cy, w, h = cx * original_w, cy * original_h, w * original_w, h * original_h
                new_cx, new_cy, new_w, new_h = rotate_bbox((cx, cy, w, h), -angle, original_w)
                new_cx += offset_x
                new_cy += offset_y
                x1, y1 = new_cx - new_w / 2, new_cy - new_h / 2
                x2, y2 = new_cx + new_w / 2, new_cy + new_h / 2
                w = x2 - x1
                h = y2 - y1
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                file.write(f"{int(class_id)} {cx/new_img_w} {cy/new_img_h} {w/new_img_w} {h/new_img_h}\n")


def read_bboxes_from_file(file_path):
    with open(file_path, 'r') as file:
        bboxes = [list(map(float, line.strip().split())) for line in file]
    return bboxes


angle = 10

base_dir = r"path/to/base"
image_input_folder = os.path.join(base_dir, 'images/train/')
bbox_input_folder = os.path.join(base_dir, 'labels/train/')
image_output_folder = os.path.join(base_dir, 'rotated/images/train/')
bbox_output_folder = os.path.join(base_dir, 'rotated/labels/train/')

os.makedirs(image_output_folder, exist_ok=True)
os.makedirs(bbox_output_folder, exist_ok=True)

for filename in os.listdir(image_input_folder):
    if filename.endswith('.tif'):
        image_path = os.path.join(image_input_folder, filename)
        bbox_file_path = os.path.join(bbox_input_folder, os.path.splitext(filename)[0] + '.txt')
        bboxes = []
        if os.path.exists(bbox_file_path):
            bboxes = read_bboxes_from_file(bbox_file_path)
        save_rotated_images_bboxes(image_path, bboxes, image_output_folder, bbox_output_folder, angle)
    else:
        print(f"Skipping {filename}, not a .tif file.")
