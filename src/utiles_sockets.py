import socket

def getIPPrivada():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def getPuertoLibre():
    # for port in range(1025, 65536):
    #     sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     result = sock.connect_ex(('127.0.0.1', port))
    #     sock.close()
    #     print(result)
    #     if result == 0:
    #         return port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port
