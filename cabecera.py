import time

class Cabecera:
    counter = 0

    def resetCounter():
        Cabecera.counter = 0
        return

    # datos esta representado en bytes
    def poner(ancho, alto, fps, datos):
        # numero de orden de paquete
        ord = Cabecera.counter
        Cabecera.counter += 1

        # timestamp
        ts = int(time.time())

        header = "{}#{}#{}x{}#{}#".format(ord, ts, ancho, alto, fps).encode()

        return header + datos

    def quitar(msg):
        foo = msg.decode().split('#')
        return {
            'ord' : foo[0],
            'ts' : foo[1],
            'res' : foo[2],
            'fps' : foo[3],
            'datos' : foo[4].encode()
        }
