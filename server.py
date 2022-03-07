import socket
import threading
from src.database import Database
from src.commands import Command


class ClientHandler:
    def __init__(self, server, sock, address):
        self.server = server
        self.sock = sock
        self.address = address
        self.main()

    def parse_message(self, message):
        args = message.split()
        command = args.pop(0)
        print(f'Argumentos: {args}')
        print(f'Comando: {command}')
        return command, args

    def main(self):
        while True:
            message = self.sock.recv(1024).decode()
            command, args = self.parse_message(message)
            if command == 'exit': break
            Command(self.sock, command, args)
        # self.server.remove(self)


class Server:
    def __init__(self, port):
        self.server = None
        self.port = port
        self.commands = ["create", "update", "list", "delete"]
        self.clients = []
        self.create_socket()
        self.handle_accept()

    def create_socket(self):
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        print('Server Socket created!')
        self.server.bind(('', self.port))
        self.server.listen(5)

    # def remove(self, client):
    #     self.clients.remove(client)
    #     # self.broadcast(f'Client {client.address} quit!\n')
    #     print(f'Client {client.address} quit!\n')
    #
    # def broadcast(self, message):
    #     for client in self.clients:
    #         client.sock.send(message.encode())

    def handle_accept(self):
        print('Accepting connections')
        while True:
            client, address = self.server.accept()
            thread = threading.Thread(target=ClientHandler, args=(self, client, address))
            thread.start()
            self.clients.append(thread)


if __name__ == "__main__":
    Database()
    Server(55001)
