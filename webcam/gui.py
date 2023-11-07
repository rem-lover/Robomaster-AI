from tkinter import *
from tkinter import ttk
import PIL, os
from PIL import ImageTk, Image
import numpy as np
import cv2
import backend

finished = False

def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    vid = cv2.VideoCapture(0)

    window = Tk()
    window.title('testing yay')

    my_image = ImageTk.PhotoImage(Image.open('temp.png'))
    imLabel = Label(window, image=my_image, width=512, height=512)
    imLabel.grid(row=0, column=1)

    webcam_label = Label(window, width=512, height=512)
    webcam_label.grid(row=0, column=0)

    def open_camera():
        global opencv_image, photo_image, finished
        _, frame = vid.read() 
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 
        captured_image = Image.fromarray(opencv_image) 
        photo_image = ImageTk.PhotoImage(image=captured_image) 

        webcam_label.photo_image = photo_image 
        webcam_label.configure(image=photo_image)  
        print(finished)      
        if not finished:
            webcam_label.after(10, open_camera)


    def take_photo():
        global finished
        webcam_label.photo_image = photo_image
        webcam_label.configure(image=photo_image)
        finished = True
        gen_image = ImageTk.PhotoImage(backend.main(opencv_image))
        imLabel.configure(image=gen_image)
        imLabel.photo_image = gen_image


    

    photo_button = Button(text='take a photo', padx=10, pady=10, command=take_photo)
    photo_button.grid(row=1, column=0, columnspan=2)


    open_camera()
    window.mainloop()



if __name__ == '__main__':
    main()

