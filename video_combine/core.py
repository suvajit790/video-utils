import sys
import cv2
import numpy as np
from styles import *
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
from math import ceil

def read_video(path):
    frames = []
    vid_capture = cv2.VideoCapture(path)
    if not vid_capture.isOpened():
        print("Error opening the video file")
    else:
        fps = int(vid_capture.get(5))
    frame_count = int(vid_capture.get(7))
    ret = True
    while (ret):
        ret, frame = vid_capture.read()
        if ret == True:
            frames.append(frame)
    vid_capture.release()
    return np.array(frames), fps, frame_count

class videosHandlar:
    def __init__(self, configs_styles, workers, size, fps):
        self.workers = workers if workers > 0 else 1
        self.frame_size = size
        self.fps = fps
        self.video_row_configs = []
        for con_sty in configs_styles:
            if 'sub' in con_sty.keys():
                self.video_row_configs[-1].update(con_sty)
            else:
                self.video_row_configs.append(con_sty)

    def __process_fn(self, row_conf):
        vid_row = videoRow(row_conf)
        row_frames = vid_row.execute(self.fps)
        row_frames_shape = row_frames.shape
        if not row_frames_shape[1:3] == self.frame_size[::-1]:
            frames = np.zeros((row_frames_shape[0], *self.frame_size[::-1], 3), dtype=np.uint8)
            for i, frame in enumerate(row_frames):
                frames[i] = cv2.resize(frame, self.frame_size)
            row_frames = frames
        return row_frames
    
    def __export_thread(self, output):
        with tqdm(total=len(self.video_row_configs), desc='Saving output') as pbar:
            while True:
                video = self.buffer.get()
                for frame in video:
                    output.write(frame)
                self.buffer.task_done()
                pbar.update(1)

    def export(self, path):
        self.buffer = Queue(maxsize=100)
        output = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, self.frame_size)
        ex_thread = Thread(target=self.__export_thread, args=(output,))
        ex_thread.setDaemon(True)
        ex_thread.start()

        with tqdm(total=len(self.video_row_configs), desc='Execute') as pbar:
            with ThreadPoolExecutor(self.workers) as executor:
                for result in executor.map(self.__process_fn, self.video_row_configs):
                    self.buffer.put(result)
                    pbar.update(1)

        self.buffer.join()
        output.release()


class videoRow:
    def __init__(self, configs):
        video_configs = []
        vid_files = configs['video'].split('|')
        vid_styles = configs['video_style'].split('|')
        for i in range(len(vid_files)):
            if 'sub' in configs.keys():
                video_configs.append((vid_files[i].strip(), vid_styles[i].strip(),
                                      (configs['sub'].split('|')[i].strip(),
                                       configs['sub_style'].split('|')[i].strip())))
            else:
                video_configs.append(
                    (vid_files[i].strip(), vid_styles[i].strip(), None))

        self.videos = [video(config) for config in video_configs]
        self.frame_size = ()
        self.fps = 0

    def execute(self, fps):
        with ThreadPoolExecutor() as ex:
            [ex.submit(video.execute()) for video in self.videos]
        return self.__resize(fps)

    def __resize(self, fps):
        max_size = (0, 0, 0)
        max_fps = max_frame_count = 0
        for video in self.videos:
            if video.frame_size[0] > max_size[0]:
                max_size = video.frame_size
            if video.fps > max_fps:
                max_fps = video.fps
            if video.frame_count > max_frame_count:
                max_frame_count = video.frame_count

        if fps > 0:
            max_fps = fps

        with ThreadPoolExecutor() as ex:
            [ex.submit(video.resize, max_size, max_fps, max_frame_count) for video in self.videos]
        
        frames = self.videos[0].frames
        for i in range(1, len(self.videos)):
            frames = np.concatenate(
                (frames, self.videos[i].frames), axis=2)
            self.videos[i-1] = 0
        del self.videos
        
        return frames


class video:
    def __init__(self, configs):
        (self.v_name, sty, sub_conf) = configs
        if len(sty) > 1:
            self.style = style(sty)
        if sub_conf != None:
            self.subtitle = sub(sub_conf)
        self.frames = []
        self.fps = 60
        self.frame_count = 60
        self.frame_size = (0, 0, 3)

    def execute(self):
        if len(self.v_name) > 0:
            self.frames, self.fps, self.frame_count = read_video(self.v_name)
        try:
            self.frames = self.style.execute(self.frames)
        except:
            pass
        self.frame_size = self.frames[0].shape

    def resize(self, target_size, target_fps, target_frame_count):
        if target_size[0] != self.frame_size[0]:
            self.frame_size = (target_size[0],
                ceil(self.frame_size[1]/self.frame_size[0]*target_size[0]), target_size[2])
            frames = np.zeros((self.frames.shape[0], *self.frame_size), dtype=np.uint8)
            for idx, frame in enumerate(self.frames):
                frames[idx] = cv2.resize(frame, self.frame_size[:2][::-1])
            self.frames = frames
        frames = np.zeros(
            (target_frame_count, *self.frame_size), dtype=np.uint8)
        factor = target_fps/self.fps
        count = 0
        for i in range(target_frame_count):
            if count < self.frame_count:
                frames[i] = self.frames[int(count)]
            else:
                frames[i] = self.frames[-1]
            count += 1/factor
        self.fps = target_fps
        self.frame_count = target_frame_count
        self.frames = frames
        self.__put_sub()

    def __put_sub(self):
        try:
            self.frames = self.subtitle.execute(self.frames)
        except Exception as e:
            print('__put_sub()', e)


class sub:
    def __init__(self, configs):
        (self.text, self.sty) = configs
        self.style = style(self.sty, txt=self.text)

    def execute(self, frames):
        self.style.execute(frames)
        return frames


class style:
    def __init__(self, config, **kwargs):
        self.styles = []
        configs = config.split('&')
        for conf in configs:
            sty = conf.split('(')[0].strip()
            style_class = getattr(sys.modules['__main__'], sty)
            style_object = style_class()
            exec('style_object.init('+conf[len(sty):]+', **kwargs)')
            self.styles.append(style_object)

    def execute(self, frames):
        for style in self.styles:
            frames = style.execute(frames)
        return frames
