from tkinter import *
from tkinter import ttk
import PIL, os
from PIL import ImageTk, Image
import numpy as np
import cv2
import backend

class DefaultWindow(Tk):

    def __init__(self, *args, **kwargs):

        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        self.vid = cv2.VideoCapture(0)
        self.finished = False

        Tk.__init__(self, *args, **kwargs)

        self.title('testing yay')

        self.my_image = ImageTk.PhotoImage(Image.fromarray(np.zeros((512, 512))))
        self.imLabel = Label(self, image=self.my_image, width=512, height=512)
        self.imLabel.grid(row=1, column=1)

        self.webcam_label = Label(self, width=512, height=512)
        self.webcam_label.grid(row=1, column=0)

        self.photo_button = Button(text='take a photo', padx=10, pady=10, command=self.take_photo)
        self.photo_button.grid(row=2, column=0)

        self.reset_button = Button(text='reset', padx=10, pady=10, command=self.reset)
        self.reset_button.grid(row=2, column=1)

        self.positive_prompt = StringVar()
        self.positive_prompt.set("masterpiece, best quality")
        self.positive_prompt_entry = Entry(self, font=('Helvetica', 16), width=75, textvariable=self.positive_prompt)
        self.positive_prompt_entry.grid(row=0, column=0, columnspan=2)

        self.open_camera()

    def open_camera(self):
        if self.finished:
            return
        self._, self.frame = self.vid.read() 
        self.opencv_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA) 
        self.captured_image = Image.fromarray(self.opencv_image) 
        self.photo_image = ImageTk.PhotoImage(image=self.captured_image) 

        self.webcam_label.photo_image = self.photo_image 
        self.webcam_label.configure(image=self.photo_image)  
        self.webcam_label.after(10, self.open_camera)

    def take_photo(self):
        self.webcam_label.photo_image = self.photo_image
        self.webcam_label.configure(image=self.photo_image)
        self.finished = True
        self.gen_image = ImageTk.PhotoImage(backend.main(self.opencv_image, self.positive_prompt_entry.get()))
        self.imLabel.configure(image=self.gen_image)
        self.imLabel.photo_image = self.gen_image

    def reset(self):
        self.finished = False
        self.open_camera()

if __name__ == "__main__":
    defaultWindow = DefaultWindow()
    defaultWindow.mainloop()