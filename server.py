import socket
import threading
from src.database import Database
from src.commands import Command

clients = []


class ClientHandler:
    def __init__(self, server, sock, address):
        self.server = server
        self.sock = sock
        self.address = address
        self.main()

    def remove(self, client):
        clients.remove(client)
        print(f'Client quit!')
        print(f'Clients connected: {len(clients)}')

    def broadcast(self, message):
        print(message)
        for client in clients:
            client.send(message.encode())

    def parse_message(self, message):
        args = message.split()
        command = args.pop(0)
        print(f'\nArgumentos: {args}')
        print(f'Comando: {command}')
        return command, args

    def main(self):
        while True:
            message = self.sock.recv(1024).decode()
            command, args = self.parse_message(message)
            Command(self, command, args)
            if command == 'exit':
                break


class Server:
    def __init__(self, port):
        self.server = None
        self.port = port
        self.commands = ["create", "update", "list", "delete"]
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

    def handle_accept(self):
        print('Accepting connections')
        while True:
            client, address = self.server.accept()
            thread = threading.Thread(target=ClientHandler, args=(self, client, address))
            thread.start()
            clients.append(client)


if __name__ == "__main__":
    Database()
    Server(55001)
