import argparse
import os
import platform
import sys
import time, yaml

import numpy as np


def arg_gen():
    parser = argparse.ArgumentParser()

    """----------------------------- options-----------------------------"""
    parser.add_argument('-cd','--config_downloader', type=str,
                        help='yaml file to use for API downloader', default="config_downloader.yaml")
    parser.add_argument('--case', type=str,
                        help='How to use AlphaPose', required=True) # Possible BBOX, POSE
    # parser.add_argument('--case', type=str,
    #                     help='How to use AlphaPose', default='POSE') # Possible BBOX, POSE
    parser.add_argument('--PathRaw', type=str,
                        help='Path to raw data', required=True)
    parser.add_argument('--PathGlob', type=str,
                        help='Path to global folder', required=True)
    # parser.add_argument('--PathRaw', type=str,
    #                     help='Path to raw data', default="/home/pc/Documents/IMKI/tech.imki.dataset-gen/data/soccer/raw/")
    # parser.add_argument('--PathGlob', type=str,
    #                     help='Path to global folder', default="/home/pc/Documents/IMKI/tech.imki.dataset-gen/data/soccer/")
    parser.add_argument('--size_bbox', type=int,
                        help='condition on the minimal size of the bbox (percentage)', default=20)

    args = parser.parse_args()
    return args

def load_arg(filename):
    a_yaml_file = open(os.path.abspath(os.path.join(os.path.dirname( __file__ ))) + "/configs/" + filename)
    args = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    return args

def no_to_False(input):
    if input =='no':
        value = False
    else:
        value = True
    return value
