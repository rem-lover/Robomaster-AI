from ultralytics import YOLO
import torch

def main():
    path = 'C:\\Users\\robomaster\\Documents\\Robomaster_AI\\yolov8'
    model = YOLO('models\\yolov8x.pt')
    torch.cuda.set_device(0)
    results = model.train(data='datasets\\coco\\coco.yaml', epochs=300)


if __name__ == '__main__':
    main()