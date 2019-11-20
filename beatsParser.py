import os
import sys
import aubio
from aubio import tempo

# Referenced https://salsa.debian.org/piem/aubio/blob/master/python/demos/demo_tempo.py
    # Python-implemented aubio demo on tempo

class Beats(object):
    def __init__(self, song, win_s=512, hop_s=256, samplerate=0):
        # Create source with audio file
        src = aubio.source(song, samplerate, hop_s)

        # Reassign samplerate (so as not to be zero)
        samplerate = src.samplerate

        # Create tempo detection object
        tempoDetection = aubio.tempo('default', win_s, hop_s, samplerate)

        delay = 0 # Tempo detection delay

        self.beats = [] # Track beats of sample
        self.framesToBeats = dict()

        self.totalFrames = 0 # All frames read

        while True:
            samples, read = src()
            beatDetected = tempoDetection(samples)
        #   print('Detecting beats...')
            if (beatDetected):
                currBeat = int(self.totalFrames - delay + beatDetected[0]*hop_s)
                self.beats.append(currBeat/samplerate)
                self.framesToBeats[self.totalFrames] = currBeat
            self.totalFrames += read
            if (read < hop_s):
                break

    def getBeats(self):
        print(self.beats)
        return self.beats
    
    def getFrameBeats(self):
        print(self.framesToBeats)
        return self.framesToBeats
