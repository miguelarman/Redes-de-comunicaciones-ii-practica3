import socket
import generales
import time

class SocketEntrante(object):
    def __init__(self, gui, terminar):
        if gui.logged == False:
            self.created = False
            self.gui = gui
            self.terminar = terminar
            return

        self.created = True

        self.ip = gui.login_ip
        self.port = gui.login_puerto
        print('{}:{}'.format(self.ip, self.port))

        self.en_llamada = False

        # Create a TCP/IP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Hace bind y escucha
        self.socket.bind((self.ip, self.port))
        print('listening on {}:{}'.format(self.ip, self.port))

    def retry(self):
        return self.__init__(self.gui, self.terminar)

    def setEnLlamada(self, bool):
        self.en_llamada = bool

    def go(self):
        while 1:
            if self.terminar.terminar() == True:
                self.socket.close()
                return

            self.socket.settimeout(generales.timeout)
            try:
                self.socket.listen(1)

                conn, addr = self.socket.accept()
                print('Connected by', addr)

                recibido = self.socket.recv(4096)

                if self.en_llamada == True:
                    respuesta = 'BUSY'
                    conn.sendall(respuesta)
                    conn.close()
                    continue
                else:
                    ret = self.gui.notifyCall(self.socket, conn, recibido) # Ver qué argumento necesita
                    if ret == 'ACCEPTED':
                        # Sobreescribe el socket sin cerrarlo
                        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.socket.bind((self.ip, self.port))
                        print('listening on {}:{}'.format(self.ip, self.port))
                    else:
                        respuesta = 'DENY'
                        conn.sendall(respuesta)
                        conn.close()

                time.sleep(generales.sleep_bucle)
            except:
                print('Timeout en el socket de llamadas entrantes')
                continue
