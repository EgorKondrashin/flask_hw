import requests

response = requests.get('http://127.0.0.1:5000/user/1')

print(response.json())
