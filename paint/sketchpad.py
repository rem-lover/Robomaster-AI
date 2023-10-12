from tkinter import Canvas

class Sketchpad(Canvas):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<Button-1>", self.savePosn)
        self.bind("<B1-Motion>",self.addLine)
        self.brushSize = 5
        self.color = None

    def savePosn(self, event):
        self.lastx, self.lasty = event.x, event.y
    
    def addLine(self, event):
        if self.color: 
            self.create_line((self.lastx, self.lasty, event.x, event.y), capstyle='round', fill=self.color, width=self.brushSize)
        else:
            self.create_line((self.lastx, self.lasty, event.x, event.y), capstyle='round', width=self.brushSize)
        self.savePosn(event)