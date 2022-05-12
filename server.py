import socket
import getopt
import json
import threading

from src.model.ticket import Ticket
from src.database import Database
from src.utils import parse_message

clients = []


class ClientHandler:
    def __init__(self, server, sock, address):
        self.server = server
        self.socket = sock
        self.address = address
        self.disconnect = False
        self.db = Database().get_database()
        self.commands = {
            'create': self.create,
            'list': self.list,
            'update': self.update,
            'delete': self.delete,
            'exit': self.exit,
            'export': self.export,
        }
        self.main()

    def remove(self, client):
        clients.remove(client)
        print(f'Client quit!')
        print(f'Clients connected: {len(clients)}')

    def broadcast(self, message):
        print(message)
        for client in clients:
            client.send(message.encode())

    def create(self, args):
        (opt, arg) = getopt.getopt(args[0:], 't:a:d')

        data = dict()

        if args:
            for (op, ar) in opt:
                if op == "-t":
                    data['title'] = ar
                if op == '-a':
                    data['author'] = ar
                if op == '-d':
                    data['description'] = ar

        ticket = Ticket(
            title=data.get('title'),
            author=data.get('author'),
            description=data.get('description'),
            status='pending',
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.close()
        self.broadcast(f'Ticket created successfully by {self.address[0]}:{self.address[1]}!')

    def list(self, args):
        (opt, arg) = getopt.getopt(args[0:], 't:a:s:d')

        tickets = self.db.query(Ticket)
        if args:
            for (op, ar) in opt:
                if op == "-t":
                    tickets = tickets.filter(Ticket.title.like(f'%{ar}%'))
                if op == '-a':
                    tickets = tickets.filter(Ticket.author.like(f'%{ar}%'))
                if op == '-s':
                    tickets = tickets.filter(Ticket.status.like(f'%{ar}%'))
                if op == '-d':
                    tickets = tickets.filter(Ticket.date_created.like(f'%{ar}%'))

        self.db.close()
        data = json.dumps({"tickets": [ticket.to_json() for ticket in tickets]})
        self.socket.send(data.encode())

    def update(self, args):
        (opt, arg) = getopt.getopt(args[0:], 'i:t:d')

        data = dict()

        for (op, ar) in opt:
            if op == '-i':
                data['id'] = ar
            if op == '-t':
                data['title'] = ar
            if op == '-d':
                data['description'] = ar

        ticket = self.db.query(Ticket).get(data['id'])

        data['title'] = data.get('title') if None else ticket.title
        data['description'] = data.get('description') if None else ticket.description

        status = input("\nNew status? ")
        ticket_updated = dict(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description'),
            author=ticket.author,
            status=status,
        )

        for key, value in ticket_updated.items():
            setattr(ticket, key, value)

        self.db.add(ticket)
        self.db.commit()
        self.db.close()
        self.socket.send("Ticket changed successfully".encode())

    def delete(self, args):
        (opt, arg) = getopt.getopt(args[0:], 'i:')
        for (op, ar) in opt:
            if op == '-i':
                _id = ar
        ticket = self.db.query(Ticket).get(_id)
        self.db.delete(ticket)
        self.db.commit()
        self.db.close()
        self.socket.send("Ticket deleted successfully".encode())

    def exit(self, _):
        self.remove(self.socket)
        self.disconnect = True
        self.socket.close()

    def export(self, _):
        pass

    def main(self):
        while not self.disconnect:
            message = self.socket.recv(1024).decode()
            command, args = parse_message(message)
            if command in self.commands:
                print(f'Executing command: {command}')
                self.commands[command](args)


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
        self.server.settimeout(5)
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
