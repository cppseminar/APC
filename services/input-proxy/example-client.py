import http.client
from jose import jws

connection = http.client.HTTPConnection('localhost', 10017, timeout=10)

payload = r"""{
    "returnUrl": "https://example.com/",
    "dockerImage": "palindrom",
    "files": {
        "main.cpp": "#include <iostream>\n\nint main() { std::cout << \"Hello json!\"; }",
        "megafile.h": "// best solution to the problem ever!"
    },
    "maxRunTime": 15
}"""

key = 'example hmac key'

req = jws.sign(str.encode(payload), key, algorithm='HS256')
print(req)

res = jws.verify(req, key, 'HS256')
print(res == str.encode(payload))

connection.request("POST", "/", req)

