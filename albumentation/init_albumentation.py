import argparse
import os
import platform
import sys
import time, yaml

import numpy as np


def arg_gen():
    parser = argparse.ArgumentParser()

    """----------------------------- options----------------------------"""
    parser.add_argument('-cd','--config_downloader', type=str,
                        help='yaml file to use for API downloader', default="config_downloader.yaml")
    parser.add_argument('--indir', type=str,
                        help='input path directory', required=True)
    parser.add_argument('--outdir', type=str,
                        help='output path directory', required=True)
    parser.add_argument('--resize', dest='resize',
                    help='if True apply resize treatment', action='store_true', default=False) ## METTRE FAUX EN DEFAULT

    # parser.add_argument('--indir', type=str,
    #                     help='input path directory', default="/home/pc/Documents/IMKI/tech.imki.dataset-gen/data/suit/crop/") # DELETE
    # parser.add_argument('--outdir', type=str,
    #                     help='output path directory', default="/home/pc/Documents/IMKI/tech.imki.dataset-gen/data/suit/crop_resize/") # DELETE

    args = parser.parse_args()
    return args

def load_arg(filename):
    a_yaml_file = open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'configs')) + "/" + filename)
    args = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    return args

def load_resize(arg_dataloader):
    try:
        new_size = arg_dataloader['RESIZE']['SIZE']
        pos = new_size.find('x')
        new_width = int(new_size[0:pos])
        new_heigth = int(new_size[pos+1:])
    except:
        print('\033[91m','FINAL SIZE FOR RESIZE NOT DETECTED OR NOT IN FORMAT : "100x120"','\033[0m')
        sys.exit(1)
    try:
        # cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_CUBIC, cv2.INTER_AREA, cv2.INTER_LANCZOS4. Value from 0 to 4
        interpolation = arg_dataloader['RESIZE']['INTERPOLATION']
    except:
        print('\033[91m','NO INTERPOLATION PARAMETER DETECTED : Default value is linear interpolation"','\033[0m')
        interpolation = 1
    return new_heigth, new_width, interpolation
