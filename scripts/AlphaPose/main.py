import os, time, yaml, cv2, sys
from init_AlphaPose import arg_gen, no_to_False
# gen_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

def load_arg(filename):
    a_yaml_file = open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'configs')) + "/" + filename)
    args = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    return args

if __name__=='__main__':
    # load argument for the main using init_flickr.py / arg_gen()
    args_main = arg_gen()
    # load arguments of the yaml file
    name_config_yaml = args_main.config_downloader
    args = load_arg(name_config_yaml)

    ## CAS BBOX EXTRACTION
    if args_main.case == 'BBOX':

        try:
            save_json = args["BBOX"]["JSON"]
            save_prev_images = args["BBOX"]["VIS_PRED"]
            thr_bbox = args["BBOX"]["TRESH"]
            size_bbox = args["BBOX"]["MIN_SIZE"]
        except:
            save_json = 'no'
            save_prev_images = 'no'
            thr_bbox = 0.7
            size_bbox = 20
        save_json = no_to_False(save_json)
        save_prev_images = no_to_False(save_prev_images)

        # On va dans le répertoire de AlphaPose
        if 'AlphaPose' in os.getcwd():
            print(os.getcwd())
        else:
            os.chdir('AlphaPose')
            print(os.getcwd())
        # On check les arguments save_img et save_json
        if save_json and save_prev_images:
            cmd = 'python3 scripts/demo_inference_bbox_resize.py --indir ' + args_main.PathRaw + ' --outdir ' + args_main.PathGlob\
               + ' --save_prev_images --save_json --thr_bbox ' + str(thr_bbox) + ' --size_bbox ' + str(size_bbox)
            print('1')
        elif save_json and not save_prev_images:
            cmd = 'python3 scripts/demo_inference_bbox_resize.py --indir ' + args_main.PathRaw + ' --outdir ' + args_main.PathGlob\
               + ' --save_json --thr_bbox ' + str(thr_bbox) + ' --size_bbox ' + str(size_bbox)
            print('2')
        elif not save_json and save_prev_images:
            cmd = 'python3 scripts/demo_inference_bbox_resize.py --indir ' + args_main.PathRaw + ' --outdir ' + args_main.PathGlob\
               + ' --save_prev_images --thr_bbox ' + str(thr_bbox) + ' --size_bbox ' + str(size_bbox)
            print('3')
        else:
            cmd = 'python3 scripts/demo_inference_bbox_resize.py --indir ' + args_main.PathRaw + ' --outdir ' + args_main.PathGlob\
               + ' --thr_bbox ' + str(thr_bbox) + ' --size_bbox ' + str(size_bbox)
            print('4')
        print(cmd)
        os.system(cmd)

    ## CAS POSE_ESTIMATION
    if args_main.case == 'POSE':
        try:
            InputPath = args_main.PathGlob + args["POSE_ESTIMATION"]["PATH"] + '/'
            if not os.path.exists(InputPath):
                print('\033[91m','PATH don''t exist.','\033[0m')
                sys.exit(1)       
        except:
            print('\033[91m','PATH is not defined in config file. Please defined them in yaml file','\033[0m')
            sys.exit(1)

        try:
            save_rgb = args["POSE_ESTIMATION"]["SAVE"]["RGB"]
            save_black = args["POSE_ESTIMATION"]["SAVE"]["BLACK"]
            save_other = args["POSE_ESTIMATION"]["SAVE"]["OTHER"]
            save_json = args["POSE_ESTIMATION"]["SAVE"]["JSON"]
        except:
            save_rgb = 'yes'
            save_black = 'yes'
            save_other = 'no'
            save_json = 'no'
        if save_other == 'yes':
            try:
                path_other = args["POSE_ESTIMATION"]["SAVE"]["PATH_OTHER"]
                if not os.path.exists(path_other):
                    print('\033[91m','PATH_OTHER don''t exist.','\033[0m')
                    sys.exit(1) 
            except:
                print('\033[91m','PATH_OTHER is not defined in config file. Please defined them in yaml file','\033[0m')
                sys.exit(1)
        try:
            model = args["POSE_ESTIMATION"]["MODEL"]
        except:
            model = 136
        try:
            thickness = args["POSE_ESTIMATION"]["DRAW"]["THICKNESS"]
            thr = args["POSE_ESTIMATION"]["DRAW"]["TRESH"]
            only_one = args["POSE_ESTIMATION"]["DRAW"]["ONLY_ONE"]
        except:
            thickness = 2
            thr = 0.5
            only_one = 'no'

        save_json, save_rgb, save_black, save_other = no_to_False(save_json), no_to_False(save_rgb), no_to_False(save_black), no_to_False(save_other)
        only_one = no_to_False(only_one)

        # On va dans le répertoire de AlphaPose
        if 'AlphaPose' in os.getcwd():
            print(os.getcwd())
        else:
            os.chdir('AlphaPose')
            print(os.getcwd())

        cmd = 'python3 scripts/demo_inference_pose_estimation.py --indir ' + InputPath + ' --outdir ' + args_main.PathGlob\
               + ' --confidence ' + str(thr) + ' --thickness ' + str(thickness) + ' --model ' + str(model)
        if save_rgb:
            cmd = cmd + ' --save_RGB'
        if save_black:
            cmd = cmd + ' --save_black'
        if save_json:
            cmd = cmd + ' --save_json'
        if only_one:
            cmd = cmd + ' --only_one'
        if save_other:
            cmd = cmd + ' --save_other --path_other ' + path_other
        print(cmd)
        os.system(cmd)