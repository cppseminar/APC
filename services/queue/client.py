"""This is implementation of client for our queue.  Serves for development
purposes only.
"""
import argparse
import asyncio
import http.client
import json
import sys

SELF_URL = "http://localhost"
SELF_PORT = 11223

SELF_FULL_URL = SELF_URL + ":" + str(SELF_PORT) + "/"

def command1(port):
    message = {
        "returnUrl" : SELF_FULL_URL,
        "dockerImage": "hello",
        "maxRunTime": 10,
        "files": {
            "main.cpp": "aa",
        },
    }
    request = json.dumps(message)
    connection = http.client.HTTPConnection(
        "localhost:10009", timeout=10
    )
    connection.request("POST", "/", request)
    response = connection.getresponse()
    return f"Response status: {response.status}"



def client(port):
    commands = [
        command1
    ]
    while True:
        prompt = input("Command> ")
        try:
            result = commands[int(prompt)](port)
            print(result)
        except Exception as e:
            print(e)

def server(port):
    ...



if __name__ == "__main__":
    print("hello")
    parser = argparse.ArgumentParser("Tester")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--client", type=int, metavar='port', dest='client')
    group.add_argument("--server", type=int, metavar='port', dest='server')
    args = parser.parse_args()
    if args.client:
        client(args.client)
    elif args.server:
        server(port)
