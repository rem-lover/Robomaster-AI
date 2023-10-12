import requests

url = 'http://127.0.0.1:7860'

r = requests.get(url=f'{url}/sdapi/v1/options')

for i, j in r.json().items():
    print(i,':', j)

# sd_model_checkpoint : realisticVisionV51_v51VAE
