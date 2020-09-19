import http.client

connection = http.client.HTTPConnection('localhost', 10018, timeout=10)

payload = r"""{
    "result": "Success"
}"""

connection.request("POST", "/", payload, headers={ "X-Send-To": "http://localhost:10080" })

