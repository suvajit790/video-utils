import cv2
import numpy as np

class crop:
    def init(self, config, **kwargs):
        self.w, self.h, self.x, self.y = config
    
    def execute(self, frames):
        return frames[:, self.y:self.y+self.h, self.x: self.x+self.w]

# text class puts text in a location with certain font size and color
class text:
    def init(self, config, **kwargs):
        self.text = kwargs['txt']
        self.color = (255, 255, 255)
        if len(config) == 3:
            self.pos, self.scale, self.thickness = config
        if len(config) == 4:
            self.pos, self.scale, self.thickness, self.color = config
    
    def execute(self, frames):
        for frame in frames:
            cv2.putText(frame, self.text, self.pos, cv2.FONT_HERSHEY_DUPLEX, self.scale, self.color[::-1], self.thickness, cv2.LINE_AA)
        return frames


class white:
    def init(self, config, **kwargs):
        self.config = config
    def execute(self, frames):
        return np.ones(self.config, dtype=np.int8) * 255
    
class black:
    def init(self, config, **kwargs):
        self.config = config
    def execute(self, frames):
        return np.zeros(self.config, dtype=np.int8)