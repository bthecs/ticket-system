# 🧐 Overview
The purpose of this project is to load tickets onto a server, making use of client-server communication, and then save them in a database.

**Table of Contents**

- [🧰 Install](#-install)
- [🚀 Usage](#-usage)
  * [👨‍🔧 Client actions](#-client-actions)
    + [Create](#create)
    + [Update](#update)
    + [Delete](#delete)
    + [List](#list)
    + [Exit](#exit)
- [🚨 Protocol](#-protocol)

# 🧰 Install

To install and run this program you will need to have:
- python3
- pip3
- python3-venv

The next step is the cloning of the repository:

```bash
git clone https://github.com/bthecs/ticket-system.git
```
Once the repository has been created, the virtual environment must be created within it:

```bash
python3 -m venv venv
```
Once the virtual environment has been created, it must be activated as follows:

```bash
source ven/bin/activate
```
once inside the environment, the last step is the installation of the requirements:

```bash
pip3 install -r requirements.txt
```

# 🚀 Usage
To start the server there are two possibilities to run the server.py and it will take the default values or in case you want to modify the host and the port you have to pass by arguments its values.

- -h:  This argument will be used to indicate the host we want to run the server on.
- -p: this argument will be used to indicate the port we want to run the server on.
- -d: this argument is optional and can be used to display the logs through the terminal.

Example of server execution with default values:

```bash
python3 server.py
```
Example of server execution with modified values:

```bash
python3 server.py -h 192.0.0.1 -p 8080 -d True
```
To start the client there are two possibilities to run the client.py and it will take the default values or in case you want to modify the host and the port you have to pass by arguments its values.

- -h: This argument will be used to indicate the host we want to run the client on
- -p: This argument will be used to indicate the port we want to run the client on

Example of client execution with default values:

```bash
python3 client.py
```

Example of server execution with modified values:

```bash
python3 client.py -h 192.0.0.1 -p 8080
```
## 👨‍🔧 Client actions
Once the connection to the server is established, the client will be able to perform different actions through the CLI, these are:

- Create
- Update
- Delete
- List
- Exit

### Create
The client will be able to create a ticket through the create command accompanied by the arguments title, author and description, these fields must be filled in or the ticket will not be created.
Arguments:

- -t: This argument is used to indicate the title to be assigned to the ticket.
- -a: This argument is used to indicate the author you want to assign to the ticket.
- -d: This argument is used to indicate the description to be assigned to the ticket.

example of ticket creation:

```bash
create -t "title" -a "author" -d "description"
```

### Update
The client will be able to modify a ticket through the update command which will bring a ticket by its id and will be able to modify the fields that we want.
Arguments:

- -i: This argument is used to indicate the id assigned to a ticket.
- -t: This argument is used to indicate the title to be assigned to the ticket.
- -a: This argument is used to indicate the author you want to assign to the ticket.
- -d: This argument is used to indicate the description to be assigned to the ticket.
- -s: This argument is used to indicate the status to be assigned to the ticket.

```bash
update -i 1 -t "title" -a "author" -d "description"
```

### Delete
The client will be able to delete a ticket through the delete command than delete a ticket by its id.
Arguments:

- -i: This argument is used to indicate the id assigned to a ticket.

```bash
delete -i 1
```

### List
With this command the client can list all the tickets created so far or he can list certain tickets filtering by title, author and description.
Arguments:

- -t: This argument is used to indicate the title to be assigned to the ticket.
- -a: This argument is used to indicate the author you want to assign to the ticket.
- -d: This argument is used to indicate the description to be assigned to the ticket.

```bash
list
```
or
```bash
list -t "Hello"
```

### Exit
With this command the client will be able to exit the server without passing any arguments.

```bash
exit
```

# 🚨 Protocol
The socket used to perform the interconnection is AF_INET is used to designate the type of addresses with which its socket can communicate (in this case, Internet Protocol v4 addresses) and SOCK_STREAM type of the socket, dependent on the previous parameter (not all domains support the same types). In this case, a socket of type STREAM: using the TCP protocol, provides certain security guarantees: packets arrive in order, discarding repeated and/or corrupted packets.

![Socket](https://i.imgur.com/sAyHJ3E.jpeg)
