import socket
import generales

class ConexionDeControl:
    def __init__(self, gui, terminar):
        if gui.logged == False:
            self.created = False
            self.gui = gui
            self.terminar = terminar
            self.ip = gui.login_ip
            self.puerto = gui.login_puerto
            return
        self.created = True

        return

    def retry(self):
        return self.__init__(self.gui, self.terminar)

    def establece_socket(self, conn=None):
        if conn == None:
            self.ip_destino = self.gui.ip_destino
            self.puerto_destino = self.gui.puerto_TCP_destino
            self.nick_destino = self.gui.nick_destino
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = conn

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

    def mandaPuertoUDP(self):
        recibido = conn.recv(generales.socket_bufsize).decode()
        print('Recibido en el handshake: {}'.format(recibido))

    def terminaConexion(self):
        return

    def enviarPuertoUDP(self):
        respuesta = 'CALL_ACCEPTED {} {}'.format(self.gui.usuario, self.gui.puerto_UDP_origen)
        self.socket.sendall(respuesta.encode())
        print('Respuesta: {}'.format(respuesta))


    def getPuertoUDP(self):
        nick = self.gui.usuario
        UDP_port = self.gui.puerto_UDP_origen

        mensaje = 'CALLING {} {}'.format(nick, UDP_port)
        self.socket.sendall(mensaje.encode())

        try:
            self.socket.settimeout(generales.timeout_handshake)
            recibido = self.socket.recv(generales.socket_bufsize).decode()
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
            print('Recibido: {}'.format(palabras))
            nick = palabras[1]
            puerto_UDP_destino = palabras[2]
            return puerto_UDP_destino
        else:
            return 'ERROR'

    def go(self):
        while True:
            if self.terminar.terminar() == True:
                return

            if self.gui.enLlamada == True:

                try:
                    self.socket.settimeout(generales.timeout)
                    recibido = self.socket.recv(generales.socket_bufsize)
                    self.socket.settimeout(0)

                    # Notificamos a la GUI de que tenemos un nuevo frame
                    self.gui.codigoControlRecibido(recibido)
                except socket.timeout:
                    print('Timeout en la conexión de control')
                    continue

            else:
                time.sleep(generales.sleep_bucle)
