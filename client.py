import sys
import socket
import getopt
from src.utils import parse_request


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.sock.connect((host, port))
        self.main()

    def main(self):
        while True:
            message = input('\n-> ')
            if not message:
                continue
            self.sock.send(message.encode())
            data = self.sock.recv(4096).decode()
            status_code, response = parse_request(data)

            if status_code in [200, 201]:
                print(response)
            if status_code in [400, 404]:
                print(response)
            if status_code in [499]:
                print(response)
                break


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
