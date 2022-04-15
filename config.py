import json

with open('config.json') as json_file:
    jsondata = json.load(json_file)
    username = jsondata['username']
    password = jsondata['password']
    avatar = jsondata['avatar']