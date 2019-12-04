import aubio
import sys
import os

# Reference:
# https://aubio.org/manual/latest/py_io.html
# First example - typical loop to read files
# Target value is: Length of song in seconds = (frames) divided by (frames per second)

class AudioObject(object):
    def __init__(self, song, samplerate=44100, hop_size=256):
        self.src = aubio.source(song)
        self.total_frames = 0
        self.hop_size = hop_size

        while True:
            samples, read = self.src()
            self.total_frames += read
            if read < self.hop_size:
                break

        self.lengthInSecs = self.total_frames/self.src.samplerate