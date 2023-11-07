import requests
import io
import base64
from PIL import Image
import cv2
import time


def main(image, prompt='1girl'):

    img_encode = cv2.imencode('.png', image)[1].tobytes()
    encoded_image = base64.b64encode(img_encode).decode('utf-8')

    # calling the api
    url = 'http://127.0.0.1:7860'
    payload = {
        "prompt": prompt,
        "negative_prompt": "underwear, ligerie, exposed clothing, sexy, nipples, boobs, clitoris, cunt, vagina, NSFW, Cleavage, Pubic Hair, Nudity, Naked, Au naturel, Watermark, Text, censored, deformed, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, disconnected head, malformed hands, long neck, mutated hands and fingers, bad hands, missing fingers, cropped, worst quality, low quality, mutation, poorly drawn, huge calf, bad hands, fused hand, missing hand, disappearing arms, disappearing thigh, disappearing calf, disappearing legs, missing fingers, fused fingers, abnormal eye proportion, Abnormal hands, abnormal legs, abnormal feet,  abnormal fingers",
        "batch_size": 1,
        'sampler_name': 'Euler a',
        "steps": 25,
        "cfg_scale": 5,
        "alwayson_scripts": {
            "controlnet": {
                "args": [
                    {
                        "input_image": encoded_image,
                        "module": "openpose",
                        "model": "control_v11p_sd15_openpose [cab727d4]",
                        'weight': 2
                    },
                    {
                        "input_image": encoded_image,
                        "module": "canny",
                        "model": "control_v11p_sd15_canny [d14c016b]",
                        'weight': 0.5,
                        "guidance": 1,
                        "guidance_start": 0,
                        "guidance_end": 0.7,
                    }
                ]
            }
        }
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()

    image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
    return image


if __name__ == '__main__':
    main()

    