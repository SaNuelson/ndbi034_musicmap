import argparse
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import numpy as np
from musicnn.extractor import extractor
tf.autograph.set_verbosity(1)

parser = argparse.ArgumentParser()
parser.add_argument("source", nargs=1, type=str, help="Source of the song file to process")
parser.add_argument("features", default=True, type=bool, help="Whether to return a set of features extracted")
parser.add_argument("tags", "taggram", default=True, type=bool, help="Whether to return a set of tags extracted")
parser.add_argument("avg", "average", "averaged", default=True, type=bool, help="Whether to return features averaged over time")

def main(args):
    taggram, tags, features = extractor(args.source, model='MTT_musicnn', input_length=1, input_overlap=None,
                                        extract_features=True)
    outer_features = np.concatenate([features["mean_pool"], features["max_pool"], features["penultimate"]], axis=1)

    if args.features:
        if args.avg:
            print(np.mean(outer_features, 0).tolist())
        else:
            print(outer_features.tolist())

    if args.tags:
        print(features)



if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
