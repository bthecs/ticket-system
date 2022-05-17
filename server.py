import socket
import getopt
import json
import threading
import sys
from src.model.ticket import Ticket
from src.database import Database
from src.utils import parse_message
from logger import Logger

clients = []



# TODO: config.cfg config.ini config.json "server -c config.ini"
# TODO: Response JSON like tcp
# TODO: Fix broadcast



class ClientHandler():
    def __init__(self, server, sock, address):        
        self.server = server
        self.socket = sock
        self.address = address
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
        logger.info(f'Ticket created successfully by {self.address[0]}:{self.address[1]}!')
        self.server.broadcast(f'Ticket created successfully by {self.address[0]}:{self.address[1]}!')

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
        if args:
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
            logger.error(f'No arguments found by {self.address[0]}:{self.address[1]}!')
            self.socket.send("Enter a valid arguments".encode())

        ticket = self.db.query(Ticket).get(data['id'])

        data['title'] = data.get('title') if None else ticket.title
        data['description'] = data.get('description') if None else ticket.description
        data['status'] = data.get('status') if None else ticket.status
        
        ticket_updated = dict(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description'),
            author=ticket.author,
            status=data.get('status'),
        )

        for key, value in ticket_updated.items():
            setattr(ticket, key, value)

        self.db.add(ticket)
        self.db.commit()
        self.db.close()
        logger.info(f'Ticket updated successfully by {self.address[0]}:{self.address[1]}!')
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
        logger.info(f'Ticket deleted successfully by {self.address[0]}:{self.address[1]}!')
        self.socket.send("Ticket deleted successfully".encode())

    def exit(self, _):
        logger.info(f'Client {self.address} disconnected!')
        self.socket.send("Bye".encode())
        self.server.remove(self.socket)
        
        

    def export(self, _):
        pass

    def main(self):
    
        while True:
            message = self.socket.recv(1024).decode()
            if not message: break
            command, args = parse_message(message)
            if command in self.commands:
                logger.info(f'Executing command: {command}')
                self.commands[command](args)
            else:
                logger.error(f'Command not found: {command}')
                self.socket.send("Enter a valid command".encode())
                    


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
        self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        logger.info(f'Socket created successfully on {(self.host)}:{self.port}!')
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        
    def remove(self, client):
        clients.remove(client)
        logger.info(f'Clients connected: {len(clients)}')

    def broadcast(self, message):
        for client in clients:
            client.send(message.encode())

    def handle_accept(self):
        logger.info('Accepting connections')
        while True:
            client, address = self.server.accept()
            logger.info(f'Connection from {address[0]}:{address[1]}')
            thread = threading.Thread(target=ClientHandler, args=(self, client, address))
            thread.start()
            clients.append(client)


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
