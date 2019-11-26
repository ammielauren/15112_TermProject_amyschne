import os
import sys
import aubio
from aubio import tempo
from numpy import median, diff

# Referenced https://salsa.debian.org/piem/aubio/blob/master/python/demos/demo_tempo.py
# And https://github.com/aubio/aubio/blob/master/python/demos/demo_tempo.py
    # Python-implemented aubio demos withs tempo

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

        self.totalFrames = 0 # All frames read

        while True:
            samples, read = src()
            beatDetected = tempoDetection(samples)
            if (beatDetected):
                currBeat = int(self.totalFrames - delay + beatDetected[0]*hop_s)
                self.beats.append(currBeat/samplerate)
            self.totalFrames += read
            if (read < hop_s):
                break

    def getBeats(self):
        return self.beats
    
    # Returns set of beat-times rounded to the first decimal place
    def roundToFirstDecimal(self):
        roundedBeats = set()
        for beat in self.beats:
            val = int(beat)
            decimals = (beat - val)*10
            append = int(round(decimals))/10
            val += append
            roundedBeats.add(val)
        return roundedBeats

    
    def convertBeatsToBPM(self):
        # Use beatsFound to find period and bpm from there
        if (len(self.beats) > 1):
            if (len(self.beats) < 4):
                return 0
            # Calculate beats occurring every 60 sec (one minute)
            bpms = 60./diff(self.beats)
                # Diff: calculates the discrete difference of beats
            return median(bpms)
        else:
            return -1


mydir = r'C:\Users\Amy\15-112\termProject\TP1_Deliverable\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile
song = fileName

newB = Beats(song)
print(newB.beats)
print(newB.roundToFirstDecimal())