# Tk section
from tkinter import *
from tkinter import colorchooser
from tkinter import filedialog
from tkinter import ttk
from sketchpad import Sketchpad
import backend
# Lib section
from PIL import Image, ImageTk
import numpy as np
import re, os, time, base64, io, requests, logging, threading, json

# Default
SD_PATH = "http://127.0.0.1:7860"
CONFIG_PATH = '.\config.json'
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class DefaultWindow(Tk):

    def __init__(self, *args, **kwargs):

        with open(CONFIG_PATH, 'r') as f:
            self.config = json.load(f)

        self.internalCount = 0
        self.internal_time = time.time()
        self.logger = logging.getLogger(name='foo')
        self.logger.setLevel(1)
        formatter = logging.Formatter('[%(threadName)s] %(asctime)s.%(msecs)03d : %(levelname).1s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        s_handler = logging.StreamHandler()
        s_handler.setLevel(10)
        s_handler.setFormatter(formatter)
        self.logger.addHandler(s_handler)
        self.bck_api = backend.Backend()

        # This variable is the state of the cursor.
        self.pressing = False

        Tk.__init__(self, *args, **kwargs)
        self.title('miku miku you')

        mainframe = ttk.Frame(self, padding='3 3 12 12')
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Control positive prompt.
        dumbLabel = ttk.Label(mainframe, text='positive prompt')
        dumbLabel.grid(column=1, row=1, sticky=(W))
        self.positive_prompt = StringVar()
        self.positive_prompt.set("masterpiece, best quality")
        positive_prompt_entry = ttk.Entry(mainframe, width=50, textvariable=self.positive_prompt)
        positive_prompt_entry.grid(column=2, row=1)

        # Seed
        dumbLabel = ttk.Label(mainframe, text='Seed')
        dumbLabel.grid(column=3, row=1, sticky=(W))
        self.seedVar = IntVar()
        self.seedVar.set(42)
        seed_entry = ttk.Entry(mainframe, width=50, textvariable=self.seedVar)
        seed_entry.grid(column=4, row=1)

        # Control SD_model.
        dumbLabel2 = ttk.Label(mainframe, text='model')
        dumbLabel2.grid(column=1, row=2, sticky=(W))
        # API SD_PATH/sdapi/v1/sd-models
        self.modelSelectorVar = StringVar()
        modelSelector = ttk.Combobox(mainframe, width=50, text=self.modelSelectorVar)
        models = [i['model_name'] for i in requests.get(f'{SD_PATH}/sdapi/v1/sd-models').json()]
        model = self.config['model']
        print(models)
        modelSelector['values'] = models
        # Catch potential error due to bad config
        try : 
            modelSelector.current(models.index(model))
        except:
            modelSelector.current(0)
        modelSelector.grid(column=2, row=2)

        # Control Sampler.
        l = ttk.Label(mainframe, text='sampler')
        l.grid(column=4, row=2)
        # API SD_PATH/sdapi/v1/sd-models
        self.samplerSelectorVar = StringVar()
        sampler = self.config['sampler']
        samplerSelector = ttk.Combobox(mainframe, width=50, text=self.samplerSelectorVar)
        samplers = [i['name'] for i in requests.get(f'{SD_PATH}/sdapi/v1/samplers').json()]
        samplerSelector['values'] = samplers
        # (same)
        try : 
            samplerSelector.current(models.index(sampler))
        except:
            samplerSelector.current(0)
        samplerSelector.grid(column=5, row=2)

        # ControlNet Type
        cnet_TypeLabel = ttk.Label(mainframe, text='ControlNet Type')
        cnet_TypeLabel.grid(column=1, row=3, sticky=(W))
        # API SD_PATH/sdapi/v1/sd-models
        self.controlTypeVar = StringVar()
        self.controlTypeSelector = ttk.Combobox(mainframe, width=50, text=self.controlTypeVar)
        self.controlTypes = [i for i in requests.get(f'{SD_PATH}/controlnet/control_types').json()['control_types'].keys() if i != 'All']
        self.controlTypeSelector['values'] = self.controlTypes
        self.controlTypeSelector.current(7)
        self.controlTypeSelector.grid(column=2, row=3)

        self.controlWeight = DoubleVar()
        self.controlWeight.set(0)
        self.controlWLabel = ttk.Label(mainframe, text=f'Cnet_W: {self.controlWeight.get()}')
        self.controlWLabel.grid(column=3, row=3)
        scaler = ttk.Scale(mainframe, length=200, from_=0, to=2, orient='horizontal', variable=self.controlWeight, command=self.updateControlWLabel)
        scaler.grid(column=4, row=3)        
        # Control ControlNet model.
        # Invariants
        dumbLabel3 = ttk.Label(mainframe, text='ControlNet model')
        dumbLabel3.grid(column=1, row=4, sticky=(W))
        
        # API SD_PATH/sdapi/v1/sd-models
        self.controlModelVar = StringVar()
        self.controlModelSelector = ttk.Combobox(mainframe, width=50, text=self.controlModelVar)
        self.controlModelSelector.grid(column=2, row=4)

        # Invariant
        dumbLabel4 = ttk.Label(mainframe, text='ControlNet Preprocessor')
        dumbLabel4.grid(column=4, row=4)
        # API SD_PATH/sdapi/v1/sd-models
        self.controlPreprocessorVar = StringVar()
        self.controlPreprocessorSelector = ttk.Combobox(mainframe, width=50, text=self.controlPreprocessorVar)
        self.controlPreprocessorSelector.grid(column=5, row=4)

        self.update_controlNetSelectors(None)

        l = ttk.Label(mainframe, text="Brush Size")
        l.grid(column=1, row=5, sticky=(W))
        self.brushSizeVar = IntVar()
        self.brushSizeSelector = ttk.Combobox(mainframe, width=30, text=self.brushSizeVar)
        self.brushSizeSelector['values'] = [i for i in range(5, 56, 10)]
        self.brushSizeSelector.current(0)
        self.brushSizeSelector.grid(column=2, row=5, sticky=(W))

        self.colorChooseButton = ttk.Button(mainframe, width=20, text="choose a color", command = self.updateColor)
        self.colorChooseButton.grid(column=3,row=5)

        self.bar = ttk.Progressbar(mainframe, length=300, mode='determinate')
        self.bar.grid(column=4,row=5, columnspan=2, sticky=(E))
        self.bar.grid_configure(padx=5)
        self.progress = ttk.Label(mainframe, text="0%")
        self.progress.grid(column=6,row=5, sticky=(W))

        self.sketchpad = Sketchpad(mainframe, width=512, height=512, background='gray76')
        self.sketchpad.grid(column=1, row=6, columnspan=3)

        self.imCanvas = Canvas(mainframe, width=512, height=512, background='gray76')
        # Not ideal. To avoid dependencies, we will create a new image.
        self.imCanvas.image = i = ImageTk.PhotoImage(Image.fromarray(np.zeros((512, 512))))
        # self.imCanvas.image = i = ImageTk.PhotoImage(Image.open('./paint/temp.png'))
        self.imCanvasState = self.imCanvas.create_image(0, 0, image=i, anchor='nw')
        self.imCanvas.grid(column=4, row=6, columnspan=3)

        # after complete setup, bind functions!
        self.controlTypeSelector.bind("<<ComboboxSelected>>", self.update_controlNetSelectors)
        self.brushSizeSelector.bind("<<ComboboxSelected>>", self.updateBrushSize)
        
        # smart delegation hehehe
        self.sketchpad.bind("<B1-ButtonRelease>", self.dummy1)
        self.sketchpad.bind("<Button-1>", self.dummy2)
        self.sketchpad.bind("<B1-Motion>",self.dummy3)

        # Move self.CallAPI to another thread,
        # change activation check requirements to look at self.pressing variable,
        # every time activationcheck is invoked, try to wait for one more second first, this wil be blocking in the alternate thread
        # (while loop to wait until self.pressing is changed, not in 1s return)

        self.controlTypeVar.trace("w", lambda x, y, z: self.dummyCallAPI2(self.sketchpad))
        self.controlPreprocessorVar.trace("w", lambda x, y, z: self.dummyCallAPI2(self.sketchpad))

        def updateConfig(k, v):
            self.config[k] = v
            with open(CONFIG_PATH, 'w+') as f:
                json.dump(self.config, f, indent=1)
        self.modelSelectorVar.trace("w", lambda x, y, z: (updateConfig('model', self.modelSelectorVar.get())))
        self.samplerSelectorVar.trace("w", lambda x, y, z: (updateConfig('sampler', self.samplerSelectorVar.get())))

        self.emptyCanvasButton = ttk.Button(mainframe, width=20, text="Clear", command = self.resetSketchySketch)
        self.emptyCanvasButton.grid(column=1,row=7)

        self.forceGenerateButton = ttk.Button(mainframe, width=20, text="Generate", command = lambda : self.dummyCallAPI2(self.sketchpad))
        self.forceGenerateButton.grid(column=2,row=7)

        self.saveImageButton = ttk.Button(mainframe, width=20, text='Save Image', command = self.saveImage)
        self.saveImageButton.grid(column=3,row=7)

        self.logger.debug("finish setting up GUI")

        ImageUpdater = threading.Thread(target=self.UpdateImage, name='imageUpdater')
        ImageUpdater.start()

        ProgressUpdater = threading.Thread(target=self.startGetProgress, name='getProgressUpdater')
        ProgressUpdater.start()

    def saveImage(self):
        filetypes = (('PNG','*.png'), ('JPG',"*.jpg"), ('All files','*'))
        f = filedialog.asksaveasfile(mode='wb', filetypes=filetypes, defaultextension=filetypes, initialdir=os.getcwd(), initialfile='out.png')
        self.image.save(f)

    def updateControlWLabel(self, e): self.controlWLabel['text'] = f'Cnet_W: {self.controlWeight.get():.3f}'

    def changePressState(self):
        # self.logger.info(f'{self.pressing} -> {not self.pressing}')
        self.pressing = not self.pressing
        # self.logger.info(self.pressing)
        '''if self.pressing == True : self.pressing = False 
        if self.pressing == False : self.pressing = True'''

    def update_controlNetSelectors(self, event):

        LocalControlTypes = requests.get(f'{SD_PATH}/controlnet/control_types').json()['control_types']
        self.logger.debug(f"looking at {self.controlTypeVar.get()}")
        if self.controlTypeVar.get() == "None":
            return
        
        data = LocalControlTypes[self.controlTypeVar.get()]

        self.controlModelSelector['values'] = data['model_list']
        self.controlPreprocessorSelector['values'] = data['module_list']
        self.controlModelVar.set(data['default_model'])
        self.controlPreprocessorVar.set(data['default_option'])

    def updateBrushSize(self, eventObject):
        self.sketchpad.brushSize = self.brushSizeVar.get()

    def updateColor(self):
        c = colorchooser.askcolor(title="choose smartass")
        self.sketchpad.color = c[-1]

    # Segment: API-related. 
    # Dummy functions are used, because I can't really 
    def dummy1(self, state):
        # self.logger.debug('dummy1')
        self.changePressState()
        self.dummyCallAPI(state) # for convenience, dummyCallAPI is called instead of just invoking callAPI directly

    def dummy2(self, state):
        self.sketchpad.savePosn(state)
        self.changePressState()

    def dummy3(self, state):
        # self.logger.info(f'{self.pressing} -> {True}')
        self.sketchpad.addLine(state)
        self.pressing = True

    def activationCheck(self):
        # Avoid over-spam of our API. We do not want the image to like, not load.
        '''self.internalCount += 1

        now_time = time.time()
        self.logger.debug(now_time - self.internal_time)
        self.logger.debug(self.internalCount)'''

        start_t = time.time()
        dt = 0
        self.logger.debug("Start check")
        while dt <= self.config['wait_time']: # 1:
            
            #self.logger.debug(f'dt {dt} : {self.pressing}')
            if self.pressing: 
                self.logger.debug(f"Fail check. pressing = {self.pressing}")
                return False
            dt = time.time() - start_t
        self.logger.debug(f"Pass check. pressing = {self.pressing}")
        return True

    def dummyCallAPI(self, eventObject):

        APIBackendThread = threading.Thread(target = self.callAPI, args = (eventObject, ),)#  name='apiBackend')
        APIBackendThread.start()

    # This is necessary to ensure that activationCheck does not block.
    # An interface for the function that detects change in model.
    def dummyCallAPI2(self, sketchpad_obj):

        APIBackendThread = threading.Thread(target = self.callAPI, args = (sketchpad_obj, ),)#  name='apiBackend')
        APIBackendThread.start()

    def callAPI(self, eventObject):

        if not self.activationCheck():
            return
        img = self.sketchpad.postscript(colormode='color', pagewidth=512)
        im = Image.open(io.BytesIO(bytes(img , 'ascii')))
        buffered = io.BytesIO()
        im.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        # !!! You need ghostscript !!!
        # See https://ghostscript.com/releases/gsdnld.html
        if eventObject == self.sketchpad:
            sketchy = self.sketchpad
        else:
            sketchy = eventObject.widget
        pos = self.positive_prompt.get()
        # to avoid making too much threads, i will put the filter here
        matches = re.finditer(r"(?=("+'|'.join(self.bck_api.badwords)+r"))", pos)
        for i in matches: 
            # self.logger.debug(i.group(1))
            pos = pos.replace(i.group(1), '')
        pos = (',').join([i for i in pos.split(',') if i and i != ' '])

        # Uncomment below line if the thing is spamming thread too much. But with the updated check, I don't think that will happen.
        # if 'img2img_Thread' in [i.name for i in threading.enumerate()]: return 

        # call backend func
        # to be honest, it's not too good to send like 1 billion args. therefore, if the need arises, i'll make a class to help with sending info (clarity haha yay)
        thr = backend.DumbThread(
            target=self.bck_api.send_img2img, args=(sketchy, self.logger, pos, self.seedVar.get(), self.samplerSelectorVar.get(),
            encoded_image, self.modelSelectorVar.get(), self.controlModelVar.get(), self.controlPreprocessorVar.get(), self.controlWeight.get(), SD_PATH),
            name='img2img_Thread'
        )

        thr.start()
        # Get is not to be done by this function. Separated thread management is good, I think.

    def UpdateImage(self):

        # Note. self.bck_api.queue.get() is blocking. It only executes whenever the queue has something available to be get.
        # So this function MUST be called in the background. Else it will block the main thread.

        while True:

            image = self.bck_api.queue.get()

            if image:
                print(image.size)

                # image.show()
                self.image = image # allow manipulation of image data.
                self.imCanvas.image = i = ImageTk.PhotoImage(image)
                # self.imCanvasState = self.imCanvas.create_image(0, 0, image=i, anchor='nw')
                self.imCanvas.itemconfig(self.imCanvasState, image=i)
                self.logger.debug("Finished updating")
            
            self.logger.debug("routine call")

    def startGetProgress(self):
        
        # This is not efficient. To be honest, if you REALLLLLY wanted to have maximum efficiency, you would put this function and some sort of
        # stop somewhere in the backend.
        # But I am lazy. And it works. So this is just a 6.67Hz updater (to avoid blowing up the rates / blocking execution of img2img API).
        progressThread = threading.Thread(target=self.bck_api.get_progress, args=(SD_PATH, ))
        progressThread.start()
        while True:
            progress = self.bck_api.ProgressQueue.get()
            self.bar['value'] = progress['progress'] * 100
            self.progress['text'] = f"{progress['progress'] * 100 : .2f}%"
            # self.logger.debug(progress)

    resetSketchySketch = lambda self : self.sketchpad.delete("all")

if __name__ == "__main__":
    defaultWindow = DefaultWindow()
    defaultWindow.mainloop()