import os
import time
from threading import Thread
from queue import Queue

import cv2
import numpy as np
import torch
import torch.multiprocessing as mp

from alphapose.utils.transforms import get_func_heatmap_to_coord
from alphapose.utils.pPose_nms import pose_nms, write_json

DEFAULT_VIDEO_SAVE_OPT = {
    'savepath': 'examples/res/1.mp4',
    'fourcc': cv2.VideoWriter_fourcc(*'mp4v'),
    'fps': 25,
    'frameSize': (640, 480)
}

EVAL_JOINTS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]


class DataWriter():
    def __init__(self, cfg, opt, save_video=False,
                 video_save_opt=DEFAULT_VIDEO_SAVE_OPT,
                 queueSize=1024):
        self.cfg = cfg
        self.opt = opt
        self.video_save_opt = video_save_opt

        self.eval_joints = EVAL_JOINTS
        self.save_video = save_video
        self.heatmap_to_coord = get_func_heatmap_to_coord(cfg)
        # initialize the queue used to store frames read from
        # the video file
        if opt.sp:
            self.result_queue = Queue(maxsize=queueSize)
        else:
            self.result_queue = mp.Queue(maxsize=queueSize)

        # if opt.save_img:
        #     if not os.path.exists(opt.outputpath + '/vis'):
        #         os.mkdir(opt.outputpath + '/vis')

        if opt.pose_flow:
            from trackers.PoseFlow.poseflow_infer import PoseFlowWrapper
            self.pose_flow_wrapper = PoseFlowWrapper(save_path=os.path.join(opt.outputpath, 'poseflow'))

    def start_worker(self, target):
        if self.opt.sp:
            p = Thread(target=target, args=())
        else:
            p = mp.Process(target=target, args=())
        # p.daemon = True
        p.start()
        return p

    def start(self):
        # start a thread to read pose estimation results per frame
        self.result_worker = self.start_worker(self.update)
        return self

    def update(self):
        final_result = []
        norm_type = self.cfg.LOSS.get('NORM_TYPE', None)
        hm_size = self.cfg.DATA_PRESET.HEATMAP_SIZE
        if self.save_video:
            # initialize the file video stream, adapt ouput video resolution to original video
            stream = cv2.VideoWriter(*[self.video_save_opt[k] for k in ['savepath', 'fourcc', 'fps', 'frameSize']])
            if not stream.isOpened():
                print("Try to use other video encoders...")
                ext = self.video_save_opt['savepath'].split('.')[-1]
                fourcc, _ext = self.recognize_video_ext(ext)
                self.video_save_opt['fourcc'] = fourcc
                self.video_save_opt['savepath'] = self.video_save_opt['savepath'][:-4] + _ext
                stream = cv2.VideoWriter(*[self.video_save_opt[k] for k in ['savepath', 'fourcc', 'fps', 'frameSize']])
            assert stream.isOpened(), 'Cannot open video for writing'
        # keep looping infinitelyd
        while True:
            # ensure the queue is not empty and get item
            (boxes, scores, ids, hm_data, cropped_boxes, orig_img, im_name) = self.wait_and_get(self.result_queue)
            if orig_img is None:
                # if the thread indicator variable is set (img is None), stop the thread
                if self.save_video:
                    stream.release()
                if self.opt.save_json:
                    pathjson = os.path.join(self.opt.outputpath, 'pose_estimation')
                    os.makedirs(pathjson, exist_ok=True)
                    write_json(final_result, pathjson, form=self.opt.format, for_eval=self.opt.eval)
                    print("Results have been written to json.")
                else:
                    print('json file not save. If needeed change --json_file to True')
                return
            # image channel RGB->BGR
            if self.opt.save_RGB:
                orig_img = np.array(orig_img, dtype=np.uint8)[:, :, ::-1] # CAS OU ON DESSINE SUR LE PHOTO D'ORIGINE (DEFAULT)
                # print('CAS OU ON DESSINE LES LABELS SUR L''IMAGE D''ORIGINE')
            if self.opt.save_black:
                black_img = np.array(orig_img, dtype=np.uint8)[:, :, ::-1] # CAS OU ON DESSINE LES LABELS SUR FOND NOIR
                black_img [:,:,:] = [0,0,0] 
                # print('CAS OU ON DESSINE LES LABELS SUR UNE IMAGE FOND NOIR')
            if self.opt.save_other:             # CAS OU ON DESSINE LES LABELS SUR UNE AUTRE IMAGE
                Pathlab = self.opt.path_other 
                other_img = cv2.imread(Pathlab + im_name, cv2.IMREAD_UNCHANGED)
                try:
                    other_img[0]
                except:
                    print('\033[91m','PATH TO OTHER DATA NOT DEFINED OR THE NAME IS DIFFERENT','\033[0m')
                    sys.exit(1)
                # print('CAS OU ON DESSINE LES LABELS SUR UNE IMAGE CHOISIE')

            if boxes is None or len(boxes) == 0:
                if self.opt.save_img or self.save_video or self.opt.vis:
                    if self.opt.save_prev_images:
                        self.write_image(orig_img, im_name, stream=stream if self.save_video else None)
            else:
                assert hm_data.dim() == 4

                if hm_data.size()[1] == 136:
                    self.eval_joints = [*range(0,136)]
                elif hm_data.size()[1] == 26:
                    self.eval_joints = [*range(0,26)]
                pose_coords = []
                pose_scores = []
                for i in range(hm_data.shape[0]):
                    bbox = cropped_boxes[i].tolist()
                    pose_coord, pose_score = self.heatmap_to_coord(hm_data[i][self.eval_joints], bbox, hm_shape=hm_size, norm_type=norm_type)
                    pose_coords.append(torch.from_numpy(pose_coord).unsqueeze(0))
                    pose_scores.append(torch.from_numpy(pose_score).unsqueeze(0))
                preds_img = torch.cat(pose_coords)
                preds_scores = torch.cat(pose_scores)
                if not self.opt.pose_track:
                    boxes, scores, ids, preds_img, preds_scores, pick_ids = \
                        pose_nms(boxes, scores, ids, preds_img, preds_scores, self.opt.min_box_area)

                _result = []
                for k in range(len(scores)):
                    _result.append(
                        {
                            'keypoints':preds_img[k], # if add *2 increase the position for an images two time bigger
                            'kp_score':preds_scores[k],# 
                            'proposal_score': torch.mean(preds_scores[k]) + scores[k] + 1.25 * max(preds_scores[k]),
                            'idx':ids[k],
                            'box':[boxes[k][0], boxes[k][1], boxes[k][2]-boxes[k][0],boxes[k][3]-boxes[k][1]] 
                        }
                    )

                result = {
                    'imgname': im_name,
                    'result': _result
                }


                if self.opt.pose_flow:
                    poseflow_result = self.pose_flow_wrapper.step(orig_img, result)
                    for i in range(len(poseflow_result)):
                        result['result'][i]['idx'] = poseflow_result[i]['idx']

                final_result.append(result)
                if self.opt.save_img or self.save_video or self.opt.vis:
                    if hm_data.size()[1] == 49:
                        from alphapose.utils.vis_pose_estimation import vis_frame_dense as vis_frame
                    elif self.opt.vis_fast:
                        from alphapose.utils.vis_pose_estimation import vis_frame_fast as vis_frame
                    else:
                        from alphapose.utils.vis_pose_estimation import vis_frame, vis_frame_bbox
                        # Never write original image with output with this programm
                    if self.opt.save_RGB:
                        img = vis_frame(orig_img, result, self.opt)
                        cas=1
                        self.write_image(img, im_name, 1, stream=stream if self.save_video else None)
                    if self.opt.save_black:
                        img2 = vis_frame(black_img, result, self.opt)
                        self.write_image(img2, im_name, 2, stream=stream if self.save_video else None)
                    if self.opt.save_other:
                        img3 = vis_frame(other_img, result, self.opt)
                        self.write_image(img3, im_name, 3, stream=stream if self.save_video else None)
                    else:
                        print('predictions drawn on the input image are not saved. If needeed change --save_prev_images to True')
                    # SAVE ALL DETECTED BBOX AS NEW IMAGE
                    # vis_frame_bbox(orig_img, result, self.opt, im_name)


    def write_image(self, img, im_name,cas , stream=None):
        if self.opt.vis:
            cv2.imshow("AlphaPose Demo", img)
            cv2.waitKey(30)
        if self.opt.save_img:
            if cas == 1:
                path = os.path.join(self.opt.outputpath,'pose_estimation' ,'vis_pose_est_RGB')
                os.makedirs(path, exist_ok=True)
                cv2.imwrite(os.path.join(self.opt.outputpath, 'pose_estimation' ,'vis_pose_est_RGB', im_name), img)
            if cas == 2:
                path = os.path.join(self.opt.outputpath, 'pose_estimation' ,'vis_pose_est_black')
                os.makedirs(path, exist_ok=True)
                cv2.imwrite(os.path.join(self.opt.outputpath, 'pose_estimation' ,'vis_pose_est_black', im_name), img)
            if cas == 3:
                path = os.path.join(self.opt.outputpath, 'pose_estimation' ,'vis_pose_est_other')
                os.makedirs(path, exist_ok=True)
                cv2.imwrite(os.path.join(self.opt.outputpath, 'pose_estimation' ,'vis_pose_est_other', im_name), img)
        if self.save_video:
            stream.write(img)

    def wait_and_put(self, queue, item):
        queue.put(item)

    def wait_and_get(self, queue):
        return queue.get()

    def save(self, boxes, scores, ids, hm_data, cropped_boxes, orig_img, im_name):
        # save next frame in the queue
        self.wait_and_put(self.result_queue, (boxes, scores, ids, hm_data, cropped_boxes, orig_img, im_name))

    def running(self):
        # indicate that the thread is still running
        return not self.result_queue.empty()

    def count(self):
        # indicate the remaining images
        return self.result_queue.qsize()

    def stop(self):
        # indicate that the thread should be stopped
        self.save(None, None, None, None, None, None, None)
        self.result_worker.join()

    def terminate(self):
        # directly terminate
        self.result_worker.terminate()

    def clear_queues(self):
        self.clear(self.result_queue)
        
    def clear(self, queue):
        while not queue.empty():
            queue.get()

    def results(self):
        # return final result
        print(self.final_result)
        return self.final_result

    def recognize_video_ext(self, ext=''):
        if ext == 'mp4':
            return cv2.VideoWriter_fourcc(*'mp4v'), '.' + ext
        elif ext == 'avi':
            return cv2.VideoWriter_fourcc(*'XVID'), '.' + ext
        elif ext == 'mov':
            return cv2.VideoWriter_fourcc(*'XVID'), '.' + ext
        else:
            print("Unknow video format {}, will use .mp4 instead of it".format(ext))
            return cv2.VideoWriter_fourcc(*'mp4v'), '.mp4'
