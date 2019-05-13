import socket

from src.generales import *

class ConexionDS:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(DS_ADDR)

    def register(self, nick, ip, port, pwd, proto):
        cmd = 'REGISTER {} {} {} {} {}'.format(nick, ip, port, pwd, proto)
        self.sock.sendall(cmd.encode())
        data = self.sock.recv(BUFSIZE).decode()

        foo = data.split(' ')
        if foo[0] == 'OK':
            return {'nick':foo[2], 'ts':foo[3]}
        else:
            return None

    def query(self, nick):
        cmd = 'QUERY {}'.format(nick)
        self.sock.sendall(cmd.encode())
        data = self.sock.recv(BUFSIZE).decode()

        foo = data.split(' ')
        if foo[0] == 'OK':
            return {'nick':foo[2], 'ip':foo[3], 'port':foo[4], 'proto':foo[5]}
        else:
            return None

    def list_users(self):
        cmd = 'LIST_USERS'
        self.sock.sendall(cmd.encode())
        data = self.sock.recv(BUFSIZE).decode()

        foo = data.split(' ')
        if foo[0] != 'OK':
            return None


        num = foo[2]
        list = data[len('OK USERS_LIST ') + len(str(num)) + 1:]
        list = list.split('#')

        array = []
        for entry in list:
            # if len(entry) < 4:
            #     continue

            array.append(entry.split(' '))

        return array

    def quit(self):
        cmd = 'QUIT'
        self.sock.sendall(cmd.encode())
        data = self.sock.recv(BUFSIZE).decode()

        return data
