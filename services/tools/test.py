#!/usr/bin/env python

"""This is implementation of client for our queue.  Serves for development
purposes only. 
"""
import argparse
import http.client
import json
import tempfile
import os

from http.server import BaseHTTPRequestHandler, HTTPServer

FILE1 = """
#include <iostream>

int main() {
    std::cout << "Hello world";
}
"""

FILE2 = ""
with open("../../tester/example/submission.cpp", "r") as f:
    FILE2 = f.read()

def command(returnUrl, docker, addr, customCmd):
    message = {
        "returnUrl" : returnUrl,
        "dockerImage": docker,
        "maxRunTime": 300,
    }

    customCmd(message)

    connection = http.client.HTTPConnection(addr, timeout=10)
    connection.request("POST", "/test", json.dumps(message))
    response = connection.getresponse()
    return f"Response status: {response.status}"    


def command0(message):
    message.update({
        "files": {
            "main.cpp": "Not a C++ source!",
        },
    })

def command1(message):
    message.update({
        "files": {
            "main.cpp": FILE1,
        },
    })

def command2(message):
    message.update({
        "files": {
            "main.cpp": FILE2,
        },
    })

def command3(message):
    message.update({
        "memory": 1000 * 1000 * 1000,
        "files": {
            "main.cpp": FILE2,
        },
    })

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
        self.end_headers()

        self.wfile.write(response)
        b = bytearray(int(self.headers['content-length']))
        self.rfile.readinto(b)

        try:
            fd, path = tempfile.mkstemp(prefix='queued-test', suffix='.json')

            try:
                with open(path, 'wb') as f:
                    f.write(b)
                print('Message logged to', path)
            finally:
                os.close(fd)

        except Exception as error:
            print(f"Body not a json, size {len(b)}, error {error}")
            print(b)





    def print_request(self):
        ...


def client(args):
    returnUrl = 'localhost:' + str(args.returnPort)

    commands = [
        command0,
        command1,
        command2,
        command3,
    ]
    print("Select command 0..", len(commands), sep='')
    while True:
        prompt = input("Command> ")
        try:
            print(command(returnUrl, args.docker, args.url + ':' + str(args.port), commands[int(prompt)]))
        except Exception as e:
            print(e)


def server(args):
    server_address = ('', args.port)
    httpd = HTTPServer(server_address, ServerHandler)
    httpd.serve_forever()



if __name__ == "__main__":
    parser = argparse.ArgumentParser("Tester")

    subparsers = parser.add_subparsers()

    parser_client = subparsers.add_parser('client')
    parser_client.add_argument('--url', type=str, default='')
    parser_client.add_argument('--port', type=int, required=True)
    parser_client.add_argument('--docker', type=str, required=True)
    parser_client.add_argument('--returnPort', type=int, required=True)
    parser_client.set_defaults(func=client)

    parser_server = subparsers.add_parser('server')
    parser_server.add_argument('--port', type=int, required=True)
    parser_server.set_defaults(func=server)

    args = parser.parse_args()
    args.func(args)
