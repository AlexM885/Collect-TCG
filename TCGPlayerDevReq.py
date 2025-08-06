import requests

url = "https://api.tcgplayer.com/app/authorize/authCode"

headers = {"accept": "application/json"}

response = requests.post(url, headers=headers)

print(response.text)