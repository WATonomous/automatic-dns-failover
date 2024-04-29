import requests

response = requests.request("GET", "http://10.0.50.114:8080")
print(type(response.text)) # str
print(response.text)
print(response.status_code)
