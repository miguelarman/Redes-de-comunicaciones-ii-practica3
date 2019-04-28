import socket

class DS_connection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None

    def connect_to_server(self):
        # Create a TCP/IP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is
        server_address = (self.ip, self.port)
        self.socket.connect(server_address)


    def register(self, nick, ip, port, password, protocol):
        command = 'REGISTER ' + nick + ' ' + ip + ' ' + str(port) + ' ' + password + ' ' + protocol
        self.socket.sendall(command.encode())
        data = self.socket.recv(4096).decode()

        if (data[0:2] != 'OK'):
            return data

        return 'OK'

    def list_users(self):
        command = 'LIST_USERS'
        self.socket.sendall(command.encode())
        data = self.socket.recv(4096).decode()

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
            if len(entry) == 0:
                continue

            # [name, ip, port, time] = entry.split(' ')

            # user = {
            # 'name': name,
            # 'ip': ip,
            # 'port': port,
            # 'time': time
            # }
            # array.append(user)
            array.append(entry.split(' '))

        return array

    def query(self, nick):
        command = 'QUERY ' + nick
        self.socket.sendall(command.encode())
        data = self.socket.recv(4096).decode()

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

    def quit(self):
        try:
            command = 'QUIT'
            self.socket.sendall(command.encode())
            data = self.socket.recv(4096).decode()
            self.socket.close()

            return data
        except:
            print('Error en quit')
