import random
import cv2
from matplotlib import pyplot as plt
import albumentations as A
import os, re
import argparse
import numpy as np


parser = argparse.ArgumentParser()

"""----------------------------- options-----------------------------"""
parser.add_argument('-wi','--width', type=int,
                help='new width', required=True)
parser.add_argument('-he','--heigth', type=int,
                help='new heigth', required=True)
parser.add_argument('-in','--interpolation', type=int,
                help='interpolation value', required=True)
parser.add_argument('--indir', type=str,
                help='input directory', required=True)
parser.add_argument('--outdir', type=str,
                help='output directory', required=True)
"""----------------------------- bypass the requirements -----------------------------"""
# parser.add_argument('-in','--interpolation', type=int,
#                 help='interpolation value', default=0)
# parser.add_argument('-wi','--width', type=int,
#                 help='new width', default=640)
# parser.add_argument('-he','--heigth', type=int,
#                 help='new heigth', default=480) #640
# parser.add_argument('--indir', type=str,
#                 help='input directory', default="/home/pc/Documents/IMKI/tech.imki.dataset-gen/data/suit/crop/")
# parser.add_argument('--outdir', type=str,
#                 help='output directory', default="/home/pc/Documents/IMKI/tech.imki.dataset-gen/data/suit/crop_resize/")
args = parser.parse_args()

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

def compute_final_size(heigth, width, new_heigth, new_width):
        ratio_heigth = max(new_heigth,heigth)/min(new_heigth,heigth)
        ratio_width = max(new_width,width)/min(new_width,width)
        ind = 0
        if ratio_heigth <= ratio_width:
                final_heigth = new_heigth
                final_width = int((new_heigth/heigth)*width)
                ind = 1
        else:
                final_width = new_width
                final_heigth = int((new_width/width)*heigth) 
                ind = 2
        if final_width > new_width or final_heigth > new_heigth:
                if ind ==1:
                        final_width = new_width
                        final_heigth = int((new_width/width)*heigth) 
                elif ind == 2:
                        final_heigth = new_heigth
                        final_width = int((new_heigth/heigth)*width)
        return final_heigth, final_width


if __name__=='__main__':
        new_heigth, new_width, interpolation = args.heigth, args.width, args.interpolation
        InputPath, OutputPath = args.indir, args.outdir

        filelist = sorted_alphanumeric(os.listdir(InputPath))
        
        for inputImg in filelist[:]: # filelist[:] makes a copy of filelist.
                if not(inputImg.endswith(".png") or inputImg.endswith(".jpg")):
                        filelist.remove(inputImg)
                else:
                        print(inputImg)

                        image = cv2.imread(InputPath + inputImg)
                        heigth, width, channel = image.shape[0], image.shape[1], image.shape[2]
                        new_image = np.zeros((new_heigth,new_width,channel),dtype=np.uint8)
                        final_heigth, final_width = compute_final_size(heigth, width, new_heigth, new_width)
                        os.makedirs(OutputPath, exist_ok=True)

                        transform = A.ReplayCompose([
                                A.Resize (final_heigth, final_width, interpolation=interpolation, always_apply=True)
                                ])
                        transformed = transform(image=image)
                        image_transform = transformed['image']
                        # # Put images on the top left corner
                        # new_image[0:final_heigth, 0:final_width,:] = image_transform[:,:,:]
                        # Put images on the middle of the final image
                        delta_h, delta_w = int((new_heigth - final_heigth)/2), int((new_width - final_width)/2)
                        new_image[delta_h:final_heigth+delta_h, delta_w:final_width+delta_w,:] = image_transform[:,:,:]
                        cv2.imwrite(OutputPath + inputImg, new_image)

