#!/usr/bin/env python

"""This is implementation of client for our queue.  Serves for development
purposes only.
"""
import argparse
import asyncio
import http.client
import json
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer

SELF_URL = "http://localhost"
SELF_PORT = 10018

SELF_FULL_URL = SELF_URL + ":" + str(SELF_PORT) + "/"

FILE1 = """
#include <iostream>

int main() {
int i = 5;
std::cout << "Hello world";
for (int i =0; i < 4096; i++) {

	auto* p = new int[1024*1024];
	p[1234] = 54;
	p[4234] = 54;
}

std::cout << "leak successfult" << std::endl;
}
"""

FILE2 = """
#include <iostream>

int main() {
for (int i =0; i < 4096; ) {

	auto* p = new int[1024*1024];
	p[1234] = 54;
	p[4234] = 54;
    delete p;
}

std::cout << "leak successfult" << std::endl;
}
"""


def command0(port):
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
        "localhost:"+str(port), timeout=10
    )
    connection.request("POST", "/", request)
    response = connection.getresponse()
    return f"Response status: {response.status}"

def command1(port):
    message = {
        "returnUrl" : SELF_FULL_URL,
        "dockerImage": "hello",
        "maxRunTime": 10,
        "files": {
            "main.cpp": FILE1,
        },
    }
    request = json.dumps(message)
    connection = http.client.HTTPConnection(
        "localhost:"+str(port), timeout=10
    )
    connection.request("POST", "/", request)
    response = connection.getresponse()
    return f"Response status: {response.status}"


def command2(port):
    message = {
        "returnUrl" : SELF_FULL_URL,
        "dockerImage": "hello",
        "maxRunTime": 10,
        "files": {
            "main.cpp": FILE2,
        },
    }
    request = json.dumps(message)
    connection = http.client.HTTPConnection(
        "localhost:"+str(port), timeout=10
    )
    connection.request("POST", "/", request)
    response = connection.getresponse()
    return f"Response status: {response.status}"

def command3(port):
    message = {
        "returnUrl" : SELF_FULL_URL,
        "dockerImage": "hello",
        "maxRunTime": 10,
        "memory": 1000 * 1000 * 1000,
        "files": {
            "main.cpp": FILE2,
        },
    }
    request = json.dumps(message)
    connection = http.client.HTTPConnection(
        "localhost:"+str(port), timeout=10
    )
    connection.request("POST", "/", request)
    response = connection.getresponse()
    return f"Response status: {response.status}"

class ServerHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_error(self):
        response = "Server error ;)".encode("ascii")
        self.send_response(500)
        self.send_header('Content-type', 'text/plain')
        # self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self):
        print("Get request - Unsupported")
        self._set_error()

    def do_POST(self):
        print("Post request - Unsupported")
        self._set_error()


    def do_PATCH(self):
        print("Patch request")
        response = "".encode("ascii")
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        # self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
        b = bytearray(int(self.headers['content-length']))
        self.rfile.readinto(b)
        try:
            decoded = json.dumps(json.loads(b), indent=1)
            print(decoded)
        except Exception as error:
            print(f"Body not a json, size {len(b)}, error {error}")
            print(b)
        finally:
            print("-----------------------")




    def print_request(self):
        ...


def client(port):
    commands = [
        command0,
        command1,
        command2,
        command3,
    ]
    while True:
        prompt = input("Command> ")
        try:
            result = commands[int(prompt)](port)
            print(result)
        except Exception as e:
            print(e)


def server(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ServerHandler)
    httpd.serve_forever()



if __name__ == "__main__":
    parser = argparse.ArgumentParser("Tester")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--client", type=int, metavar='port', dest='client')
    group.add_argument("--server", action='store_const', const=True)
    args = parser.parse_args()
    if args.client:
        client(args.client)
    elif args.server:
        server(SELF_PORT)
