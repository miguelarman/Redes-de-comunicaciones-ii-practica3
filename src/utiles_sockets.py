"""
    Prácticas de Redes de comunicaciones 2

    Autores:
        Miguel Arconada Manteca
        Mario García Pascual

    utiles_sockets:
        En este fichero se implementan dos funciones útiles en lo relativo
        a la gestión de sockets en el equipo:
            - Obtener tu dirección IP privada
            - Obtener un puerto libre
"""

import socket

"""
Función que crea un socket para calcular tu dirección IP

Returns:
    Tu dirección IP
"""
def getIPPrivada():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

"""
Función que calcula un puerto libre en el equipo

Returns:
    El número de un puerto libre de la máquina
"""
def getPuertoLibre():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
