import threading
import socket
import time
import collections

from generales import *

class ModuloUDP:
    def __init__(self, my_addr, her_addr, in_buf, out_buf):
        # my_addr y his_addr son ambas pares (ip, port)
        self.my_addr = my_addr
        self.her_addr = her_addr
        self.in_buf = in_buf
        self.out_buf = out_buf

        # abrimos nuestro socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(my_addr)

        # creamos los hilos
        self.send_thread = threading.Thread(target=self. __enviando)
        self.recv_thread = threading.Thread(target=self.__recibiendo)

    def start(self):
        self.stop_threads = False
        self.recv_thread.start()
        self.send_thread.start()

    def  __enviando(self):
        while not self.stop_threads:
            try:
                data = in_buf.popleft()
                self.sock.sendto(data, her_addr)
            except IndexError:
                print('error buf')
                time.sleep(IN_BUF_SLEEP)
            except socket.error:
                raise


    def __recibiendo(self):
        while not self.stop_threads:
            try:
                data, addr = self.sock.recvfrom(BUFSIZE)
                out_buf.append(data)
            except socket.error:
                raise

    def shutdown(self):
        self.stop_threads = True
        self.send_thread.join()
        self.recv_thread.join()
