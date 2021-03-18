## Dataming-scripts

This code hav been developed following my need to generate or compute large dataset for deep-learning applications.\
Parameter must be written in [config file](configs/INSTALL.md)
python main.py -cd config_downloader.yaml 

More info : [docs/INFO.md](docs/INFO.md)

## Installation
### Global: part 1
* cd dataset-gen
* conda create --prefix ./venv -y python=3.6
* conda activate ./venv

* pip install flickrapi
* pip install -U albumentations
* pip install yacs
* conda install -c conda-forge dominate
* conda install scipy scikit-image
* conda install tqdm
* pip install natsort
* pip install opencv-python

### AlphaPose Install: part 2
* git clone https://github.com/MVIG-SJTU/AlphaPose.git \
**follow then the installation instructions provided by AlphaPose: https://github.com/MVIG-SJTU/AlphaPose/blob/master/docs/INSTALL.md** \
\
**don't forget to download model for AlphaPose: [MODEL_ZOO.md](https://github.com/MVIG-SJTU/AlphaPose/blob/master/docs/MODEL_ZOO.md):**
* For Bbox, `Fast Pose (DUC) - Resnet152 - from MSCOCO DATASET`
* For Pose Estimation, `Fast Pose - Resnet50 - from Halpe dataset` both 26 and 136 keypoints

### Global: part 3
Only after downloading Alphapose !
* mv scripts/AlphaPose/init_AlphaPose.py scripts/AlphaPose/main.py AlphaPose
* mv scripts/AlphaPose/scripts/demo_inference_pose_estimation.py scripts/AlphaPose/scripts/demo_inference_bbox_resize.py AlphaPose/scripts
* mv scripts/AlphaPose/alphapose/utils/vis_bbox_resize.py scripts/AlphaPose/alphapose/utils/vis_pose_estimation.py AlphaPose/alphapose/utils
* mv scripts/AlphaPose/alphapose/utils/writer_bbox_resize.py scripts/AlphaPose/alphapose/utils/writer_pose_estimation.py AlphaPose/alphapose/utils
