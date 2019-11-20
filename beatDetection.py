import os
import beatsParser as beats
import cmu_112_graphics as graphics

mydir = r'C:\Users\Amy\15-112\termProject\aubio_demo\sampleAudio'
myfile = 'file_example_WAV_1MG.wav'

fileName = mydir + os.sep + myfile

beatObj = beats.Beats(fileName)

beats = beatObj.getBeats()

class BeatMaker(graphics.App):
    def appStarted(app, beats, path):
        beats = beats.Beats(path).getBeats()
        app.beats = set(beats)
        print(app.beats)
        app.count = 0
        app.timerDelay = 1
        app.drawCircle = False

    def timerFired(app, beats):
        if app.count in app.beats:
            app.drawCircle = True
            print(f'Drew circle for {app.count}')
        else:
            app.drawCircle = False
    
    def redrawAll(app, canvas):
        r = 20
        if app.drawCircle:
            pass
#            canvas.create_oval(app.width//2-r, app.height//2-r, app.width//2+r, app.height//2+r, fill='blue')
    
def drawBeats():
    app = BeatMaker(beats, fileName)

drawBeats()

