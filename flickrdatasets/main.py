from flickr import get_urls, sizes
from downloader import download_images
import os, time, yaml, cv2, sys
from init_flickr import arg_gen
# gen_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

def load_arg(filename):
    a_yaml_file = open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'configs')) + "/" + filename)
    args = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    return args

def download(outputPath):
    for specie in all_species:

        print('Getting urls for', specie)
        urls = get_urls(specie, img_per_specie, sizes, api_param)
        print('Downloading images for', specie)
        if outputPath == 'data/':
            path = os.path.join('data', specie, 'raw')
            download_images(urls, path)
        else:
            path = outputPath
            path = path + specie + '/raw'
            download_images(urls, path)
if __name__=='__main__':
    # load argument for the main using init_flickr.py / arg_gen()
    args_main = arg_gen()
    # load arguments of the yaml file
    name_config_yaml = args_main.config_downloader
    args = load_arg(name_config_yaml)
    try:
        outputPath = args["PATH"]["DATAPATH"]
    except:
        outputPath = 'data/'
        print('outputPath is not defined. Images will be stored in ', os.getcwd(),'/', os.path.join('data', 'name_specie', 'raw'))
    try:
        all_species = args['SPECIES']['LIST']
    except: 
        print('\033[91m','no species defined. Please defined them in yaml file','\033[0m')
        sys.exit(1)
    try:
        img_per_specie = args['API_PARAM']['img_per_specie']
    except:
        print('\033[91m','Please defined the number of images to download in the yaml file','\033[0m')
        sys.exit(1)
    try:
        img_size = args['API_SIZES']
    except:
        print('no sizes defined for the images. They will be downloaded in their original sizes')
        img_size = {'MAX_SIZE': 0, 'MIN_SIZE': 0, 'ORIGINAL_SIZE': 'yes'}
    try:
        api_param = args['API_PARAM']
        api_param['KEY']
        api_param['SECRET']
    except:
        print('\033[91m','no key and secret num defined for flickr. Please defined them in yaml file','\033[0m')
        sys.exit(1)
    sizes = sizes(img_size)

    start_time = time.time()
    download(outputPath)
    print('Took', round(time.time() - start_time, 2), 'seconds')
