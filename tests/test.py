import requests
 
#api-endpoint
URL = "http://localhost:8000/"
 
#sending get request and saving the response as response object
r = requests.get(url=URL)

print(r.status_code)
print(r.json())
