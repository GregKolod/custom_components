import json
import requests

url = 'http://192.168.1.10:8080/remoteControl/cmd?operation='
resoult = []

for i in range(0, 10240):
    response = requests.get(url + str(i)).json()
    result = response['result']['responseCode']

    if result == '0':
        print(i, response)
