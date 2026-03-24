from PIL import Image
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
import os

IMAGE_DIR = Path(r"path/to/images")
BBOX_DIR = Path(r"path/to/inference_bbox")
CONFIDENCE_THRESHOLD = 0.4
RECTANGLE_COLOR = (255, 0, 0)
RECTANGLE_THICKNESS = 2
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.9
FONT_THICKNESS = 2


def load_image(filepath):
    try:
        pil_image = Image.open(filepath)
        image = np.array(pil_image)
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    except IOError:
        print(f"Failed to load image: {filepath}")
        return None


def draw_bounding_boxes(image, bbox_file_path):
    num_detections = 0
    with open(bbox_file_path, 'r') as f:
        for line in f:
            cls, x1, y1, x2, y2, conf = line.strip().split()
            if float(conf) < CONFIDENCE_THRESHOLD:
                continue
            x1, y1, x2, y2 = map(int, map(float, [x1, y1, x2, y2]))
            cv2.rectangle(image, (x1, y1), (x2, y2), RECTANGLE_COLOR, RECTANGLE_THICKNESS)
            cv2.putText(image, f"{cls} {float(conf):.2f}", (x1, y1 - 10), FONT, FONT_SCALE, RECTANGLE_COLOR, FONT_THICKNESS)
            num_detections += 1
    return num_detections


def process_images(image_directory, bbox_directory):
    for filepath in image_directory.glob('*.tif'):
        bbox_file_path = bbox_directory / (filepath.stem + '.txt')
        if not bbox_file_path.exists() or os.path.getsize(bbox_file_path) == 0:
            continue

        with open(bbox_file_path, 'r') as f:
            detections_above_threshold = any(float(line.split()[5]) >= CONFIDENCE_THRESHOLD for line in f)

        if not detections_above_threshold:
            continue

        image = load_image(filepath)
        if image is None:
            continue

        num_detections = draw_bounding_boxes(image, bbox_file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(12, 8))
        plt.imshow(image)
        plt.title(f"{filepath.name} - Detections: {num_detections}")
        plt.axis('off')
        plt.show()


process_images(IMAGE_DIR, BBOX_DIR)
