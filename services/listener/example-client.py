import http.client
from jose import jws

connection = http.client.HTTPConnection('localhost', 1488, timeout=10)

payload = r"""{
    "returnUrl": "https://example.com/",
    "dockerImage": "palindrom",
    "files": {
        "main.cpp": "#include <iostream>\n\nint main() { std::cout << \"Hello json!\"; }"
    },
    "maxRunTime": 1
}"""

private_key = {
    "kty":"EC",
    "d":"JICDA0EoyoUrOLWpykFwKgFB-9tIfWphUnfqjWAVSdA",
    "crv":"P-256",
    "x":"bWrIDOM1ZD_aeQ--HJoqL_ench7qRSGBCD_5t3gBgzM",
    "y":"BJKB0iiarWhW1Q_btd2KSBIwYSGfn38T2xKq36fH-Ks"
}

public_key = {
    "kty":"EC",
    "crv":"P-256",
    "x":"bWrIDOM1ZD_aeQ--HJoqL_ench7qRSGBCD_5t3gBgzM",
    "y":"BJKB0iiarWhW1Q_btd2KSBIwYSGfn38T2xKq36fH-Ks"
}


req = jws.sign(str.encode(payload), private_key, algorithm='ES256')
print(req)

res = jws.verify(req, public_key, 'ES256')
print(res == str.encode(payload))

connection.request("POST", "/", req)

