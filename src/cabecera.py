import time
from parse import parse

class Cabecera:
    """
        Esta clase permite poner y quitar
        las cabeceras para el control de
        las comunicaciones
    """
    counter = 0

    def resetCounter():
        """ Resetea el contador de paquetes

        Returns
        -------
        type
            None

        """
        Cabecera.counter = 0
        return


    def poner(ancho, alto, fps, datos):
        """
            Pone la cabecera con la informacion necesaria a los
            datos pasados, que estan representados en bytes

        Parameters
        ----------
        ancho : int
            El ancho de la resolucion
        alto : int
            El alto de la resolucion
        fps : int
            Los fps que se estan retransmitiendo
        datos : bytes
            Los datos en bytes

        Returns
        -------
        bytes
            Los bytes correspondientes a la cabecera concatenado a los datos

        """
        # numero de orden de paquete
        ord = Cabecera.counter
        Cabecera.counter += 1

        # timestamp
        ts = int(time.time())

        header = "{}#{}#{}x{}#{}#".format(ord, ts, ancho, alto, fps).encode()

        return header + datos

    def quitar(msg):
        """
            Quita la cabecera al paquete y devuelve la informacion
            parseada junto con los datos

        Parameters
        ----------
        msg : bytes
            El paquete al que se le quiere quitar la cabecera

        Returns
        -------
        dict
            Diccionario con la informacion de la cabecera y los datos

        """
        foo = parse('{}#{}#{}#{}#{}', msg.decode())
        return {
            'ord' : foo[0],
            'ts' : foo[1],
            'res' : foo[2],
            'fps' : foo[3],
            'datos' : foo[4].encode()
        }
