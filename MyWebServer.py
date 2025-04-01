import socket
import sys
import threading
from datetime import datetime, timezone

serverPort = 8888
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
acceptedRequests = ["GET", "HEAD"]

def get_current_date():
    return datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

def respond(connectionSocket, address):
    request = connectionSocket.recv(1024).decode()

    lines = request.split("\r\n")
    request_line = lines[0]
    method, file_path, http_version = request_line.split()    

    for line in lines:
        print(line)

    
    if method not in acceptedRequests: # If the request is not a head or get req

        response = 'HTTP/1.1 501 Not Implemeneted\r\n'
        response += 'Date: ' +get_current_date() + '\r\n'
        response += 'Connection: keep-alive\r\n'
        response += 'Server: MyWebServer\r\n'
        response += "Content-Length: 0\r\n\r\n"

        print(f"Sending Response:\n{response}")
        connectionSocket.send(response.encode())
        connectionSocket.close()
        return 
    
    response = 'HTTP/1.1 200 OK\r\n'
    response += 'Date: ' +get_current_date() + '\r\n\r\n'

    print(f"Sending Response to client:\n\n{response}")

    connectionSocket.send(response.encode())
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
