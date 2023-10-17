from tkinter import *
from tkinter import ttk
from tkinter_webcam import webcam

window = Tk()
window.title('testing yay')
window.geometry('1000x1000')

video = webcam.Box(window, width=450, height=450)
video.show_frames()

window.mainloop()