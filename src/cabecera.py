import time
# from parse import parse

class Cabecera:

    ord_len = 5
    frames_len = 3
    ts_len = 10
    size_len = 7


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

        header = "{}#{}#{}x{}#{}#".format(int(ord), int(ts), int(ancho), int(alto), int(fps)).encode()
        # header = "{:05d}#{:010d}#{:03d}x{:03d}#{:03d}#".format(int(ord), int(ts), int(ancho), int(alto), int(fps)).encode()

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

        # x = Cabecera.ord_len + 1 + Cabecera.frames_len + 1 + Cabecera.ts_len + 1 + Cabecera.size_len + 1
        # cabecera = msg[:x].decode()
        # framecod = msg[x:]
        #
        # orden, ts, size, fps, _ = cabecera.split('#')
        campos = msg.split(b'#')
        orden, ts, size, fps = campos[:4]
        framecod = b'#'.join(campos[4:])

        return {
        'orden' : orden.decode(),
        'fps' : fps.decode(),
        'res' : size.decode(),
        'datos' : framecod
        }
