import requests
import json


url = 'http://127.0.0.1:7860'

response = requests.get(url=f'{url}/sdapi/v1/options')
r = json.loads(response.text)
print(r["sd_model_checkpoint"])