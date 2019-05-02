import time
import generales
import socket

class PuertoUDPSaliente:
    def __init__(self, gui, terminar):
        if gui.logged == False:
            self.created = False
            self.gui = gui
            self.terminar = terminar
            self.buffer_envio = []
            return
        self.created = True

    def retry(self):
        return self.__init__(self.gui, self.terminar)

    def crea_puerto(self):
        self.ip_destino = self.gui.ip_destino
        self.puerto_UDP_destino = self.gui.puerto_UDP_destino

        print('Creando el socket UDP...')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def terminaConexion(self):
        # Vaciamos el buffer de envío
        self.buffer_envio = []

    def nuevoFrame(self, frame):
        # Añadimos el frame al buffer de envío
        self.buffer_envio.append(frame)

    def go(self):
        while 1:
            if self.terminar.terminar() == True:
                return

            # TODO: Si tiene frames pendientes por mandar, los envía
            if len(self.buffer_envio) > 0:
                # Envía el frame correspondiente
                # data = -------
                # self.socket.sendto(data.encode(), (self.ip_destino, self.puerto_UDP_destino))
                continue

            time.sleep(generales.sleep_bucle)
