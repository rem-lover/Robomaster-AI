import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
from PIL import Image 
import io, base64, time

import threading, multiprocessing

class DumbThread(threading.Thread):
    # Test on returning the argument from the function directly.
    # But thr.join() is blocking. So, no good.
        
    def __init__(self, group=None, target=None, name=None, daemon=False,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

class Backend:

    def __init__(self): 
        # Necessary.
        self.queue = multiprocessing.Queue()
        self.ProgressQueue = multiprocessing.Queue()
        # How do you think we got this? Much effort.
        self.badwords = "torture, penetration, unbirth, unusual pupils, urethra, urination, urine, vomit, x-ray, wet clothes, transparent clothes, yaoi, yandere, yuri, lesbian, selfcest, shibari, shemale, snuff, strap-on, stuck in wall, spanking, whipping, hitting, squirting, tanlines, tentacles, vibrator, dildo, sex toys, vibrating egg, panty, piss, prostitution, prostate massage, pregnant, rape, rimjob, ryona, saliva, threesome, nakadashi, netorare, navel fuck, necrophilia, nudity, nose fuck, nose hook, lactation, gay, bisexual, LGBTQ+, leash, scat, smegma, masturbation, mensuration, milking, mind control, mind break, rolled eyes, extended tongue ,gay sex, forniphilia, furry, gaping, futanari,glory hole, amputee, cum bucket,headless, harem, hentai, horse cock, human cattle, humiliation, impregnation, incest, inflation, french kissing, milf, dilf, enema, ear fuck, exhibitionism, exposed clothing, voyeur, facesitting, pubic hair, fisting, footjob, cannibalism, chastity belt, chikan, cervix, orgasm, paizuri, cock, condom, semen, sperm, deepthroat, defloration, domination, submissive, sadistic, asphyxiation, bondage, bdsm, slave, bound, testicles, bikini, penis, breast feeding, bukkake, blowjob, orgy, gangbang, petplay, sex, 69, ahegao, anal, anus, butthole, ass, asshole, butt, prolapse, armpit sex, anthology, swimsuit, bra, lace, latex suit,ropes, ball gag, big breast, pussy, cunt, bitch, beastiality, rule34, adult content, gore, vore, blood, guro, violent, internal organs, weird, disgusting, ugly, vomiting, bad skin, illness, decayed skin, scary, underwear, ligerie, exposed clothing, sexy, nipples, boobs, clitoris, cunt, vagina".replace(', ', ',').split(',')
            

    def send_img2img(self, sketchboard, logger, positive_prompt, seed, sampler, image, sd_model, cnetmodel, cnetpreprocessor, weight, url):
        self.logger = logger
        logger.info(f"received prompt \"{positive_prompt}\"\nControlNet Model={cnetmodel}\nControlNet Preprocessor={cnetpreprocessor}")
        
        # logger.debug(cnetmodel == "None" or cnetpreprocessor == "None")
        # Validation of proper prompt

        # Raising a ValueError blocks the thread. However, as long as I return on this thread, the function will not have any outputs.
        # N: The outputs are managed by queue anyway. So it does not matter unless the queue is tampered with.
        # Same goes for the bottom part. Ha.
        if cnetmodel == "None" or cnetpreprocessor == "None":
            if cnetpreprocessor: pass
            else: 
                # raise ValueError("No cnet")
                win = tk.Toplevel()
                win.title("Error")
                messagebox.showerror('Error', 'ControlNet model/preprocessor cannot be None')

                win.destroy()
                sketchboard.delete("all")
                return 
            # l = tk.Label(win, text="ControlNet model/preprocessor cannot be None.")
            # l.grid(row=0, column=0)

            # b = ttk.Button(win, text="Close", command=win.destroy)
            # b.grid(row=1, column=0)
            
        # logger.debug(not positive_prompt)
        if not positive_prompt:
            # raise ValueError("No prompt")
            win = tk.Toplevel()
            win.title("Error")
            messagebox.showerror('Error', 'At least put some effort in you cunt\nMake a positive prompt!')

            win.destroy()
            sketchboard.delete("all")
            return

        # Local requests are fast. This is a necessary step. You should know that.
        response = requests.get(url=f'{url.strip("/sdapi/v1/img2img")}/sdapi/v1/options')
        logger.debug(response.json()['sd_model_checkpoint'])
        option_payload = {
            "sd_model_checkpoint": sd_model,
            "CLIP_stop_at_last_layers": 2
        }

        response = requests.post(url=f'{url.strip("/sdapi/v1/img2img")}/sdapi/v1/options', json=option_payload)
        logger.debug(f'options rescode -> {response.status_code}')

        payload = {
            "prompt":positive_prompt,
            # "negative_prompt":"(torture, penetration, unbirth, unusual pupils, urethra, urination, urine, vomit, x-ray, wet clothes, transparent clothes, yaoi, yandere, yuri, lesbian, selfcest, shibari, shemale, snuff, strap-on, stuck in wall, spanking, whipping, hitting, squirting, tanlines, tentacles, vibrator, dildo, sex toys, vibrating egg, panty, piss, prostitution, prostate massage, pregnant, rape, rimjob, ryona, saliva, threesome, nakadashi, netorare, navel fuck, necrophilia, nudity, nose fuck, nose hook, lactation, gay, bisexual, LGBTQ+, leash, scat, smegma, masturbation, mensuration, milking, mind control, mind break, rolled eyes, extended tongue ,gay sex, forniphilia, furry, gaping, futanari,glory hole, amputee, cum bucket,headless, harem, hentai, horse cock, human cattle, humiliation, impregnation, incest, inflation, french kissing, milf, dilf, enema, ear fuck, exhibitionism, exposed clothing, voyeur, facesitting, pubic hair, fisting, footjob, cannibalism, chastity belt, chikan, cervix, orgasm, paizuri, cock, condom, semen, sperm, deepthroat, defloration, domination, submissive, sadistic, asphyxiation, bondage, bdsm, slave, bound, testicles, bikini, penis, breast feeding, bukkake, blowjob, orgy, gangbang, petplay, sex, 69, ahegao, anal, anus, butthole, ass, asshole, butt, prolapse, armpit sex, anthology, swimsuit, bra, lace, latex suit,ropes, ball gag, big breast, pussy, cunt, bitch, beastiality, rule34, adult content, gore, vore, blood, guro, violent, internal organs, weird, disgusting, ugly, vomiting, bad skin, illness, decayed skin, scary, underwear, ligerie, exposed clothing, sexy, nipples, boobs, clitoris, cunt, vagina, NSFW, Cleavage, Pubic Hair, Nudity, Naked, Au naturel, Watermark, Text, censored, deformed, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, disconnected head, malformed hands, long neck, mutated hands and fingers, bad hands, missing fingers, cropped, worst quality, low quality, mutation, poorly drawn, huge calf, bad hands, fused hand, missing hand, disappearing arms, disappearing thigh, disappearing calf, disappearing legs, missing fingers, fused fingers, abnormal eye proportion, Abnormal hands, abnormal legs, abnormal feet,  abnormal fingers : 2)", # Add more here
            "negative_prompt" : "EasyNegative",
            "width":512,
            "height":512,
            "steps":20,
            "cfg":7,
            "seed":seed,
            "batch_size":1,
            # "sampler_name":"Euler", TODO : Implement changing the sampler.
            "sampler_name": sampler, # ^: Implemented !
            "init_images":[image],
            "alwayson_scripts": {
                "controlnet": {
                    "args": [
                        {
                            "module":cnetpreprocessor,
                            "model":cnetmodel,
                            "weight":weight
                        }
                    ]
                }
            }
        }
        # Note. Maybe there's more things in ControlNet. But I cannot be bothered to go in and test.

        # respThread = threading.Thread(target = self.img2img_func, args=(f'{url}/sdapi/v1/img2img', payload), daemon=True)
        # respThread.start()

        resp = requests.post(f'{url}/sdapi/v1/img2img', json=payload)
        
        r = resp.json()
        logger.debug(f'img2img r {resp.status_code}')
        image = r['images'][0]
        
        #image = None 
        #while not image:
        #    pass
            # logger.debug("waiting...")

        image = Image.open(io.BytesIO(base64.b64decode(image.split(",", 1)[0])))
        
        # Queues are the way to solve this problem. Basically, it allows for communication between threads.
        # In this case, I can start many threads with this function (send_img2img) concurrently. Obviously, since they all belong to the same class
        # in the main file, the queue defined in the object at the start of the gui class will be the same queue for all threads.
        # Therefore, by using 1 queue, I can manage all of the images. Great!
        self.queue.put(image)
        logger.info('api: i put it ')
        return image

    def img2img_func(self, url, payload):
        resp = requests.post(url, json=payload)
        
        r = resp.json()
        self.logger.debug(f'r {resp.status_code}')
        self.image = r['images'][0]
    
    def get_progress(self, url):
        while True:
            r = requests.get(url=f'{url}/sdapi/v1/progress').json()
            self.ProgressQueue.put(r)
            time.sleep(0.15)