import cv2
from ultralytics import YOLO
import torch
import os

def main():
    # choosing model
    model = YOLO('models\\yolov8x-pose-p6.pt')
    torch.cuda.set_device(0)

    for r in model.predict(source='0', stream=True, show=True):
        pass


if __name__ == '__main__':
    main()