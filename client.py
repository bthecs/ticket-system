import json
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 55001))

while True:
    message = input('-> ')
    sock.send(message.encode('utf-8'))
    # command = message[0].split() if message == type(list) else message

    command = sock.recv(1024).decode('utf-8')

    if command == 'create':
        title = input('title? ')
        author = input('Author? ')
        description = input('description? ')
        ticket = json.dumps(dict(
            title=title,
            author=author,
            status='pending',
            description=description,
        ))
        sock.send(ticket.encode('utf-8'))

    elif command == 'update':
        ticket_json = json.loads(sock.recv(1024).decode('utf-8'))
        for key, value in ticket_json.items():
            print(f'{key}: {value}')

        title = input('Title? ')
        description = input('Description? ')

        ticket_updated = json.dumps(dict(
            id=ticket_json.get('id'),
            title=ticket_json.get('title') if not title else title,
            author=ticket_json.get('author'),
            status=ticket_json.get('status'),
            description=ticket_json.get('description') if not description else description,
        ))
        sock.send(ticket_updated.encode('utf-8'))

    elif command == 'list':
        tickets = json.loads(sock.recv(4096).decode('utf-8'))
        if "tickets" in tickets.keys():
            for ticket in tickets['tickets']:
                print(f"""
                ###################################
                N° {ticket.get('id')}
                Title: {ticket.get('title')}
                Author: {ticket.get('author')}
                Status: {ticket.get('status')}
                Description: {ticket.get('description')}
                Date Created: {ticket.get('date_created')}""")
        else:
            print(tickets["error"])
