from appJar import gui, appjar
from PIL import Image, ImageTk
import numpy as np
import cv2
import time
import queue
import sys

import src.utiles_sockets as utiles
from src.aplicacion import App
from src.cabecera import Cabecera

class Interfaz():
    def __init__(self, window_size, video=0):
        self.llamada_entrante = None

        # Creamos una variable que contenga el GUI principal
        self.app = gui('Redes2 - P2P', window_size)
        self.app.setGuiPadding(10,10)

        # Preparación del interfaz
        self.app.setLocation(200, y=100)
        self.app.addLabel('label', 'Cliente Multimedia P2P - Redes2')
        self.app.addImage('video_enviado', "imgs/webcam.gif")

        # Registramos funcioones
        self.cap = cv2.VideoCapture(video)
        self.app.setPollTime(20)
        self.app.registerEvent(self.capturaFrame)
        self.app.registerEvent(self.muestraFrame)
        self.app.registerEvent(self.compruebaVentanas)

        # Añadir los botones
        self.app.addButtons(["Lista de usuarios", 'Llamar', 'Pausar', 'Reanudar',"Colgar", "Salir"], self.buttonsCallback)

        # Barra de estado
        # Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
        self.app.addStatusbar(fields=2, side='RIGHT')
        self.app.setStatusbar("FPS: 0", 0)
        self.app.setStatusbar("Duración de la llamada: 00:00", 1)
        self.app.setStatusbarWidth(25, 1)

        # Anadimos funcion al cerrar
        self.app.setStopFunction(self.stopExecution)

        # # Creamos ventana de login
        print('Pantalla de inicio de sesión')
        try:
            self.app.startSubWindow('Login', modal=True)
        except appjar.ItemLookupError:
            print('Ventana \'Login\' ya abierta')
            self.app.showSubWindow('Login')
            return

        self.app.setSize(300, 200)

        self.app.addLabel('usuario', 'Usuario:', 0, 0)
        self.app.addLabel('pass', 'Contraseña:', 1, 0)
        self.app.addLabel('ip', 'Dirección IP:', 2, 0)
        self.app.addLabel('puerto', 'Puerto:', 3, 0)
        self.app.addLabel('protocolo', 'Protocolo:', 4, 0)
        self.app.addEntry('usuarioEnt', 0, 1)
        self.app.addSecretEntry('passEnt', 1, 1)
        self.app.addEntry('ipEnt', 2, 1)
        self.app.addNumericEntry('puertoEnt', 3, 1)
        self.app.addEntry('protEnt', 4, 1)

        # Prefijar valores de ip, puerto y protocolo
        ip_privada = utiles.getIPPrivada()
        print('IP privada: {}'.format(ip_privada))
        puerto_disponible = utiles.getPuertoLibre()
        print('Puerto disponible: {}'.format(puerto_disponible))
        self.app.setEntry('ipEnt', ip_privada)
        self.app.setEntry('puertoEnt', puerto_disponible)
        self.app.setEntry('protEnt', 'V1')


        self.app.addButtons(["Aceptar", "Cancelar"], self.botones_login, colspan=2)
        self.app.setFocus("usuarioEnt")
        self.app.enableEnter(self.botones_login)
        self.app.stopSubWindow()

        self.app.hide()
        self.app.showSubWindow('Login')

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

    #################################################
    # Funciones que se encargan del vídeo
    #################################################
    def capturaFrame(self):
        if App.logged:
            # Capturamos un frame de la cámara o del vídeo
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (640,480))
            cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

            # Lo mostramos en el GUI
            self.app.setImageData("video_enviado", img_tk, fmt = 'PhotoImage')

            if App.on_call:
                # Codificamos el frame para enviarlo
                # Compresión JPG al 50% de resolución (se puede variar)
                encode_param = [cv2.IMWRITE_JPEG_QUALITY,50]
                result, encimg = cv2.imencode('.jpg', frame, encode_param)
                if result == False:
                    print('Error al codificar imagen')

                encimg = encimg.tobytes()

                width = self.cap.get(3)
                height = self.cap.get(4)
                fps = self.cap.get(cv2.CAP_PROP_FPS)

                datos = Cabecera.poner(width, height, fps, encimg)

                try:
                    App.enviar(datos)
                except queue.Full:
                    print('Cola de envío llena')

    def muestraFrame(self):
        if App.on_call:
            datos = App.recibir()

            if datos:
                dicc = Cabecera.quitar(datos)

                res = dicc['res']
                width, height = res.split('x')
                fps = dicc['fps']
                encimg = dicc['datos']


                # Descompresión de los datos, una vez recibidos
                decimg = cv2.imdecode(np.frombuffer(encimg,np.uint8), 1)

                # Conversión de formato para su uso en el GUI
                cv2_im = cv2.cvtColor(decimg,cv2.COLOR_BGR2RGB)
                img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

                self.app.setImageData("video_recibido", img_tk, fmt = 'PhotoImage')
                self.app.setImageSize('video_recibido', width, height)

                self.app.setStatusbar("FPS: {}".format(fps), 0)


    def compruebaVentanas(self):
        if App.on_call:
            self.app.showSubWindow('Llamada')
        else:
            self.app.hideSubWindow('Llamada')

        if self.llamada_entrante:
            ret = self.app.yesNoBox('Llamada entrante', 'Llamada entrante de: {}'.format(self.llamada_entrante))
            print('ret: {}'.format(ret))
            if ret == False:
                return False

            self.app.showSubWindow('Llamada')
            self.app.setLabel('label_video','Video de {}'.format(self.llamada_entrante))

            self.llamada_entrante = None

    #################################################
    # Callback de funciones
    #################################################
    def buttonsCallback(self, button):
        if button == "Salir":
            # Salimos de la aplicación
            App.stop()
            self.app.stop()
        elif button == 'Lista de usuarios':
            self.lista = App.lista_de_usuarios()

            try:
                self.app.startSubWindow('Usuarios', modal=True)
            except appjar.ItemLookupError:
                print('Ventana \'Usuarios\' ya abierta')
                self.app.showSubWindow('Usuarios')
                return

            self.app.setSize(550, 600)
            self.app.addLabel("lx", 'Usuarios disponibles para llamar')
            self.app.addTable('tabla_usuarios', [['Nombre', 'Dirección IP', 'Puerto']], action = self.selecciona_lista_usuarios)
            print('Añadiendo filas')
            self.app.addTableRows('tabla_usuarios', self.lista)
            print('Añadidas filas')
            self.app.setTableWidth('tabla_usuarios', 500)
            self.app.setTableHeight('tabla_usuarios', 550)
            self.app.stopSubWindow()
            self.app.showSubWindow('Usuarios')

        elif button == 'Llamar':
            nick = self.app.stringBox('pregunta_nick', 'Nick del usuario a llamar')
            if nick:
                print('Llamar a {}'.format(nick))

                foo = App.llamar(nick)
                if foo == None:
                    self.app.errorBox('sdfsdf', 'No se ha podido conectar con {}'.format(nick))
                else:
                    self.app.showSubWindow('Llamada')
                    self.app.setLabel('label_video','Video de {}'.format(nick))
        elif button == 'Pausar':
            App.pausar()
        elif button == 'Reanudar':
            App.reanudar()
        elif button == "Colgar":
            App.colgar()
            self.app.hideSubWindow('Llamada')
        else:
            print('Botón no definido ({})'.format(button))

    # Callback de los botones de login
    def botones_login(self, button):
        if button == 'Cancelar':
            # self.app.hideSubWindow('Login')
            self.app.stop()
        elif button == "Aceptar":
            # Leer los campos de inicio de sesión
            self.nick = self.app.getEntry("usuarioEnt")
            self.password = self.app.getEntry("passEnt")
            self.login_ip = self.app.getEntry("ipEnt")
            self.login_puerto = int(self.app.getEntry("puertoEnt"))
            self.protocolo = self.app.getEntry("protEnt")
            print('Usuario: {}. Contraseña: {}'.format(self.nick, self.password))
            print('Dirección IP: {}. Puerto: {}. Protocolo: {}'.format(self.login_ip, self.login_puerto, self.protocolo))

            foo = App.login(self.nick, self.login_ip, self.login_puerto, self.password, self.protocolo)

            if foo == True:
                print('Login correcto')
                self.app.hideSubWindow('Login')
                self.app.show()
            else:
                print('Login incorrecto')
                self.app.errorBox("Login incorrecto", "Datos inválidos. Prueba de nuevo")
                return

    # Callback de la tabla de usuarios
    def selecciona_lista_usuarios(self, index):
        if self.lista:
            nick, ip, puerto = self.lista[index][:-1]
            puerto = int(puerto)

            ret = self.app.okBox('Usuario seleccionado', 'Ha seleccionado al usuario {} con direccion {}:{}'.format(nick, ip, puerto))

            if ret == False:
                return

            foo = App.llamar(nick)

            if foo == True:
                self.app.hideSubWindow('Usuarios')



    #################################################
    # Notificaciones
    #################################################
    def notifyCall(self, nick):
        self.llamada_entrante = nick

        return True

    def meCuelgan(self):
        self.app.hideSubWindow('Llamada')


    def stopExecution(self):
        print('Saliendo')
        return True
