from download_manager import download_song
from file_manager import getall
from mnn_extractor import process
import os

memory = getall()

track = memory.tracks[0]

download_song(memory, track.id)

print(os.getcwd())
print(os.path.join(os.getcwd(), track.path))
features = process(track)

pass