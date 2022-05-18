import socket
import getopt
import json
import threading
import sys
from urllib import response
from src.model.ticket import Ticket
from src.database import Database
from src.utils import parse_message, make_response
from logger import Logger


class ClientHandler():
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.db = Database().get_database()
        self.commands = {
            'create': self.create,
            'list': self.list,
            'update': self.update,
            'delete': self.delete,
            'exit': self.exit,
        }
        self.main()

    def create(self, args):
        (opt, arg) = getopt.getopt(args[0:], 't:a:d:')

        data = dict()

        if args:
            if (len(args)) == 6:
                for (op, ar) in opt:
                    if op == "-t":
                        data['title'] = ar
                    if op == '-a':
                        data['author'] = ar
                    if op == '-d':
                        data['description'] = ar
            else:
                logger.error(
                    f'Insuficient arguments by {self.address[0]}:{self.address[1]}!')
                response = make_response(
                    404, f'Insuficient arguments. Try again!')
                self.socket.send(response.encode())
                return
        else:
            logger.error(
                f'No arguments found by {self.address[0]}:{self.address[1]}!')
            response = make_response(404, f'No arguments found. Try again!')
            self.socket.send(response.encode())
            return

        ticket = Ticket(
            title=data.get('title'),
            author=data.get('author'),
            description=data.get('description'),
            status='pending',
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.close()
        logger.info(
            f'Ticket created successfully by {self.address[0]}:{self.address[1]}!')
        response = make_response(201, f'Ticket created successfully!')
        self.socket.send(response.encode())

    def list(self, args):
        (opt, arg) = getopt.getopt(args[0:], 't:a:s:d:')

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
                    tickets = tickets.filter(
                        Ticket.date_created.like(f'%{ar}%'))

        self.db.close()
        data = json.dumps(
            {"tickets": [ticket.to_json() for ticket in tickets]}, sort_keys=True, indent=4)
        response = make_response(200, data)
        self.socket.send(response.encode())

    def update(self, args):
        (opt, arg) = getopt.getopt(args[0:], 'i:t:d:s:')

        data = dict()

        if args:

            if not '-i' in args:
                logger.error(
                    f'Id not found in the arguments by {self.address[0]}:{self.address[1]}!')
                response = make_response(
                    404, f'Id not found in the arguments. Try again!')
                self.socket.send(response.encode())
                return

            for (op, ar) in opt:
                if op == '-i':
                    data['id'] = ar
                if op == '-t':
                    data['title'] = ar
                if op == '-d':
                    data['description'] = ar
                if op == '-s':
                    data['status'] = ar
        else:
            logger.error(
                f'No arguments found by {self.address[0]}:{self.address[1]}!')
            response = make_response(404, f'No arguments found. Try again!')
            self.socket.send(response.encode())

        ticket = self.db.query(Ticket).get(data.get('id'))

        for key, value in data.items():
            setattr(ticket, key, value)

        self.db.add(ticket)
        self.db.commit()
        self.db.close()
        logger.info(
            f'Ticket updated successfully by {self.address[0]}:{self.address[1]}!')
        response = make_response(200, f'Ticket updated successfully!')
        self.socket.send(response.encode())

    def delete(self, args):
        (opt, arg) = getopt.getopt(args[0:], 'i:')
        for (op, ar) in opt:
            if op == '-i':
                _id = ar
        ticket = self.db.query(Ticket).get(_id)
        self.db.delete(ticket)
        self.db.commit()
        self.db.close()
        logger.info(
            f'Ticket deleted successfully by {self.address[0]}:{self.address[1]}!')
        response = make_response(200, f'Ticket deleted successfully!')
        self.socket.send(response.encode())

    def exit(self, _):
        logger.info(f'Client {self.address} disconnected!')
        response = make_response(499, f'Client disconnected!')
        self.socket.send(response.encode())
        self.socket.close()
        raise SystemExit

    def main(self):
        try:
            while True:
                message = self.socket.recv(1024).decode()
                command, args = parse_message(message)
                if command in self.commands:
                    logger.info(f'Executing command: {command}')
                    self.commands[command](args)
                else:
                    logger.error(f'Command not found: {command}')
                    response = make_response(
                        404, f'Command not found: {command}. Try again!')
                    self.socket.send(response.encode())
        except SystemExit:
            pass


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.create_socket()
        self.handle_accept()

    def create_socket(self):
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.info(
            f'Socket created successfully on {(self.host)}:{self.port}!')
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    def handle_accept(self):
        logger.info('Accepting connections')
        while True:
            client, address = self.server.accept()
            logger.info(f'Connection from {address[0]}:{address[1]}')
            thread = threading.Thread(
                target=ClientHandler, args=(client, address))
            thread.start()


if __name__ == "__main__":

    (opt, arg) = getopt.getopt(sys.argv[1:], 'h:p:d:')
    host = '127.0.0.1'
    port = 8080
    debug = False

    for (op, ar) in opt:
        if op == '-h':
            host = str(ar)
        if op == '-p':
            port = int(ar)
        if op == '-d':
            if ar.lower() == 'true':
                debug = True

    Database()
    logger = Logger(debug=debug or False)
    Server(host, port)
