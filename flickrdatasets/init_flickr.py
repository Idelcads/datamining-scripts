import argparse
import os
import platform
import sys
import time

import numpy as np

def arg_gen():
    """----------------------------- options download dataset-----------------------------"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-cd','--config_downloader', type=str,
                        help='yaml file to use for API downloader', default="config_downloader.yaml")
    args = parser.parse_args()
    return args