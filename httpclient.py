#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, Anders Johnson
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

class HTTPClient(object):
    def get_host_port_path(self,url):
        # Returns the host, port and path from the url string.
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme not in ('http', 'https'):
            # We need to specify the scheme in the URL in order to parse and send it.
            # We assume that http is requested.
            url = 'http://' + url
            return self.get_host_port_path(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        if port == None:
            # We assume we are trying to access port 80 if there is no port defined.
            port = 80
        if path == '':
            # We didn't request anything... so let's request /
            path = '/'
        return (host, port, path)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # Given an HTTP response, returns the status code
        return int(data.split(' ')[1])

    def get_headers(self,data):
        # Given an HTTP response, returns the headers
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        # Given an HTTP response, returns the body
        body_start = data.find('\r\n\r\n') + len('\r\n\r\n')
        body = data[body_start:]
        return body
    
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

    def GET(self, url, args=None):
        host, port, path = self.get_host_port_path(url)
        self.connect(host, port)
        data = "GET %s HTTP/1.1\r\nHost: %s:%s\r\nConnection: close\r\n\r\n" % (path, host, port)
        self.sendall(data)
        response = self.recvall(self.socket)
        # We strip out the code and body, and send as an HTTPResponse.
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Let's encode the args as a url string, to start
        if args:
            body = urllib.parse.urlencode(args)
        else:
            body = ''
        host, port, path = self.get_host_port_path(url)
        self.connect(host, port)
        content_length = len(body.encode('utf-8'))
        data = "POST %s HTTP/1.1\r\nHost: %s:%s\r\nContent-Type: application/x-222-form-urlencoded\r\nContent-Length: %s\r\nConnection: close\r\n\r\n%s" % (path, host, port, content_length, body)
        self.sendall(data)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

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
        print(client.command( sys.argv[2], sys.argv[1] ).body)
    else:
        print(client.command( sys.argv[1] ).body)
