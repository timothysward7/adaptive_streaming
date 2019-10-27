#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hls_video_segmenter.py
#
#
#
import queue as Q
import os
import glob
import argparse
import subprocess
import shlex
import json
import pprint


class Stream(object):
    def __init__(self, w, h, br, fps):
        self.width = w
        self.height = h
        self.bit_rate = br
        self.fps = fps
    
    #def __lt__(self, other):
    #    return self.bit_rate > other.bit_rate

    def __str__(self):
        return ('Resolution: ' + str(self.height) + 'x' + str(self.width) +
                '; bit rate: ' + str(self.bit_rate) + 'k; fps: ' + str(self.fps))


def run_ffmpeg(video_file_loc, streams, extra_params=''):
    """"""
    n_streams = len(streams)
    fps = streams[0].fps 
    extra_param_str = ''
    for token in extra_params:
        extra_param_str += token 
    video_file = video_file_loc.split('/')[len(video_file_loc.split('/'))-1]
    cur_dir_root = video_file_loc.split('/')[0]       
    cmd = 'ffmpeg -i ' + video_file_loc + ' '
    if n_streams > 1:
        tmp_line = '-filter_complex "[v:0]split=' + str(n_streams)
        for i in range(0, n_streams):
            if i < n_streams - 1:
                tmp_line += '[vtemp00' + str(i+1) + ']'
            else:
                tmp_line += '[vout00' + str(i+1) + ']'
        tmp_line += ';'
        for i in range(1, n_streams):
            stream = streams[i]
            tmp = ('[vtemp00' + str(i) + ']scale=w=' + str(stream.height) + 
                                                   ':h=' + str(stream.width) +
                     '[vout00' + str(i) + ']')
            if i < n_streams - 1:
                tmp += ';'
            tmp_line += tmp
        tmp_line += '" '
        cmd += tmp_line  
    cmd += ('-g ' + str(fps) + ' -sc_threshold 0 ' + extra_param_str + ' ')
    stream_index = 0        
    for stream in streams:
        tmp_line = '-map '
        if n_streams == 1:
            tmp_line += 'v:0'
        else: 
            tmp_line += '[vout00' + str(stream_index + 1) + ']'
        tmp_line += ' -c:v:' + str(stream_index) + ' libx264'
        tmp_line += ' -b:v:' + str(stream_index)
        bit_rate = stream.bit_rate
        tmp_line += ' ' + str(bit_rate) + 'k' + ' '
        cmd += tmp_line
        stream_index += 1
    tmp_line = ''    
    for stream in streams:
        tmp_line += '-map a:0 '
    seg_dir = 'seg_files/' + video_file_loc.split('/')[1].split('.')[0]
    tmp_line += ('-c:a aac -b:a 128k -ac 2 ' +
                 '-f hls -hls_time 4 -hls_playlist_type event ' +
                 '-master_pl_name master.m3u8 ' +
                 # TODO: why doesn't folder structure work?
                 #'-hls_segment_filename ' + seg_dir + '/stream_%v/data%06d.ts ' + 
                 #'-use_localtime_mkdir 1 ' + 
                 '-var_stream_map "')
    stream_index = 0
    for stream in streams:
        tmp_line += 'v:' + str(stream_index) + ',a:' + str(stream_index)
        if stream_index < n_streams - 1:
            tmp_line += ' '
        stream_index += 1
    tmp_line += '" '
    tmp_line += seg_dir + '/stream_%v.m3u8'
    cmd += tmp_line
    print("~~~COMMAND~~~")
    print("\"" + cmd + "\"")
    #exit()
    os.system(cmd)

def run_demo():
    """ """
    streams = []
    streams.append(Stream(1920, 1080, 5000, 30))
    if not os.path.exists('seg_files/bbb_sunflower_1080p_30fps_normal'):
        os.system("mkdir seg_files/bbb_sunflower_1080p_30fps_normal")
    elif len(os.listdir('seg_files/bbb_sunflower_1080p_30fps_normal') ) > 0:
        print("Overwriting directory seg_files/bbb_sunflower_1080p_30fps_normal")
        os.system('rm seg_files/bbb_sunflower_1080p_30fps_normal/*')
    run_ffmpeg('videos/bbb_sunflower_1080p_30fps_normal.mp4', streams)
    

def main(args):
    if len(args) > 1:
        print("Not ready for arg input")
        return
    else:
        run_demo()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
