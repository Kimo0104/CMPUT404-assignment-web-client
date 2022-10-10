#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
    
    def __repr__(self) -> str:
        return self.code +'\n' + self.body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split("\r\n")[0].split(" ")[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_url(self, url):
        
        parsed_url = urllib.parse.urlparse(url)

        port = parsed_url.port
        path = parsed_url.path
        host = parsed_url.hostname
        port = port if port else 80
        path = path if (path != "" and path) else "/"
        #In the case the user doesnt enter http://
        #then the host name is None and is contained in the path
        if host is None:
            slash_idx = path.find('/')
            if slash_idx == -1:
                host = path
                path = "/"
            else:
                host = path[:slash_idx]
                path = path[slash_idx:]

        return host, path, port

    def GET(self, url, args=None):
        host, path, port = self.parse_url(url)
        self.connect(host, port)

        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}:{port}\r\n"
        request += "Connection: close\r\n\r\n"

        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def encode_args(self,args):
        encoded_args = ""
        for k, v in args.items():
            encoded_args += f"{k}={v}&"
        encoded_args = encoded_args[:-1]
        return encoded_args

    def POST(self, url, args=None):
        host, path, port = self.parse_url(url)
        self.connect(host, port)

        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}:{port}\r\n"
        request += "Connection: close\r\n"

        encoded_args = self.encode_args(args) if args else ""
        print(encoded_args)
        if args:
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            request += f"Content-Length: {len(encoded_args.encode('utf-8'))}\r\n\r\n"
        else: request += "Content-Length: 0\r\n\r\n"

        request += encoded_args

        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        return HTTPResponse(self.get_code(response), self.get_body(response))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
