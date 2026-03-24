from PIL import Image
import numpy as np
import os
import random
import shutil


def is_image_processed(image_path, suffix='_processed'):
    """Check if the image has already been processed."""
    base, ext = os.path.splitext(image_path)
    processed_path = f"{base}{suffix}{ext}"
    return os.path.exists(processed_path)


def load_bboxes(txt_file_path):
    """Load bounding boxes from a text file."""
    with open(txt_file_path, 'r') as file:
        bboxes = [list(map(float, line.strip().split())) for line in file.readlines()]
    return [bbox[1:] for bbox in bboxes]


def create_inverted_bbox_mask(image_size, bboxes):
    """Create a mask that is True outside bounding boxes."""
    mask = np.ones((image_size[1], image_size[0]), dtype=bool)
    for bbox in bboxes:
        cx, cy, w, h = bbox
        x1 = int((cx - w / 2) * image_size[0])
        y1 = int((cy - h / 2) * image_size[1])
        x2 = int((cx + w / 2) * image_size[0])
        y2 = int((cy + h / 2) * image_size[1])
        mask[y1:y2, x1:x2] = False
    return mask


def sample_colors_from_texture(texture, num_samples=100):
    """Sample colors from a texture."""
    texture_array = np.array(texture)
    sample_indices = [(random.randint(0, texture.height - 1), random.randint(0, texture.width - 1)) for _ in range(num_samples)]
    return [tuple(texture_array[idx]) for idx in sample_indices]


def apply_color_from_samples(image, mask, gravel_texture_dir):
    """Apply sampled colors from a random texture to the masked areas of the image."""
    gravel_textures = [os.path.join(gravel_texture_dir, f) for f in os.listdir(gravel_texture_dir) if f.endswith('.jpg')]
    if not gravel_textures:
        raise FileNotFoundError("No texture files found in the specified directory.")
    gravel_texture_path = random.choice(gravel_textures)
    gravel_texture = Image.open(gravel_texture_path).convert('RGB')
    color_samples = sample_colors_from_texture(gravel_texture, 1000)

    image_array = np.array(image)
    mask_indices = np.argwhere(mask)
    for idx in mask_indices:
        random_color = random.choice(color_samples)
        if image_array.shape[2] == 4:
            image_array[idx[0], idx[1], :3] = random_color
        else:
            image_array[idx[0], idx[1], :] = random_color
    return Image.fromarray(image_array)


def process_single_image(image_path, bbox_file_path, gravel_texture_dir, base_name):
    if not is_image_processed(image_path):
        bboxes = load_bboxes(bbox_file_path)
        output_bbox_path = os.path.join(os.path.dirname(bbox_file_path), base_name + '_processed.txt')
        image = Image.open(image_path).convert('RGB')
        mask = create_inverted_bbox_mask(image.size, bboxes)
        image_with_texture = apply_color_from_samples(image, mask, gravel_texture_dir)
        output_image_path = image_path.replace('.tif', '_processed.tif')
        image_with_texture.save(output_image_path)
        shutil.copyfile(bbox_file_path, output_bbox_path)
        print(f"Processed and saved: {output_image_path} and {output_bbox_path}")
    else:
        print(f"Skipping already processed file: {image_path}")


image_dir = r"path/to/images/train"
bbox_dir = r"path/to/labels/train"
gravel_texture_dir = r"path/to/gravel"

for filename in os.listdir(image_dir):
    if filename.endswith('.tif'):
        image_path = os.path.join(image_dir, filename)
        base_name = os.path.splitext(filename)[0]
        bbox_file_path = os.path.join(bbox_dir, base_name + '.txt')
        if os.path.exists(bbox_file_path):
            process_single_image(image_path, bbox_file_path, gravel_texture_dir, base_name)
        else:
            print(f"No bounding box file found for {filename}, skipping.")
