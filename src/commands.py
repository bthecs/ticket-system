from src.database import Ticket, Database
import getopt
import json


class Command:
    def __init__(self, client, command, args):
        self.COMMANDS = {
            'create': self.create,
            'list': self.list,
            'update': self.update,
            'delete': self.delete,
            'exit': self.exit,
        }
        self.command = command
        self.args = args
        self.db = Database().get_database()
        self.client = client
        self.execute()

    def execute(self):
        print(f'Executing command: {self.command}')
        if self.command in self.COMMANDS:
            self.client.send(self.command.encode())
            self.COMMANDS[self.command](self.args)

    def create(self, _):
        ticket_json = json.loads(self.client.recv(1024).decode())
        ticket = Ticket(
            title=ticket_json.get("title"),
            author=ticket_json.get("author"),
            description=ticket_json.get("description"),
            status='pending',
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.close()
        self.client.send('Ticket created successfully!'.encode())

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
        self.client.send(data.encode())

    def update(self, args):
        (opt, arg) = getopt.getopt(args[0:], 'i:')
        for (op, ar) in opt:
            if op == '-i':
                _id = ar

        ticket = self.db.query(Ticket).get(_id)
        print(ticket.to_json())
        self.client.send(json.dumps(ticket.to_json()).encode())
        ticket_json = json.loads(self.client.recv(1024).decode())
        for key, value in ticket_json.items():
            setattr(ticket, key, value)
        self.db.add(ticket)
        self.db.commit()
        self.db.close()
        self.client.send("Ticket changed successfully".encode())

    def delete(self, args):
        (opt, arg) = getopt.getopt(args[0:], 'i:')
        for (op, ar) in opt:
            if op == '-i':
                _id = ar
        ticket = self.db.query(Ticket).get(_id)
        self.db.delete(ticket)
        self.db.commit()
        self.db.close()
        self.client.send("Ticket deleted successfully".encode())

    def exit(self, _):
        self.client.close()
