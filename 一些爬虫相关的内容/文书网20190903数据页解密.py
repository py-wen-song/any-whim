
import re
import json
import time
import random
import base64
from urllib.parse import unquote, quote

import requests
from lxml import etree

# pip install cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# 3des, cbc
def get_encryptor(key, iv=None):
    algoer = algorithms.TripleDES(key)
    cipher = Cipher(algoer, modes.CBC(iv), backend=default_backend())
    def enc(bitstring):
        padder    = padding.PKCS7(algoer.block_size).padder()
        bitstring = padder.update(bitstring) + padder.finalize()
        encryptor = cipher.encryptor()
        return encryptor.update(bitstring) + encryptor.finalize()
    def dec(bitstring):
        decryptor = cipher.decryptor()
        ddata     = decryptor.update(bitstring) + decryptor.finalize()
        unpadder  = padding.PKCS7(algoer.block_size).unpadder()
        ddata     = unpadder.update(ddata) + unpadder.finalize()
        return ddata
    class f:pass
    f.encrypt = enc
    f.decrypt = dec
    return f

def rdn(length):
    temp = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join([random.choice(temp) for i in range(length)]).encode()

def create_ciphertext():
    key  = rdn(24)
    iv   = ('%04d%02d%02d' % time.localtime()[:3]).encode()
    data = str(int(time.time()*1000)).encode()
    encryptor = get_encryptor(key, iv)
    data =  (key + iv + base64.b64encode(encryptor.encrypt(data))).decode()
    return ' '.join([bin(ord(i))[2:] for i in data])

def post_info(docId):
    # 生成请求参数函数
    def mk_url_headers_body():
        url = 'http://wenshu.court.gov.cn/website/parse/rest.q4w'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
        }
        body = {
            "docId": docId,
            "ciphertext": create_ciphertext(),
            "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@docInfoSearch",
            "__RequestVerificationToken": rdn(24)
        }
        return url,headers,body
    url,headers,body = mk_url_headers_body()
    _data     = json.loads(requests.post(url,headers=headers,data=body).content)
    key       = _data['secretKey'].encode()
    iv        = ('%04d%02d%02d' % time.localtime()[:3]).encode()
    _encdata  = base64.b64decode(_data['result'].encode())
    encryptor = get_encryptor(key, iv)
    return json.loads(encryptor.decrypt(_encdata))

if __name__ == '__main__':
    s = post_info("adb77f453fa84556a8afaaba00c0fa28")
    print(s)
