import requests

url = 'http://localhost:8000/api/user_profile/'
headers = {'Authorization': 'Bearer <token>'}

response = requests.get(url, headers=headers)

print(response.json())

