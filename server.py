import json
import socket
import threading
from src.database import init_db, conn
from src.database import Ticket


class Server:

    def __init__(self, port=55001):
        self.port = port
        self.socket = None
        self.commands = ["create", "update", "list", "delete"]

    def connect(self) -> None:
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.socket.bind(('', self.port))
        self.socket.listen(1)

        while True:
            client_conn, address = self.socket.accept()
            thread = threading.Thread(target=self.handler, args=(client_conn, address), daemon=True)
            thread.start()

    def handler(self, client_conn, address: tuple) -> None:
        db = conn()
        print(f"Client connected ({address[0]}:{address[1]})")
        while True:
            message = client_conn.recv(1024).decode('utf-8')
            args = message.split()  # ['list', '--title', 'harry']
            command = args.pop(0)  # 'list'
            print(f'Argumentos: {args}')
            print(f'Comando: {command}')

            client_conn.send(command.encode('utf-8'))

            if command == 'create':

                ticket_json = json.loads(client_conn.recv(1024).decode('utf-8'))
                self.create(ticket_json)

            elif command == 'update':
                id = int(args.pop())
                ticket = db.query(Ticket).get(id)

                client_conn.send(json.dumps(ticket.to_json()).encode('utf-8'))
                ticket_json = json.loads(client_conn.recv(1024).decode('utf-8'))
                self.update(ticket_json, ticket)

            elif command == 'list':
                tickets = self.list(args)
                client_conn.send(json.dumps(tickets).encode('utf-8'))

            elif command == 'delete':
                id = int(args[0])
                ticket = db.query(Ticket).get(id)
                self.delete(ticket)
            elif command == 'exit':
                print(f'Client disconnected ({address[0]}:{address[1]})')
                client_conn.close()

    def create(self, ticket_json):
        db = conn()
        ticket = Ticket.from_json(ticket_json)
        try:
            db.add(ticket)
            db.commit()
            db.close()
            return 'Ticket created successfully'
        except Exception as error:
            db.close()
            return str(error)

    def update(self, ticket_json, ticket):
        db = conn()
        for key, value in ticket_json.items():
            setattr(ticket, key, value)
        db.add(ticket)
        try:
            db.commit()
            db.close()
            return ticket.to_json()
        except Exception as error:
            return str(error)

    def list(self, args):
        db = conn()
        tickets = db.query(Ticket)
        if not args:
            tickets = tickets.order_by(Ticket.date_created.desc())
        elif args[0] in ('--title', '-t'):
            tickets = tickets.filter(Ticket.title.like(f'%{args[1]}%'))
        elif args[0] in ('--author', '-a'):
            tickets = tickets.filter(Ticket.author.like(f'%{args[1]}%'))
        elif args[0] in ('--status', '-s'):
            tickets = tickets.filter(Ticket.status.like(f'%{args[1]}%'))
        elif args[0] in ('--date', '-d'):
            tickets = tickets.filter(Ticket.date_created.like(f'%{args[1]}%'))
        else:
            return {"error": "Filter not found"}
        return {"tickets":[ticket.to_json() for ticket in tickets]}

    def delete(self, ticket):
        db = conn()
        db.delete(ticket)
        db.commit()
        db.close()
        return 'Delete successfully'

    def run(self):
        self.connect()


if __name__ == "__main__":
    init_db()
    Server().run()
