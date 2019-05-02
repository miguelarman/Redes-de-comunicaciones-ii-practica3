import socket
import generales
import time

class ReceptorFrames:
    def __init__(self, gui, terminar):
        if gui.logged == False:
            self.created = False
            self.gui = gui
            self.terminar = terminar
            return
        self.created = True


    def retry(self):
        return self.__init__(self.gui, self.terminar)

    def configura_puerto(self):
        self.ip = self.gui.login_ip
        self.puerto = self.gui.puerto_UDP_origen

        # Configura el puerto
        print('Creando el socket UDP...')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Puerto entrante configurado')
        self.socket.bind((self.ip, self.puerto))

    def terminaConexion(self):
        return

    def go(self):
        while 1:
            if self.terminar.terminar() == True:
                return

            try:
                self.socket.settimeout(generales.timeout)
                recibido, adress = self.socket.recvfrom(4096)
                recibido.decode()
                self.socket.settimeout(generales.timeout)

                # Notificamos a la GUI de que tenemos un nuevo frame
                self.gui.nuevoFrameRecibido(recibido)
            except socket.timeout:
                print('Timeout en el socket UDP receptor')
                continue

            # time.sleep(generales.sleep_bucle)
