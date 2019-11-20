import os
import sys
import aubio

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
        #print(f'Samplerate = {samplerate}')

        tolerance = 0.2 # Threshold

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

            #print(f'Frame, pitch, confidence = {self.totalFrames/(samplerate), pitch, confidence}')

            if (pitch >= 0 and pitch <= 300):

                self.pitches[self.totalFrames] = pitch
                self.values.append(pitch)
                self.confidences.append(confidence)

            self.totalFrames += read
            
            if read < hop_s: break
        #print(self.totalFrames)
        self.uniqueVals = set(self.values)
#        print(self.uniqueVals)
    
    def getPitchPath(self):
        return self.pitches
        # Dictionary of frame => pitch

    def getMinPitch(self):
        return min(self.uniqueVals)

    def getPitchRange(self):
        print(f'Pitch range = {max(self.uniqueVals)} - {min(self.uniqueVals)} = {max(self.uniqueVals) - min(self.uniqueVals)}')
        return abs(max(self.uniqueVals) - min(self.uniqueVals))


mydir = r'C:\Users\Amy\15-112\termProject\aubio_demo\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile

newPath = PitchPath(fileName)

newPitchPath = PitchPath(fileName)
path = newPitchPath.getPitchPath()
