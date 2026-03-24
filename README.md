# Railway Asset Detection Using YOLOv9 and Drone Imagery

Automated detection of railway infrastructure assets from high-resolution drone imagery using YOLOv9, as described in:

> Robu, C., Cal, F.S., Brás-Geraldes, C., & Gachet, J. (2025). "Automated Railway Asset Management Using YOLOv9 and Drone Imagery." *RIMNI - Revista Internacional de Métodos Numéricos para Cálculo y Diseño en Ingeniería*.

## Overview

This repository contains the complete pipeline for detecting five types of railway assets from aerial drone imagery:

- **Concrete Twin-block Sleepers** — track-embedded reinforced concrete blocks
- **Transponders** — automatic speed control equipment on the track axis
- **Railway Switches** — mechanical components enabling track-to-track transitions
- **Wooden Sleepers** — traditional wooden track support structures
- **Track Clearance Markers** — boundary indicators at track junctions

The system processes 5000×5000 pixel drone images, segments them into 640×640 tiles, and applies YOLOv9c for single-class detection per asset type. The pipeline was deployed on over 30 km of Portuguese railway, detecting more than 150,000 assets with F1 Scores above 0.93 for all classes.

## Repository Structure

```
railway-asset-detection/
├── README.md
├── LICENSE
├── requirements.txt
├── install.bat
├── data_preparation/
│   ├── images_into_640.py        # Tile 5000×5000 images into 640×640
│   ├── rotate_images.py          # Rotation augmentation with bbox recalculation
│   ├── apply_gravel_texture.py   # Background texture replacement
│   └── train_test_split.py       # 70/30 train-validation split
├── training/
│   ├── train.py                  # YOLOv9c model training
│   └── dataset.yaml              # Dataset configuration template
├── inference/
│   ├── test.py                   # Run detection on images or directories
│   └── plot_bboxes.py            # Visualize detections with bounding boxes
└── deployment/
    └── bbox_to_arcgis.py         # Convert detections to ArcGIS shapefiles
```

## Figures

A high-resolution version of the YOLOv9 architecture diagram (Figure 2 in the paper) is available in this repository as [`figures/yolov9_architecture.tiff`](figures/yolov9_architecture.tiff) for readers requiring finer detail than the PDF rendering allows.

## Pipeline

### 1. Image Tiling
```bash
python data_preparation/images_into_640.py
```
Segments large 5000×5000 aerial images into 640×640 tiles using a sliding-window approach with overlap at boundaries.

### 2. Annotation
Tiles are annotated using [CVAT.ai](https://www.cvat.ai/) and exported in YOLO format.

### 3. Data Augmentation
```bash
python data_preparation/rotate_images.py
python data_preparation/apply_gravel_texture.py
```
- **Rotation:** Each tile is rotated in fixed-degree increments (3°–8°) with bounding boxes recalculated via rotation matrix transformation.
- **Background replacement:** Areas outside bounding boxes are replaced with randomly sampled gravel textures from 8 texture images.

### 4. Train/Validation Split
```bash
python data_preparation/train_test_split.py
```
Splits original tiles 70/30 **before** augmentation is applied, preventing data leakage.

### 5. Training
```bash
python training/train.py
```
Fine-tunes YOLOv9c from COCO-pretrained weights. Key configuration: batch size 8, 200–300 epochs with early stopping, SGD optimizer, dropout 0.25.

### 6. Inference
```bash
python inference/test.py
```
Accepts a single image or a directory. Displays detections with bounding boxes and confidence scores.

### 7. Visualization
```bash
python inference/plot_bboxes.py
```
Reads exported bounding box text files and overlays them on the original 5000×5000 images with a configurable confidence threshold.

### 8. GIS Export
```bash
python deployment/bbox_to_arcgis.py
```
Converts bounding box coordinates to georeferenced ArcGIS shapefiles using `.tfw` world files and `.prj` projection files.

## Installation

### Option A: Standard install
```bash
pip install -r requirements.txt
```

### Option B: With CUDA GPU support (recommended)
```bash
install.bat
```
This installs dependencies and configures PyTorch with CUDA 12.1 support for GPU-accelerated training.

### Hardware Used
- GPU: NVIDIA Quadro RTX 4000 (8 GB VRAM)
- System RAM: 128 GB
- Training time: 30–50 hours per asset

## Results

| Asset | Precision | Recall | F1 Score | mAP₅₀₋₉₅ |
|-------|-----------|--------|----------|-----------|
| Concrete Twin-block Sleeper | 0.9972 | 0.9835 | 0.9903 | 0.9800 |
| Transponder | 0.9822 | 0.9787 | 0.9805 | 0.9700 |
| Railway Switch | 0.9643 | 0.9643 | 0.9643 | 0.9500 |
| Wooden Sleeper | 0.9253 | 0.9543 | 0.9396 | 0.9300 |
| Track Clearance Marker | 0.9091 | 0.9524 | 0.9302 | 0.9200 |

Results from field deployment on 30+ km of railway imagery (unseen during training).

## Dataset

The dataset is proprietary to [Infraestruturas de Portugal](https://www.infraestruturasdeportugal.pt/) and cannot be shared publicly. The dataset comprised 2,643 high-resolution 5000×5000 aerial images captured using a Trinity F9 drone across multiple regions of Portugal.

## Citation

```bibtex
@article{robu2025railway,
  title={Automated Railway Asset Management Using YOLOv9 and Drone Imagery},
  author={Robu, Cristian and Cal, Filipe S. and Br{\'a}s-Geraldes, Carlos and Gachet, Jo{\~a}o},
  journal={RIMNI - An International Journal of Numerical Methods for Calculation and Design in Engineering},
  year={2025}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
