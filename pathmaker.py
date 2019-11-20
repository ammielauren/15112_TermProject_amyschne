import sys
import os
import aubio

mydir = r'C:\Users\Amy\15-112\termProject\aubio_demo\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile
song = fileName

class Path(object):
    def __init__(self, song, samplerate=44100, win_s=1024, hop_s=256):
        # Create a list of notes
        self.src = aubio.source(fileName, samplerate, hop_s)
        samplerate = self.src.samplerate
        tolerance = 0.9

        notes_obj = aubio.notes('default', win_s, hop_s, samplerate)
        # Note: notes object uses ONSET and OFFSET based on the perceived
        #       start and end of a pitch
        # Notes object gives [onset, offset, midi number]
            # Midi number = standard conversion of notes to frequency/tuning
                # Formula: frequency = 440 * (2 ^ ( (n - 69) /12) )
                    # n = Midi number
            # https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies

        print('Starting...')

        totalFrames = 0
        frameIndex = 0

        self.notes = dict()
        self.noteVals = []

        while True:
            samples, read = self.src()
            newNote = notes_obj(samples)
            if (newNote[0] != 0): # newNote is a list of ints
                print(f'Frame {frameIndex}:',end='  ')
                print(f'Start, end = {newNote[0], newNote[2]}', end = '\t')
                print(f'Midi value = {newNote[1]}')
                self.notes[frameIndex] = newNote[1]
                self.noteVals.append(newNote[1])
            totalFrames += read
            frameIndex += 1
            if (read < hop_s):
                break
        
        self.totalFrames = totalFrames

        self.highest = max(self.noteVals)
        self.lowest = min(self.noteVals)
        print(f'Highest = {self.highest}, lowest = {self.lowest}, range = {self.highest-self.lowest}')
        self.range = self.highest-self.lowest
        print(self.totalFrames)
        print(f'Notes dictionary, frames : notes\n{self.notes}')
        print('Done!')

    def makePath(self):
        # Have:
            # self.range, range of pitches
            # self.notes, a list of tuples of the frame and corresponding note
            # self.totalFrames, total # of frames
        # Want to return a list of y-values for the song
        # One y-value for each frame
        path = []
        for frame in range(self.totalFrames):
            if frame in self.notes:
                print('found a frame!')
                note = self.notes[frame] - self.lowest
                print(f'Note = {note}, range = {self.range}', end = '\t')
                print(note/self.range)
                path.append(note/self.range)
            else:
                path.append(0)
        return path

newPath = Path(fileName)
print(newPath.makePath())
#print(newPath.makePath())