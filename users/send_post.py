import urllib.request
import json 
import requests
import simplejson  
from django.conf import settings   

# body = {'ids': [12, 14, 50]}  
# myurl = "http://www.testmycode.com"

# req = urllib.request.Request(myurl)
# req.add_header('Content-Type', 'application/json; charset=utf-8')
# jsondata = json.dumps(body)
# jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
# req.add_header('Content-Length', len(jsondataasbytes))
# response = urllib.request.urlopen(req, jsondataasbytes)

def send_post_request(myurl,body):
    # req = urllib.request.Request(myurl)
    # req.add_header('Content-Type', 'application/json; charset=utf-8')
    # jsondata = json.dumps(body)
    # jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
    # req.add_header('Content-Length', len(jsondataasbytes))
    # response = urllib.request.urlopen(req, jsondataasbytes)
    # response = requests.post( url = myurl, data = body)
    headers = {'Content-Type': 'application/json','Authorization': settings.FLUTTER_SEC_KEY}

    response = requests.post(myurl, data=json.dumps(body), headers=headers)
    # res_content = simplejson.loads(response)
    res_content = json.loads(response.content)
    return res_content
