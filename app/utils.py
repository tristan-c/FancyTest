from Crypto.Cipher import AES
from Crypto import Random

import base64
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError

def getCrypter(key):
    obj = AES.new(key, AES.MODE_CBC, Random.new().read(AES.block_size))
    return obj

def get_bearer_token(consumer_key,consumer_secret):
    """stolen from https://github.com/pabluk/twitter-application-only-auth/
    no licence so thx pabluk
    """
    bearer_token = '%s:%s' % (consumer_key, consumer_secret)
    encoded_bearer_token = base64.b64encode(bearer_token.encode('ascii'))
    request = Request('https://api.twitter.com/oauth2/token')
    request.add_header('Content-Type',
                       'application/x-www-form-urlencoded;charset=UTF-8')
    request.add_header('Authorization',
                       'Basic %s' % encoded_bearer_token.decode('utf-8'))

    request_data = 'grant_type=client_credentials'.encode('ascii')
    request.data = request_data

    response = urlopen(request)
    raw_data = response.read().decode('utf-8')
    data = json.loads(raw_data)
    return data['access_token']

def get_only_urls(_list):
    url_list = []
    for items in _list:
        if items:
            for item in items:
                url = item.get("url",None)
                if url and url not in url_list:
                    url_list.append(url)

    return url_list