import http.client
import json
import base64
import datetime
from jose import jws

connection = http.client.HTTPConnection('localhost', 10017, timeout=10)

query = r"""{
    "returnUrl": "http://host.docker.internal:8000",
    "dockerImage": "hello",
    "files": {
        "main.cpp": "#include <iostream>\n\nint main() { std::cout << \"Hello json!\"; }",
        "megafile.h": "// best solution to the problem ever!"
    },
    "maxRunTime": 15
}"""

message = {
    "timestamp": int(datetime.datetime.timestamp(datetime.datetime.now())),
    "payload": json.loads(query),
    "uri": "/abcd"
}

secret_key64 = "aaaa"
decoded_key = base64.decodebytes(secret_key64.encode("utf-8"))
request = jws.sign(json.dumps(message).encode("utf-8"), decoded_key, algorithm="HS256")
connection = http.client.HTTPConnection("localhost:10017", timeout=10)
connection.request("POST", "/abcd", request)
response = connection.getresponse()
print(response.status)
