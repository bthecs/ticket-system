import json
import sys
import socket
import getopt
from time import sleep


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.sock.connect((host, port))
        self.main()

    def main(self):
        message = input('-> ')
        while True:
            self.sock.send(message.encode())
            data = self.sock.recv(4096).decode()
            print(data)
            if data == "Bye": break
            message = input('\n-> ')


if __name__ == "__main__":
    
    (opt, arg) = getopt.getopt(sys.argv[1:], 'h:p:')
    
    host = '127.0.0.1'
    port = 8080
    
    for (op, ar) in opt:
        if op == '-h':
            host = str(ar)
        if op == '-p':
            port = int(ar)

    Client(host, port)
