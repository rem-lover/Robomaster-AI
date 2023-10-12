import os
import yaml
import shutil
import random

def main():
    
    # input for the name of the downloaded DJI dataset
    input_path = 'original_first'
    output_path = input_path + '_yolov8'

    # read DJI dataset
    with open(f'{input_path}/obj.names') as read_file:
        names = read_file.read().split('\n')
    
    # create output dir
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        os.mkdir(output_path+'/images')
        os.mkdir(output_path+'/images/train')
        os.mkdir(output_path+'/images/val')
        os.mkdir(output_path+'/images/test')
        os.mkdir(output_path+'/labels')
        os.mkdir(output_path+'/labels/train')
        os.mkdir(output_path+'/labels/val')
        os.mkdir(output_path+'/labels/test')

    # create .yaml file
    data_dict = {
        'path': f'../datasets/{output_path}',
        'train': 'images/train', 
        'val': 'images/val', 
        'test': 'images/test',
        'names': {i:name for i, name in enumerate(names)}
    }
    with open(f'{output_path}/{input_path}.yaml', 'w') as dump_file:
        yaml.dump(data_dict, dump_file)
    
    # sorting
    split_pt1, split_pt2 = 0.7, 0.9
    with open(f'{input_path}/train.txt', 'r') as text:
        raw_text = str(text.read()).split('\n')
        raw_text.pop()
        random.shuffle(raw_text)
        path_list = [i[5:-4] for i in raw_text]
        total_number = len(path_list)

    train_list = path_list[:round(total_number*split_pt1)]
    val_list = path_list[round(total_number*split_pt1):round(total_number*split_pt2)]
    test_list = path_list[round(total_number*split_pt2):]

    for frame_name in train_list:
        source = f'{input_path}/{frame_name}.jpg'
        destination = f'{output_path}/images/train'
        shutil.copy(source, destination)
        source = f'{input_path}/{frame_name}.txt'
        destination = f'{output_path}/labels/train'
        shutil.copy(source, destination)

    for frame_name in val_list:
        source = f'{input_path}/{frame_name}.jpg'
        destination = f'{output_path}/images/val'
        shutil.copy(source, destination)
        source = f'{input_path}/{frame_name}.txt'
        destination = f'{output_path}/labels/val'
        shutil.copy(source, destination)
    
    for frame_name in test_list:
        source = f'{input_path}/{frame_name}.jpg'
        destination = f'{output_path}/images/test'
        shutil.copy(source, destination)
        source = f'{input_path}/{frame_name}.txt'
        destination = f'{output_path}/labels/test'
        shutil.copy(source, destination)



if __name__ == '__main__':
    main()