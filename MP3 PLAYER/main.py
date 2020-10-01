from tkinter import *
from tkinter import filedialog
from pygame import mixer
import os
import stagger


class MusicPlayer:
    filename = "MUSIC NAME"

    def __init__(self, window):
        window.geometry('500x400')
        window.title('MP3 Player')
        window.resizable(1, 1)
        Load = Button(window, text='Load Music', width=10, font=('Times', 10), command=self.load)
        Play = Button(window, text='Play', width=10, font=('Times', 10), command=self.play)
        Pause = Button(window, text='Pause', width=10, font=('Times', 10), command=self.pause)
        Stop = Button(window, text='Stop', width=10, font=('Times', 10), command=self.stop)
        self.label = Label(window, text=MusicPlayer.filename, font=('Times', 20), width=25)
        self.label.place(x=60, y=10)
        Load.place(x=200, y=160)
        Play.place(x=200, y=120)
        Pause.place(x=310, y=120)
        Stop.place(x=90, y=120)
        self.music_file = False
        self.playing_state = False

    def load(self):
        MusicPlayer.filename = filedialog.askopenfilename()
        self.music_file = True
        self.play()

    def play(self):
        if self.music_file:
            mixer.init()
            mixer.music.load(MusicPlayer.filename)
            mixer.music.play()
            mp3 = stagger.read_tag(MusicPlayer.filename)
            
            self.label['text'] = os.path.basename(MusicPlayer.filename)

    def pause(self):
        if not self.playing_state:
            mixer.music.pause()
            self.playing_state = True
        else:
            mixer.music.unpause()
            self.playing_state = False

    def stop(self):
        mixer.music.stop()


root = Tk()
Photo = PhotoImage(file="icon.png")
root.iconphoto(False, Photo)
app = MusicPlayer(root)
root.mainloop()
