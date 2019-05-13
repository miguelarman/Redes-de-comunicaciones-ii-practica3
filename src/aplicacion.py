import threading
import collections
import queue

from src.modulo_tcp import ModuloTCP
from src.conexion_ds import ConexionDS
from src.generales import *
from src.utiles_sockets import *
from src.cabecera import Cabecera

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
    out_buf = queue.PriorityQueue()

    def login(nick, ip, port, pwd, proto):
        # hacemos uso del servidor de descubrimiento
        ds = ConexionDS()
        foo = ds.register(nick, ip, port, pwd, proto)
        ds.quit()
        if not foo:
            print("login fallido")
        else:
            print("login exitoso")

            App.nick = nick
            App.ip = ip
            App.my_tcp_port = port
            App.my_udp_port = getPuertoLibre()
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
            ds.quit()
            if not foo:
                print("nick no encontrado")
            else:
                print("usuario encontrado")
                ret = App.__llamar((foo['ip'], int(foo['port'])))
                if not ret:
                    print("no se ha podido establecer llamada")
                else:
                    Cabecera.resetCounter()
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
                return App.out_buf.get_nowait()[1]
            except:
                return

    def lista_de_usuarios():
        if App.logged:
            ds = ConexionDS()
            foo = ds.list_users()
            ds.quit()
            return foo

    def __vaciar_cola(cola):
        while not cola.empty():
            try:
                cola.get_nowait()
            except cola.Empty:
                return

    def vaciar_bufs():
        App.__vaciar_cola(App.in_buf)
        App.__vaciar_cola(App.out_buf)

    def responder(nick):
        Cabecera.resetCounter()
        return App.gui.notifyCall(nick)

    def pausar():
        if App.on_call:
            App.control_conn.pausar()
            App.on_hold = True
            App.vaciar_bufs()
            return True

    def nos_pausan():
        if App.on_call and not App.on_hold:
            App.on_hold = True
            App.vaciar_bufs()
            return True


    def reanudar():
        if App.on_call and App.on_hold:
            App.vaciar_bufs()
            App.control_conn.reanudar()
            App.on_hold = False
            return True

    def nos_reanudan():
        if App.on_call and App.on_hold:
            App.vaciar_bufs()
            App.on_hold = False
            return True

    def colgar():
        if App.on_call:
            App.control_conn.colgar()
            App.control_conn.stop()
            App.on_hold = False
            App.on_call = False
            App.vaciar_bufs()
            return True

    def nos_cuelgan():
        if App.on_call:
            App.control_conn.stop()
            App.on_hold = False
            App.on_call = False
            App.vaciar_bufs()

    def stop():
        if App.logged:
            if App.on_call:
                App.colgar()
            App.tcp.stop()
            return
        else:
            return
