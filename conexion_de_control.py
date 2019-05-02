import socket
import generales

class ConexionDeControl:
    def __init__(self, gui):
        self.gui = gui
        self.ip = gui.login_ip
        self.puerto = gui.login_puerto
        self.ip_destino = gui.ip_destino
        self.puerto_destino = gui.puerto_TCP_destino
        self.nick_destino = gui.nick_destino

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.bind((self.ip, self.puerto))

    def conecta(self):
        try:
            self.socket.settimeout(generales.timeout_connect)
            self.socket.connect((self.ip_destino, self.puerto_destino))
            self.socket.settimeout(None)
        except socket.timeout:
            return 'TIMEOUT', None
        except ConnectionRefusedError:
            return 'ERROR', 'Conection refused'
        except:
            return 'ERROR', 'Unexpected error'

        return 'OK', None

    def cerrar(self):
        self.socket.close()

    def terminaConexion(self):
        return

    def getPuertoUDP(self):
        nick = self.gui.usuario
        UDP_port = self.gui.puerto_UDP_origen

        mensaje = 'CALLING {} {}'.format(nick, UDP_port)
        self.socket.sendall(mensaje.encode())
        try:
            self.socket.settimeout(generales.timeout_handshake)
            recibido = self.socket.recv(4096).decode()
            self.socket.settimeout(None)
        except socket.timeout:
            print('Timeout en el handsake')
            return 'TIMEOUT'
        palabras = recibido.split(' ')

        comando = palabras[0]
        if comando == 'CALL_DENIED':
            return 'DENIED'
        elif comando == 'CALL_BUSY':
            return 'BUSY'
        elif comando == 'CALL_ACCEPTED':
            nick = palabras[1]
            puerto_UDP_destino = palabras[2]
            return puerto_UDP_destino
        else:
            return 'ERROR'
