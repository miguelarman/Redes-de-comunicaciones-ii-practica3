import socket
import threading
import time

from src.generales import *
import src.aplicacion

class ModuloUDP:
    def __init__(self):
        # Bandera de control del modulo UDP
        self.shutdown = False

        # Abrimos nuestro socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(aplicacion.App.my_udp_addr)

        # Creamos los hilos
        self.send_thd = threading.Thread(target=self.__enviando)
        self.recv_thd = threading.Thread(target=self.__recibiendo)

    def start(self):
        self.shutdown = False
        self.recv_thd.start()
        self.send_thd.start()

    def stop(self):
        self.shutdown = True
        self.sock.close()
        self.recv_thd.join()
        self.send_thd.join()

    def  __enviando(self):
        while not self.shutdown:
            try:
                if not aplicacion.App.on_hold:
                    data = aplicacion.App.in_buf.get_nowait()
                    self.sock.sendto(data, aplicacion.App.her_udp_addr)
                else:
                    time.sleep(UDP_SLEEP)
            except queue.Empty:
                time.sleep(UDP_SLEEP)
            except socket.error:
                time.sleep(UDP_SLEEP)


    def __recibiendo(self):
        self.sock.settimeout(UDP_SLEEP)
        while not self.shutdown:
            try:
                if not aplicacion.App.on_hold:
                    data, addr = self.sock.(BUFSIZE)
                    aplicacion.App.out_buf.put_nowait(data)
                    print(data)
                else:
                    time.sleep(UDP_SLEEP)
            except queue.Full:
                time.sleep(UDP_SLEEP)
            except socket.timeout:
                time.sleep(UDP_SLEEP)
            except socket.error:
                time.sleep(UDP_SLEEP)
