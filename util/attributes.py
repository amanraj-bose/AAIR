import tensorflow as tf
import numpy as np
import os, platform

class Train:
    def __init__(self, size:tuple, scale:bool=True, batch:int=32, shuffle:int=50):
        super(Train, self).__init__()
        self.size = size
        self.scale = scale
        self.batch = batch
        self.shuffle = shuffle
    
    def read_img(self, x, y):
        x = tf.io.read_file(x)
        x = tf.io.decode_image(x, 3, expand_animations=False)
        x = tf.image.resize(x, self.size)
        x = tf.cast(x, tf.float32)
        if self.scale:
            x = x/255.

        return x, y
    
    def tensor_slices(self, x):
        return tf.data.Dataset.from_tensor_sliceses(x).map(self.read_img).batch(self.batch).shuffle(self.shuffle)

def path_replacer(x):
    r = ["\\", "/"]
    if platform.system().lower() == "windows":
        y = r[0][0]
        z = r[1]
    else:
        y = r[1]
        z = r[0][0]
    
    return os.path.join(str(x).replace(z, y))