import musicnn.tagger as tagger
from typing import List
from classes import Track
import numpy as np
import os

def process(track: Track):
    taggram, tags, features = tagger.extractor(track.path)
    penultimate = features['penultimate']
    penultimage_average = np.mean(penultimate, axis=0)
    track.mnn_features = list(penultimage_average.tolist())
    return True
