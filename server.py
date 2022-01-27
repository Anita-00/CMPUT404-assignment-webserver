#  coding: utf-8 
import re
import socketserver
import subprocess
import os.path
from os import path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.byte_data = self.request.recv(1024).strip()

        print ("Got a request of: %s\n" % self.byte_data)

        # removes spaces
        self.data = self.byte_data.replace(b' ', b'')

        # get method and check if valid
        method = self.parse_req_method(self.data)
        method_isvalid = self.check_method_valid(method)

        # get requested page and check if valid
        req_page = self.parse_req_page(self.data, method)
        isPath, req_page_full, content_type = self.check_page_valid(req_page)

        self.handle_page(req_page_full, content_type, isPath, method_isvalid)
    
    def parse_req_method(self, data):
        # gets the method called by the client

        method = data.split(b'/')[0]
        return method
    
    def parse_req_page(self, data, method):
        # gets the page requested by the client

        method_len = len(method)
        HTTP_start = data.find(b'HTTP')
        req_page = data[method_len:HTTP_start]

        return req_page

    def check_method_valid(self, method):
        # check that the requested method is GET
        # other types are not supported

        if method != b'GET':
            return False
        else:
            return True
    
    def check_page_valid(self, req_page):
        # checks if the page/directory exists in www folder

        root = b"./www"
        req_page_full = root + req_page

        # set default values
        content_type = None
        isPath = 200 # path is OK

        abs_path = path.abspath(req_page_full)

        if path.exists(req_page_full) and b'www' in abs_path:
            # check if secure

            if path.isfile(req_page_full):
                # get extension of file
                name, ext = path.splitext(req_page_full)

                if ext == b'.html':
                    content_type = 'text/html'

                elif ext == b'.css':
                    content_type = 'text/css'

            elif path.isdir(req_page_full):

                # if directory, set index.html page to open
                if str(req_page_full)[-2] == '/':
                    content_type = 'text/html'
                    #req_page_full = root + req_page + b'index.html'
                    req_page_full += b'index.html'
                else:
                    # if missing /, add to the end and redirect error
                    req_page_full = req_page + b'/'
                    isPath = 301

        else:
            # path is not found
            isPath = 404
        
        return isPath, req_page_full, content_type


    def handle_page(self, req_page_full, content_type, isPath, method_isvalid):
        
        connection = "close"
        str_page = req_page_full.decode()

        if method_isvalid == False:
            self.request.sendall(bytearray(f"HTTP/1.1 405 Method Not Allowed\r\nConnection: {connection}\r\n\r\n",'utf-8'))
        elif isPath == 301:
            print("301 error")
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation: {str_page}\r\nConnection: {connection}\r\n\r\n",'utf-8'))
        elif isPath == 404:
            self.request.sendall(bytearray(f"HTTP/1.1 404 Not Found\r\nConnection: {connection}\r\n\r\n",'utf-8'))
        elif isPath == 200:           
            page_file = open(req_page_full, "r")
            page_read = page_file.read()
            page_length = len(page_read)     
            
            self.request.sendall(bytearray(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {page_length}\r\nConnection: {connection}\r\nLocation: {str_page}\r\n\r\n",'utf-8'))
            self.request.sendall(bytes(page_read, encoding='utf8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
