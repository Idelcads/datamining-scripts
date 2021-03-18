import os
import sys
import time, yaml

import numpy as np
from init_albumentation import arg_gen, load_arg, load_resize

if __name__=='__main__':

    args = arg_gen()
    name_config_yaml = args.config_downloader
    arg_dataloader = load_arg(name_config_yaml)
    #Resize
    if args.resize:
        new_height, new_width, interpolation = load_resize(arg_dataloader)
        
        if 'albumentation' in os.getcwd():
            print(os.getcwd())
        else:
            os.chdir('albumentation')
            print(os.getcwd())

        cmd = 'python3 main_resize.py --indir ' + args.indir + ' --outdir ' + args.outdir\
            + ' -wi ' + str(new_width) + ' -he ' + str(new_height) + ' -in ' + str(interpolation)
        print(cmd)
        os.system(cmd)
