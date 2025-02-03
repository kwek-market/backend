import urllib.request
import json 
import requests
import simplejson  
from django.conf import settings   


def send_flutter_post_request(myurl,body):
    headers = {'Content-Type': 'application/json','Authorization': settings.FLUTTER_SEC_KEY}

    response = requests.post(myurl, data=json.dumps(body), headers=headers)
    # res_content = simplejson.loads(response)
    res_content = json.loads(response.content)
    return res_content

