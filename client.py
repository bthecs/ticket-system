import json
import socket


class Client:
    def __init__(self, port):
        self.COMMANDS = {
            'create': self.create,
            'list': self.list,
            'update': self.update,
            'delete': self.delete,
            'exit': self.exit
        }
        self.sock = None
        self.command = None
        self.port = port
        self.create_socket()
        self.main()

    def create_socket(self):
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.sock.connect(('127.0.0.1', self.port))

    def main(self):
        while True:
            message = input('-> ')
            self.sock.send(message.encode())
            self.command = self.sock.recv(1024).decode()
            if self.command in self.COMMANDS:
                self.COMMANDS[self.command]()


    def create(self):
        title = input('title? ')
        author = input('Author? ')
        description = input('description? ')
        ticket = json.dumps(dict(
            title=title,
            author=author,
            description=description,
        ))
        self.sock.send(ticket.encode())
        print(self.sock.recv(1024).decode())

    def list(self):
        print(self.sock.recv(1024).decode())

    def update(self):
        ticket_json = json.loads(self.sock.recv(1024).decode())
        for key, value in ticket_json.items():
            print(f'{key}: {value}')
        title = input('Title? ')
        description = input('Description? ')
        ticket_updated = dict(
            id=ticket_json.get('id'),
            title=ticket_json.get('title') if not title else title,
            description=ticket_json.get('description') if not description else description,
            author=ticket_json.get('author'),
            status=ticket_json.get('status'),
        )
        self.sock.send(json.dumps(ticket_updated).encode('utf-8'))
        self.sock.recv(1024).decode()

    def delete(self):
        self.sock.recv(1024).decode()

    def exit(self):
        self.sock.close()


if __name__ == "__main__":
    Client(55001)
