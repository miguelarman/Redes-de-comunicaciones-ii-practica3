import threading
import time
import socket

from src.generales import *
from src.modulo_udp import ModuloUDP
import src.aplicacion

class ConexionControl:
    def __init__(self, conn):
        # Socket de la conexion de control
        self.conn = conn

        # Bandera de control para apagar el modulo
        self.shutdown = False

        # Modulo UDP
        self.udp = ModuloUDP()

        # Hilo del modulo
        self.control_thd = threading.Thread(target=self.__controlando)

    def start(self):
        self.shutdown = False
        print('iniciando modulo udp')
        self.udp.start()
        self.control_thd.start()

    def stop(self):
        self.shutdown = True
        self.conn.shutdown(socket.SHUT_RDWR)
        self.conn.close()
        self.udp.stop()
        self.control_thd.join()

    def __controlando(self):
        self.conn.settimeout(CONTROL_TIMEOUT)
        while not self.shutdown:
            try:
                data = self.conn.recv(BUFSIZE)

                foo = data.decode().split(' ')
                if foo[0] == 'CALL_HOLD':
                    print("Código de pausa recibido")
                    src.aplicacion.App.nos_pausan()
                elif foo[0] == 'CALL_RESUME':
                    print("Código de reanudación recibido")
                    src.aplicacion.App.nos_reanudan()
                elif foo[0] == 'CALL_END':
                    print("Código de finalización recibido")
                    src.aplicacion.App.nos_cuelgan()
                else:
                    print("Código erróneo recibido, finalizamos")
                    src.aplicacion.App.nos_cuelgan()
            except socket.timeout:
                time.sleep(CONTROL_SLEEP)
            except socket.error:
                time.sleep(CONTROL_SLEEP)
        print('soy uno de los thds de conn y estoy saliendo')

    def pausar(self):
        cmd = 'CALL_HOLD {}'.format(src.aplicacion.App.nick)
        self.conn.sendall(cmd.encode())


    def reanudar(self):
        cmd = 'CALL_RESUME {}'.format(src.aplicacion.App.nick)
        self.conn.sendall(cmd.encode())

    def colgar(self):
        cmd = 'CALL_END {}'.format(src.aplicacion.App.nick)
        self.conn.sendall(cmd.encode())
