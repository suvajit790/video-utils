import argparse
from core import *
import time

def tuple_type(strings):
    strings = strings.replace("(", "").replace(")", "")
    mapped_int = map(int, strings.split(","))
    return tuple(mapped_int)


def parse_conf(config_file, style_file, workers, size, fps):
    configs_styles = []
    with open(config_file, 'r') as conf:
        for line in conf.readlines():
            line = line.strip()
            name, value = line.split('-')
            temp_dict = {name.strip() : value.strip()}
            configs_styles.append(temp_dict)
    with open(style_file, 'r') as sty:
        for idx, line in enumerate(sty.readlines()):
            line = line.strip()
            name, value = line.split('-')
            configs_styles[idx][name.strip()+'_style'] = value.strip()

    return videosHandlar(configs_styles, workers, size, fps)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, help = "video config file")
    parser.add_argument("-s", "--style", required=True, help = "video style file")
    parser.add_argument("-o", "--out_path", required=False, default='output.avi', help = "video out path")
    parser.add_argument("-f", "--fps", type=int, required=False, default=0, help = "per video out size")
    parser.add_argument("-w", "--workers", type=int, required=False, default=8, help = "max number of threads to use")
    parser.add_argument("-sz", "--size", type=tuple_type, required=False, default=(0, 0), help = "size of output video frame in (w, h) format")
    
    args = parser.parse_args()

    config_file = args.config
    style_file = args.style
    out_path = args.out_path
    fps = args.fps
    workers = args.workers
    size = args.size
    
    start_time = time.time()
    video_data = parse_conf(config_file, style_file, workers, size, fps)
    video_data.export(out_path)
    end_time = time.time()
    print(f'Execution time {(end_time-start_time)}s')
