import requests

ride = {
    "year": 2023,
    "month": 5
}

url = 'http://localhost:9696/predict'
response = requests.post(url, json=ride)
print(response.json())
