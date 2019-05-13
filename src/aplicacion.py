import threading
import collections
import queue
import random

from src.modulo_tcp import ModuloTCP
from src.conexion_ds import ConexionDS
from src.generales import *

class App:
    nick = None
    ip = None
    my_tcp_port = None
    my_udp_port = None
    protocol = None

    my_tcp_addr = None
    my_udp_addr = None

    logged = False
    on_call = False
    on_hold = False

    on_call_lock = threading.Lock()

    gui = None
    tcp = None
    control_conn = None

    in_buf = queue.Queue()
    out_buf = queue.Queue()

    def login(nick, ip, port, pwd, proto):
        # hacemos uso del servidor de descubrimiento
        ds = ConexionDS()
        foo = ds.register(nick, ip, port, pwd, proto)
        if not foo:
            print("login fallido")
        else:
            print("login exitoso")

            App.nick = nick
            App.ip = ip
            App.my_tcp_port = port
            App.my_udp_port = random.randint(1000, 60000)
            App.protocol = proto

            App.my_tcp_addr = (App.ip, int(App.my_tcp_port))
            App.my_udp_addr = (App.ip, int(App.my_udp_port))

            App.tcp = ModuloTCP()
            App.tcp.start()

            App.logged = True

            return True

    def __llamar(her_tcp_addr):
        return App.tcp.llamar(her_tcp_addr)

    def llamar(nick):
        if App.logged:
            ds = ConexionDS()
            foo = ds.query(nick)
            if not foo:
                print("nick no encontrado")
            else:
                print("usuario encontrado")
                ret = App.__llamar((foo['ip'], int(foo['port'])))
                if not ret:
                    print("no se ha podido establecer llamada")
                else:
                    print("en llamada")
                    return True

    def enviar(msg):
        if App.on_call and not App.on_hold:
            try:
                App.in_buf.put_nowait(msg)
            except queue.Full:
                return

    def recibir():
        if App.on_call and not App.on_hold:
            try:
                return App.out_buf.get_nowait()
            except:
                return

    def responder(nick):
        return App.gui.notifyCall(nick)

    def pausar():
        if App.on_call:
            App.control_conn.pausar()
            App.on_hold = True
            return True

    def nos_pausan():
        if App.on_call:
            App.on_hold = True
            return True


    def reanudar():
        if App.on_call:
            App.control_conn.reanudar()
            App.on_hold = False
            return True

    def nos_reanudan():
        if App.on_call:
            App.on_hold = False
            return True

    def colgar():
        if App.on_call:
            App.control_conn.colgar()
            App.control_conn.stop()
            App.on_hold = False
            App.on_call = False
            return True

    def nos_cuelgan():
        if App.on_call:
            App.control_conn.stop()
            App.on_hold = False
            App.on_call = False

    def stop():
        if App.logged:
            if App.on_call:
                App.colgar()
            App.tcp.stop()
            return
        else:
            return
