import time

class Cabecera:
    counter = 0

    def resetCounter():
        Cabecera.counter = 0
        return

    def poner(ancho, alto, fps, datos):
        # numero de orden de paquete
        ord = Cabecera.counter
        Cabecera.counter += 1

        # timestamp
        ts = int(time.time())

        return "{}#{}#{}x{}#{}#{}".format(ord, ts, ancho, alto, fps, datos)

    def quitar(msg):
        foo = msg.split('#')
        return {
            'ord' : foo[0],
            'ts' : foo[1],
            'res' : foo[2],
            'fps' : foo[3],
            'datos' : foo[4]
        }
