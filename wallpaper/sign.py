import time
import random
import string
import hashlib


class Sign:
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15)),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': int(time.time()),
            'url': url
        }

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        print(string)
        self.ret['signature'] = hashlib.sha1(string.encode("utf-8")).hexdigest()
        return self.ret
