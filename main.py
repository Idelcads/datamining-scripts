import os
import sys
import time, yaml

import numpy as np
from init import arg_gen, load_arg, path_raw_data, path_resize_data

if __name__=='__main__':

    args = arg_gen()
    name_config_yaml = args.config_downloader
    arg_dataloader = load_arg(name_config_yaml)
    # DONWLOADER if API and flickr
    if arg_dataloader["API_PARAM"]["NEED"] == 'yes' and arg_dataloader["API_PARAM"]["TYPE"] == 'flickr': # download images on flickr if required
        cmd = 'python flickrdatasets/main.py -cd ' + args.config_downloader
        os.system(cmd)
        # RENAME DATA ?? non car flickr ne retélécharge pas si l'image est déja présente


    # CHECK PATH OF RAW DATA AND IF IT CONTAIN IMAGES
    PathRawData, GlobalPath = path_raw_data(arg_dataloader)
    try:
        PathRawData[0]
        print(PathRawData)
    except:
        print('\033[91m','Raw data path not found','\033[0m')
        sys.exit(1)

    # BBOX EXTRACTION AND RESIZE
    
    #BBOX extract
    if (arg_dataloader["BBOX"]["EXTRACT"] == 'yes'):
        for i in range(len(PathRawData)):
            cmd = 'python AlphaPose/main.py -cd ' + args.config_downloader + ' --PathRaw ' + PathRawData[i] + ' --PathGlob ' + GlobalPath[i] + ' --case BBOX'
            os.system(cmd)

    if (arg_dataloader["RESIZE"]["NEED"] == 'yes'):
        # RESIZE SPECIFIED FOLDER USING ALBUMENTATION
        InputResizePath, OutputResizePath = path_resize_data(arg_dataloader)
        try:
            InputResizePath[0]
            print(InputResizePath)
        except:
            print('\033[91m','Input path for data to resize not found','\033[0m')
            sys.exit(1)
        for i in range(len(InputResizePath)):
            cmd = 'python albumentation/main.py -cd ' + args.config_downloader + ' --indir ' + InputResizePath[i] + ' --outdir ' + OutputResizePath[i] + ' --resize'
            os.system(cmd)

    #POSE ESTIMATION
    if (arg_dataloader["POSE_ESTIMATION"]["NEED"] == 'yes'):
        for i in range(len(PathRawData)):
            cmd = 'python AlphaPose/main.py -cd ' + args.config_downloader + ' --PathRaw ' + PathRawData[i] + ' --PathGlob ' + GlobalPath[i] + ' --case POSE'
            os.system(cmd)
