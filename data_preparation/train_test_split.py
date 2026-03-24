import os
import shutil
from sklearn.model_selection import train_test_split


def move_files(files, src_dir, dst_dir):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    for file in files:
        src_path = os.path.join(src_dir, file)
        if not os.path.exists(src_path):
            continue
        dst_path = os.path.join(dst_dir, file)
        shutil.move(src_path, dst_path)


image_dir = 'path/to/images/train'
bbox_dir = 'path/to/labels/train'
image_val_dir = 'path/to/images/val'
bbox_val_dir = 'path/to/labels/val'

all_images = [os.path.splitext(f)[0] for f in os.listdir(image_dir) if f.endswith('.tif')]
train_images, val_images = train_test_split(all_images, test_size=0.3, random_state=42)

move_files([f + '.tif' for f in val_images], image_dir, image_val_dir)
move_files([f + '.txt' for f in val_images], bbox_dir, bbox_val_dir)

print(f"Training set: {len(train_images)} files.")
print(f"Validation set: {len(val_images)} files.")
