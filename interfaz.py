from appJar import gui, appjar
from PIL import Image, ImageTk
import numpy as np
import cv2
import time
import sys

import utiles_sockets
# from version2.conexion_ds import ConexionDS


class Interfaz():
    def __init__(self, window_size):
        # Creamos atributos
        # self.conexion_ds = ConexionDS()

        # Creamos una variable que contenga el GUI principal
        self.app = gui('Redes2 - P2P', window_size)
        self.app.setGuiPadding(10,10)

        # Preparación del interfaz
        self.app.setLocation(200, y=100)
        self.app.addLabel('label', 'Cliente Multimedia P2P - Redes2')
        self.app.addImage('video_enviado', "imgs/webcam.gif")

        # Añadir los botones
        self.app.addButtons(["Lista de usuarios", 'Llamar', "Colgar", "Salir", 'Mostrar'], self.buttonsCallback)

        # Barra de estado
        # Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
        self.app.addStatusbar(fields=2, side='RIGHT')
        self.app.setStatusbar("FPS: 0", 0)
        self.app.setStatusbar("Duración de la llamada: 00:00", 1)
        self.app.setStatusbarWidth(25, 1)

        # Anadimos funcion al cerrar
        self.app.setStopFunction(self.stopExecution)

        # # Creamos ventana de login
        # print('Pantalla de inicio de sesión')
        # try:
        #     self.app.startSubWindow('Login', modal=True)
        # except appjar.ItemLookupError:
        #     print('Ventana \'Login\' ya abierta')
        #     self.app.showSubWindow('Login')
        #     return
        #
        # self.app.setSize(300, 200)
        #
        # self.app.addLabel('usuario', 'Usuario:', 0, 0)
        # self.app.addLabel('pass', 'Contraseña:', 1, 0)
        # self.app.addLabel('ip', 'Dirección IP:', 2, 0)
        # self.app.addLabel('puerto', 'Puerto:', 3, 0)
        # self.app.addLabel('protocolo', 'Protocolo:', 4, 0)
        # self.app.addEntry('usuarioEnt', 0, 1)
        # self.app.addSecretEntry('passEnt', 1, 1)
        # self.app.addEntry('ipEnt', 2, 1)
        # self.app.addNumericEntry('puertoEnt', 3, 1)
        # self.app.addEntry('protEnt', 4, 1)
        #
        # # Prefijar valores de ip, puerto y protocolo
        # try:
        #     ip_privada = utiles_sockets.getIPPrivada()
        #     print('IP privada: {}'.format(ip_privada))
        #     puerto_disponible = utiles_sockets.getPuertoLibre()
        #     print('Puerto disponible: {}'.format(puerto_disponible))
        #     self.app.setEntry('ipEnt', ip_privada)
        #     self.app.setEntry('puertoEnt', puerto_disponible)
        #     self.app.setEntry('protEnt', 'V1')
        # except: # No se puede calcular la IP y el puerto
        #     self.app.setEntry('ipEnt', '127.0.0.1')
        #     self.app.setEntry('puertoEnt', 9999)
        #     self.app.setEntry('protEnt', 'V1')
        #
        # self.app.addButtons(["Aceptar", "Cancelar"], self.botones_login, colspan=2)
        # self.app.setFocus("usuarioEnt")
        # self.app.enableEnter(self.botones_login)
        # self.app.stopSubWindow()
        #
        # self.app.hide()
        # self.app.showSubWindow('Login')

        # Creamos ventana donde mostrar el vídeo recibido
        try:
            self.app.startSubWindow('Llamada')
        except appjar.ItemLookupError:
            print('Ventana \'Llamada\' ya abierta')
            self.app.showSubWindow('Llamada')
            return

        # Preparación del interfaz
        self.app.setLocation(900, y=100)
        self.app.addLabel('label_video', 'Video de <usuario>')
        self.app.addImage('video_recibido', "imgs/webcam.gif")

        self.app.stopSubWindow()
        # self.app.showSubWindow('Llamada')


    def start(self):
        self.app.go()

    def buttonsCallback(self, button):
        if button == "Salir":
            # Salimos de la aplicación
            self.app.stop()
        elif button == 'Mostrar':
            # Mostramos la ventana de vídeo
            self.app.openSubWindow('Llamada')
            self.app.setLabel('label_video', 'Video de <Cambiado>')
            self.app.showSubWindow('Llamada')

    def botones_login(self, boton):
        print('Se ha hecho click en {}'.format(boton))
        return

    def stopExecution(self):
        print('Saliendo')
        return True

if __name__ == '__main__':
    gui = Interfaz("640x520")

    # gui.login()

    gui.start()
