import socket
import sys

server_url = 'vega.ii.uam.es'
server_port = 8000

def connect_to_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (server_url, server_port)
    sock.connect(server_address)

    return sock

def list_users(sock):
    command = 'LIST_USERS'
    sock.sendall(command.encode())
    data = sock.recv(4096).decode()

    ret = data.split(' ')
    if (ret[0] != 'OK'):
        print('Error con la peticion')
        print(data)
        return

    num = ret[2]
    list = data[len('OK USERS_LIST ') + len(str(num)) + 1:]
    list = list.split('#')

    array = []
    for entry in list:
        [name, ip, port, time] = entry.split(' ')

        user = {
        'name': name,
        'ip': ip,
        'port': port,
        'time': time
        }
        array.append(user)

    return array

def query(sock, nick):
    command = 'QUERY ' + nick
    sock.sendall(command.encode())
    data = sock.recv(4096).decode()

    if (data[0:2] != 'OK'):
        print('Error con la peticion')
        print(data)
        return

    user = data[len('OK USER_FOUND '):]

    [name, ip, port, version] = user.split(' ')

    user = {
    'name': name,
    'ip': ip,
    'port': port,
    'version': version
    }

    return user

sock = connect_to_server()
# data = list_users(sock)
# print(data)
data = query(sock, 'agk')
print(data)
