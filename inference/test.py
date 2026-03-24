from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import os

# Configuration
model_path = "path/to/weights/best.pt"
input_path = "path/to/image_or_directory"

model = YOLO(model_path)

# Get list of images (single file or directory)
if os.path.isdir(input_path):
    image_paths = [os.path.join(input_path, f) for f in os.listdir(input_path)
                   if f.lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg'))]
else:
    image_paths = [input_path]

for image_path in image_paths:
    pred = model(image_path, imgsz=5000)
    boxes = pred[0].boxes.xyxy.tolist()
    classes = pred[0].boxes.cls.tolist()
    conf = pred[0].boxes.conf.tolist()
    names = pred[0].names
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    for (x1, y1, x2, y2), cls, conf_level in zip(boxes, classes, conf):
        if conf_level >= 0.00:
            image = cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            label = f"{names[int(cls)]} {conf_level:.2f}"
            image = cv2.putText(image, label, (int(x1), int(y1-10)),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    plt.figure(figsize=(12, 8))
    plt.imshow(image)
    plt.title(os.path.basename(image_path))
    plt.axis('off')
    plt.show()
