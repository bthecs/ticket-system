import json
import socket
from time import sleep


class Client:
    def __init__(self, port):
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.sock.connect(('127.0.0.1', port))
        self.main()

    def main(self):
        message = input('-> ')
        while message != 'exit':
            self.sock.send(message.encode())
            data = self.sock.recv(4096).decode()
            print(data)
            input('Press any key to continue...')
            message = input('\n-> ')
        sleep(1)
        self.sock.close()


if __name__ == "__main__":
    Client(55001)
