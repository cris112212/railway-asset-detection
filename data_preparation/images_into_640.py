import os
import math
from PIL import Image

input_directory = r'path/to/images'
output_directory = r'path/to/images_output'
os.makedirs(output_directory, exist_ok=True)
seg_width, seg_height = 640, 640
tif_files = [f for f in os.listdir(input_directory) if f.endswith('.tif')]

for tif_file in tif_files:
    image_path = os.path.join(input_directory, tif_file)
    large_image = Image.open(image_path)
    img_width, img_height = large_image.size
    num_width_segs = math.ceil(img_width / seg_width)
    num_height_segs = math.ceil(img_height / seg_height)
    image_segments = []

    for i in range(num_height_segs):
        for j in range(num_width_segs):
            left = j * seg_width if (j + 1) * seg_width <= img_width else img_width - seg_width
            upper = i * seg_height if (i + 1) * seg_height <= img_height else img_height - seg_height
            right = left + seg_width
            lower = upper + seg_height
            segment = large_image.crop((left, upper, right, lower))
            image_segments.append(segment)

    for i, segment in enumerate(image_segments):
        filename = f"{os.path.splitext(tif_file)[0]}_segment_{i+1}.tif"
        full_path = os.path.join(output_directory, filename)
        segment.save(full_path, "TIFF")

    print(f"Exported {len(image_segments)} segments for {tif_file}.")

print("Processing complete for all images.")
