import os
import sys
import aubio

# Reference: https://github.com/aubio/aubio/blob/master/python/demos/demo_pitch.py

downsample = 1 # Downsampling reduces sampling rate if needed
    # In this case, not reduced (1)
samplerate = 44100 // downsample
win_s = 2048 // downsample
hop_s = 512 // downsample

class PitchPath(object):
    def __init__(self, fileName, samplerate=44100, hop_s=512):
        # Create source object from audio file
        self.src = aubio.source(fileName, samplerate, hop_s)
        # Reassign samplerate (non-zero)
        self.samplerate = self.src.samplerate

        tolerance = 0.1 # Threshold

        pitch_obj = aubio.pitch('yin', win_s, hop_s, self.samplerate)
            # YIN: algorithm for pitch detection
            # "A fundamental frequency estimator for speech and music"
        pitch_obj.set_unit('Hz')
            # Setting unit of pitch to Hz
        pitch_obj.set_tolerance(tolerance)
            # Setting tolerance of pitch confidence

        # Track pitches as found
            # Pitches are measured in frequencies
            # Each input frame is analyzed to identify fundamental frequency
        self.pitches = dict()
        # Track confidence for each
            # Pitch with confidence lower than tolerance (0.9) not considered
            # Reference:
            # https://buildmedia.readthedocs.org/media/pdf/aubio/latest/aubio.pdf
        self.confidences = []
        self.values = []
        self.totalFrames = 0 # Frames read

        while True:
            samples, read = self.src()
            pitch = pitch_obj(samples)[0] # First pitch
            confidence = pitch_obj.get_confidence()

            if (pitch >= 0 and pitch <= 2000): # Reasonable range of pitches audible to human ear

                self.pitches[self.totalFrames/self.samplerate] = pitch
                self.values.append(pitch)
                self.confidences.append(confidence)

            self.totalFrames += read
            
            if read < hop_s: break
        self.uniqueVals = set(self.values)
    
    def getPitchPath(self):
        return self.pitches
        # Dictionary of frame => pitch

    def getMinPitch(self):
        return min(self.uniqueVals)

    def getPitchRange(self):
        return abs(max(self.uniqueVals) - min(self.uniqueVals))