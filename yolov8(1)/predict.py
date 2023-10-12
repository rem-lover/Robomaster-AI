from ultralytics import YOLO
import torch
import os
import time


def main():
    # choosing model
    model = YOLO(f'runs\\detect\\train14\\weights\\best.pt')
    torch.cuda.set_device(0)

    # input video -> folder of frames
    filename = 'red3'
    video = f'{filename}.mp4'
    imgntxt = f'outputs\\{filename}\\obj_train_data'
    if not os.path.exists(f'outputs\\{filename}'):
        os.makedirs(imgntxt)
        os.system(f'ffmpeg -i {video} -r 30 -f image2 outputs\\{filename}\\obj_train_data\\frame%06d.png')
    test_list = [f'{imgntxt}\\{i}' for i in os.listdir(imgntxt)]

    # prediction
    batchsize = 400
    results = []
    for i in range(0, round(len(test_list)/batchsize)):
        lower, upper = batchsize*i, batchsize*(i+1)-1
        if upper > len(test_list):
            upper = -1

        batchresults = model.predict(test_list[lower:upper], stream=True)
        for result in batchresults:
            results.append(result)
    

if __name__ == '__main__':
    main()