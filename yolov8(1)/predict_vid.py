from ultralytics import YOLO
import torch
import os

def main():
    # choosing model
    model = YOLO(f'runs\\detect\\train25\\weights\\best.pt')
    torch.cuda.set_device(0)

    # input video
    filename = 'red3'
    video = f'{filename}.mp4'

    for r in model.predict(source=video, stream=True, save=True, save_txt=True):
        pass


if __name__ == '__main__':
    main()
    