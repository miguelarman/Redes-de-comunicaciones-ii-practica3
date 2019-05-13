import socket
import threading
import time

from src.generales import *
from src.conexion_control import ConexionControl
import src.aplicacion


class ModuloTCP:
    def __init__(self):
        # Socket del modulo TCP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(aplicacion.App.my_tcp_addr)

        # Bandera de control para apagar el modulo
        self.shutdown = False

        # Hilo del modulo
        self.listen_thd = threading.Thread(target=self.__escuchando)

    def start(self):
        self.shutdown = False
        self.listen_thd.start()

    def stop(self):
        self.shutdown = True
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        #self.listen_thd.join()

    def __escuchando(self):
        self.sock.settimeout(LISTEN_TIMEOUT)
        while not self.shutdown:
            try:
                self.sock.listen(1)
                conn, her_addr = self.sock.accept()
                self.responder(conn, her_addr)
            except socket.timeout:
                time.sleep(LISTEN_SLEEP)
            except socket.error:
                raise

    def responder(self, conn, her_addr):
        aplicacion.App.on_call_lock.acquire()
        if aplicacion.App.on_call:
            aplicacion.App.on_call_lock.release()

            print("Llamada rechazada, ocupado")
            # Estamos ocupados
            cmd = 'CALL_BUSY'
            conn.sendall(cmd.encode())
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        else:
            aplicacion.App.on_call = True
            aplicacion.App.on_call_lock.release()

            data = conn.recv(BUFSIZE)
            foo = data.decode().split(' ')
            if foo[0] == 'CALLING':
                # Es una petición de llamada y la procesamos
                if aplicacion.App.responder(foo[1]):
                    print("Llamada aceptada")
                    # Llamada aceptada, abrimos conexion de control
                    cmd = 'CALL_ACCEPTED {} {}'.format(aplicacion.App.nick, aplicacion.App.my_udp_port)
                    conn.sendall(cmd.encode())

                    aplicacion.App.her_tcp_addr = her_addr
                    aplicacion.App.her_udp_addr = (her_addr[0], int(foo[2]))
                    aplicacion.App.control_conn = ConexionControl(conn)
                    aplicacion.App.control_conn.start()
                    return True
                else:
                    print("Llamada denegada")
                    # Llamada denegada
                    cmd = 'CALL_DENIED {}'.format(aplicacion.App.nick)
                    conn.sendall(cmd.encode())
                    aplicacion.App.on_call_lock.acquire()
                    aplicacion.App.on_call = False
                    aplicacion.App.on_call_lock.release()

                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
            else:
                print('No respeta el protocolo')
                # No respeta el protocolo, nos vamos
                aplicacion.App.on_call_lock.acquire()
                aplicacion.App.on_call = False
                aplicacion.App.on_call_lock.release()

                conn.shutdown(socket.SHUT_RDWR)
                conn.close()

    def llamar(self, her_addr):
        aplicacion.App.on_call_lock.acquire()
        if aplicacion.App.on_call:
            aplicacion.App.on_call_lock.release()
            print('No puedes llamar cuando estas en llamada')
        else:
            aplicacion.App.on_call = True
            aplicacion.App.on_call_lock.release()

            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(CONNECT_TIMEOUT)
            try:
                conn.connect(her_addr)
            except socket.timeout:
                print('Timeout al conectar')
                aplicacion.App.on_call_lock.acquire()
                aplicacion.App.on_call = False
                aplicacion.App.on_call_lock.release()
                return
            except socket.error:
                aplicacion.App.on_call_lock.acquire()
                aplicacion.App.on_call = False
                aplicacion.App.on_call_lock.release()
                raise

            cmd = 'CALLING {} {}'.format(aplicacion.App.nick, aplicacion.App.my_udp_port)
            conn.sendall(cmd.encode())

            conn.settimeout(REPLY_TIMEOUT)
            try:
                data = conn.recv(BUFSIZE)
            except socket.timeout:
                print('Timeout al esperar respuesta')
                aplicacion.App.on_call_lock.acquire()
                aplicacion.App.on_call = False
                aplicacion.App.on_call_lock.release()
                return
            except socket.error:
                raise

            foo = data.decode().split(' ')
            if foo[0] == 'CALL_ACCEPTED':
                # Llamada aceptada, creamos conexion de control
                print('Llamada aceptada')
                aplicacion.App.her_tcp_addr = her_addr
                aplicacion.App.her_udp_addr = (her_addr[0], int(foo[2]))
                aplicacion.App.control_conn = ConexionControl(conn)
                aplicacion.App.control_conn.start()
                return True
            elif foo[0] == 'CALL_DENIED':
                # Llamada denegada
                print('Llamada denegada')
                aplicacion.App.on_call_lock.acquire()
                aplicacion.App.on_call = False
                aplicacion.App.on_call_lock.release()

                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            elif foo[0] == 'CALL_BUSY':
                # Esta ocupado
                print("Receptor ocupado")
                aplicacion.App.on_call_lock.acquire()
                aplicacion.App.on_call = False
                aplicacion.App.on_call_lock.release()

                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            else:
                # No respeta el protocolo, adios
                print('No respeta el protocolo')
                aplicacion.App.on_call_lock.acquire()
                aplicacion.App.on_call = False
                aplicacion.App.on_call_lock.release()

                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
