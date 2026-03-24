import torch
from ultralytics import YOLO


def run_training():
    print(torch.cuda.device_count())
    print(torch.cuda.get_device_name(0))

    model = YOLO("yolov9c.yaml")

    dataset = r"path/to/dataset.yaml"
    save_dir = 'path/to/save'
    save_name = 'my_training_run'

    results = model.train(
        data=dataset, batch=8, epochs=300, patience=50,
        project=save_dir, name=save_name, dropout=0.25
    )


if __name__ == '__main__':
    run_training()
