import argparse
import os
import platform
import sys
import time, yaml

import numpy as np


def arg_gen():
    parser = argparse.ArgumentParser()

    """----------------------------- options download dataset-----------------------------"""
    parser.add_argument('-cd','--config_downloader', type=str,
                        help='yaml file to use for API downloader', default="config_downloader.yaml")

    """----------------------------- options -----------------------------"""


    # parser.add_argument('--config_downloader', type=str, required=True,
    #                     help='experiment configure file name')
    # parser.add_argument('--checkpoint', type=str, required=True,
    #                     help='checkpoint file name')

    # parser.add_argument('--format', type=str,
    #                     help='save in the format of cmu or coco or openpose, option: coco/cmu/open')
    # parser.add_argument('--posebatch', type=int, default=80,
    #                     help='pose estimation maximum batch size PER GPU')
    # """----------------------------- Video options -----------------------------"""
    # parser.add_argument('--video', dest='video',
    #                     help='video-name', default="")
    # parser.add_argument('--pose_track', dest='pose_track',
    #                     help='track humans in video with reid', action='store_true', default=False)

        # POUR CHINTER LES ARGUMENTS OBLIGATOIRES REPLACE required=True by default="parameter"
    args = parser.parse_args()
    return args

def load_arg(filename):
    a_yaml_file = open(os.path.abspath(os.path.join(os.path.dirname( __file__ ))) + "/configs/" + filename)
    args = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    return args

def path_raw_data(arg_dataloader):
    try:
        InputPath = arg_dataloader['PATH']['DATAPATH']
        Subfolder = arg_dataloader['SPECIES']['LIST']
    except:
        print('\033[91m','DATAPATH or SPECIES is not defined. Please defined them in yaml file','\033[0m')
        sys.exit(1)
    PathRawData = []
    GlobalPath = []
    for i in range(len(Subfolder)):
        for fname in os.listdir(InputPath + Subfolder[i] + '/raw/'):
            if fname.endswith('.png') or fname.endswith('.jpg'):
                PathRawData.append(InputPath + Subfolder[i] + '/raw/')
                GlobalPath.append(InputPath + Subfolder[i] + '/')
                break
    return PathRawData, GlobalPath

def path_resize_data(arg_dataloader):
    try:
        InPath = arg_dataloader['PATH']['DATAPATH']
        Subfolder = arg_dataloader['SPECIES']['LIST']
        ResizePath = arg_dataloader['RESIZE']['PATH']
    except:
        print('\033[91m','DATAPATH, SPECIES or RESIZE PATH is not defined. Please defined them in yaml file','\033[0m')
        sys.exit(1)
    InputPath = []
    OutputPath = []
    for i in range(len(Subfolder)):
        for fname in os.listdir(InPath + Subfolder[i] + '/' + ResizePath + '/'):
            if fname.endswith('.png') or fname.endswith('.jpg'):
                InputPath.append(InPath + Subfolder[i] + '/' + ResizePath + '/')
                OutputPath.append(InPath + Subfolder[i] + '/' + ResizePath + '_resize/')
                break
    return InputPath, OutputPath