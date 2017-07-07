#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon May 01 05:18:38 2017

@author: zhaoy
"""

import numpy as np
import cv2
import json
import os
import os.path as osp

from fx_image_roi import get_image_roi

# crop settings, set the region of cropped faces
output_square = True
padding_factor = 0.25
do_resize = True
output_size = (224, 224)

roi_scale = 1.0 + padding_factor * 2

landmark_fn = r'../align-faces-by-mtcnn/lfw_mtcnn_falied3_align_rlt.json'
img_root_dir = r'C:/zyf/dataset/lfw'
#webface_src_dir = r'/disk2/data/FACE/LFW/LFW'
aligned_save_dir = img_root_dir + '-aligned-nowarp-224x224'

log_fn1 = 'align_succeeded_list.txt'
log_fn2 = 'align_failed_list.txt'

log_align_params = 'align_params.txt'

fp_in = open(landmark_fn, 'r')
img_list = json.load(fp_in)
fp_in.close()

if not osp.exists(img_root_dir):
    print('ERROR: webface root dir not found!!!')

else:
    if not osp.exists(aligned_save_dir):
        print('mkdir for aligned faces, aligned root dir: ', aligned_save_dir)
        os.makedirs(aligned_save_dir)

    fp_log_params = open(osp.join(aligned_save_dir, log_align_params), 'w')
    params_template = ('output_square = {}\n'
                       'padding_factor = {}\n'
                       'do_resize = {}\n'
                       'output_size = {}\n')

    fp_log_params.write(params_template.format(
            output_square,
            padding_factor,
            do_resize,
            output_size)
    )
    fp_log_params.close()

    fp_log1 = open(osp.join(aligned_save_dir, log_fn1), 'w')
    fp_log2 = open(osp.join(aligned_save_dir, log_fn2), 'w')

    for item in img_list:
        err_msg = ''
        if 'filename' not in item:
            err_msg = "'filename' not in item, break..."
            print(err_msg)
            fp_log2.write(err_msg + '\n')
            break

        img_fn = osp.join(img_root_dir, item['filename'])
        save_fn = osp.join(aligned_save_dir, item['filename'])
        save_fn_dir = osp.dirname(save_fn)

        print('===> Processing image: ' + img_fn)

        if 'faces' not in item:
            err_msg = "'faces' not in item"
            fp_log2.write(item['filename'] + ': ' + err_msg + '\n')
            continue
        elif 'face_count' not in item:
            err_msg = "'face_count' not in item"
            fp_log2.write(item['filename'] + ': ' + err_msg + '\n')
            continue

        if not osp.exists(save_fn_dir):
            os.makedirs(save_fn_dir)

        nfaces = item['face_count']

        if nfaces < 1:
            fp_log2.write(item['filename'] + ': ' + "item['face_count'] < 1" + '\n')
            continue

        if nfaces != len(item['faces']):
            fp_log2.write(item['filename'] + ': ' +
                          "item['face_count'] != len(item['faces']" + '\n')
            continue

        faces = item['faces']
        max_idx = 0

        if nfaces > 1:
            for idx in range(1, nfaces):
                if faces[idx]['score'] > faces[max_idx]['score']:
                    max_idx = idx

        rect = faces[max_idx]['rect']
        roi = [rect[0], rect[1], rect[2]-rect[0], rect[3]-rect[1]]

        try:
            image = cv2.imread(img_fn, True)

            dst_img = get_image_roi(image, roi, roi_scale, output_square)
            if do_resize:
                dst_img = cv2.resize(dst_img, output_size)
            cv2.imwrite(save_fn, dst_img)
        except:
            fp_log2.write(item['filename'] + ': ' +
                          "exception when loading image or aligning faces or saving results" + '\n')
            continue

        fp_log1.write(item['filename'] + ': ' + " succeeded to align" + '\n')

    fp_log1.close()
    fp_log2.close()