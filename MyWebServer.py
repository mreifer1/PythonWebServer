import socket
import sys
import threading
from datetime import datetime, timezone
import os
import time

serverPort = 8888
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
acceptedRequests = ["GET", "HEAD"]

def get_current_date():
    return datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

def parse_date(date_str):
    return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')

def respond(connectionSocket, address):
    request = connectionSocket.recv(1024).decode()

    if_modified_since = ''
    flag = False
    file_path = 'index.html'
    file_size = os.path.getsize(file_path)
    modification_time = os.path.getmtime(file_path)
    last_modified = time.gmtime(modification_time)
    formatted_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", last_modified)

    lines = request.split("\r\n")
    request_line = lines[0]
    method, Req_file_path, http_version = request_line.split()

    for line in lines:
        if line.startswith("If-Modified-Since"):
            flag = True
            if_modified_since = line.split(":", 1)[1].strip()
            break

    print("Request Method: ", method)
    print("Requested File: ", Req_file_path, "\n")

    file_last_modified_datetime = datetime.strptime(formatted_time, "%a, %d %b %Y %H:%M:%S GMT")
    
    if method not in acceptedRequests: # If the request is not a head or get req

        response = 'HTTP/1.1 501 Not Implemeneted\r\n'
        response += 'Date: ' +get_current_date() + '\r\n'
        response += 'Server: MyWebServer\r\n'
        response += "Content-Length: 0\r\n\r\n"

        print(f"Sending Response:\n\n{response}")
        connectionSocket.send(response.encode())
        connectionSocket.close()
        return 
    elif Req_file_path not in ['/', '/index.html']:

        response = 'HTTP/1.1 404 Not Found\r\n'
        response += 'Date: ' +get_current_date() + '\r\n'
        response += 'Server: MyWebServer\r\n'
        response += "Content-Length: 0\r\n\r\n"

        print(f"Sending Response:\n\n{response}")
        connectionSocket.send(response.encode())
        connectionSocket.close()
        return
    elif method == "HEAD": # head req
        
        response = 'HTTP/1.1 200 OK\r\n'
        response += 'Date: ' +get_current_date() + '\r\n'
        response += 'Connection: keep-alive\r\n'
        response += 'Server: MyWebServer (Windows)\r\n'
        response += f'Last-Modified: {formatted_time}\r\n'
        response += "Content-Length: 0\r\n\r\n" # head request / error requests content-length = 0 

        print(f"Sending Response:\n\n{response}")
        connectionSocket.send(response.encode())
        connectionSocket.close()
        return
    elif method == "GET": # get req

        if flag:
            if_modified_datetime = parse_date(if_modified_since)

            if file_last_modified_datetime <= if_modified_datetime:

                response = 'HTTP/1.1 304 Not Modified\r\n'
                response += 'Date: ' + get_current_date() + '\r\n'
                response += 'Server: MyWebServer\r\n'
                response += f'Content-Length: 0\r\n\r\n'

                print(f"Sending Response:\n\n{response}")
                connectionSocket.send(response.encode())
                connectionSocket.close()
                return
        
        file = open(file_path,'rb') 
        file_response = file.read() 

        response = 'HTTP/1.1 200 OK\r\n'
        response += 'Date: ' + get_current_date() + '\r\n'
        response += 'Connection: keep-alive\r\n'
        response += 'Server: MyWebServer\r\n'
        response += f'Last-Modified: {formatted_time}\r\n'
        response += f'Content-Length: {file_size}\r\n\r\n'

        
        final_response = response.encode() + file_response
        print(f"Sending Response:\n\n{final_response.decode()}")
        connectionSocket.send(final_response)
        connectionSocket.close()
        return

# start the web server
try:
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(('', serverPort))
    print("The server is ready to receive on port {port}.\n".format(port=serverPort))
except Exception as e:
    print("An error occurred on port {port}\n".format(port=serverPort))
    serverSocket.close()
    sys.exit(1)

serverSocket.listen(1)

# handle requests
while True:
    (connectionSocket, address) = serverSocket.accept()
    print("Received connection from {addr}\n".format(addr=address))
    threading.Thread(target=respond, args=(connectionSocket, address)).start()
