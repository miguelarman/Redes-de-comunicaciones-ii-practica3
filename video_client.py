# import the library
from appJar import gui, appjar
from PIL import Image, ImageTk
import numpy as np
import cv2
from descubrimiento import DS_connection
import generales
import utiles_sockets
import threading
from llamadas_entrantes import SocketEntrante
from control_terminar import ControlTerminar
# from lista_usuarios import Lista_Usuarios

class VideoClient(object):

	def __init__(self, window_size):

		# Inicializamos la lista de usuarios
		# self.lista = Lista_Usuarios()
		self.lista = None
		self.login_puerto = None
		self.login_ip = None
		self.logged = False

		# Creamos una variable que contenga el GUI principal
		self.app = gui("Redes2 - P2P", window_size)
		self.app.setGuiPadding(10,10)

		# Preparación del interfaz
		self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
		self.app.addImage("video", "imgs/webcam.gif")

		# Añadimos icono de la aplicación

		# Registramos la función de captura de video
		# Esta misma función también sirve para enviar un vídeo
		# self.cap = cv2.VideoCapture(0)
		self.cap = cv2.VideoCapture('videos/video.mp4')
		self.app.setPollTime(20)
		self.app.registerEvent(self.capturaVideo)

		# Añadir los botones
		self.app.addButtons(["Conectar", "Colgar", "Salir"], self.buttonsCallback)

		# Barra de estado
		# Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
		self.app.addStatusbar(fields=2, side='RIGHT')
		self.app.setStatusbar("FPS: XX", 0)
		self.app.setStatusbar("Duración de la llamada: 00:00", 1)
		self.app.setStatusbarWidth(25, 1)

		# Anadimos funcion al cerrar
		self.app.setStopFunction(self.stopExecution)

		# Creamos conexión al servidor de descubrimiento
		self.discover_server = DS_connection(generales.server_url, generales.server_port)
		self.discover_server.connect_to_server()
		print('Conectado al servidor de descubrimiento')

	def start(self):
		self.app.go()

	def login(self):
		# Iniciar sesión
		print('Pantalla de inicio de sesión')
		try:
			self.app.startSubWindow('Login', modal=True)
		except appjar.ItemLookupError:
			print('Ventana \'Login\' ya abierta')
			self.app.showSubWindow('Login')
			return

		self.app.setSize(295, 207)

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
		ip_privada = utiles_sockets.getIPPrivada()
		print('IP privada: {}'.format(ip_privada))
		puerto_disponible = utiles_sockets.getPuertoLibre()
		print('Puerto disponible: {}'.format(puerto_disponible))
		self.app.setEntry('ipEnt', ip_privada)
		self.app.setEntry('puertoEnt', puerto_disponible)
		self.app.setEntry('protEnt', 'V0')

		self.app.addButtons(["Aceptar", "Cancelar"], self.botones_login, colspan=2)
		self.app.setFocus("usuarioEnt")
		self.app.enableEnter(self.botones_login)
		self.app.stopSubWindow()

		self.app.hide()
		self.app.showSubWindow('Login')


	def botones_login(self, button):
		if button == 'Cancelar':
				self.app.hideSubWindow('Login')
				self.app.stop()
		elif button == "Aceptar":
			# Leer los campos de inicio de sesión
			self.usuario = self.app.getEntry("usuarioEnt")
			self.password = self.app.getEntry("passEnt")
			self.login_ip = self.app.getEntry("ipEnt")
			self.login_puerto = int(self.app.getEntry("puertoEnt"))
			self.protocolo = self.app.getEntry("protEnt")
			print('Usuario: {}. Contraseña: {}'.format(self.usuario, self.password))
			print('Dirección IP: {}. Puerto: {}. Protocolo: {}'.format(self.login_ip, self.login_puerto, self.protocolo))

			ret = self.discover_server.register(self.usuario, self.login_ip, self.login_puerto, self.password, self.protocolo)
			if ret == 'OK':
				print('Login correcto')
				self.app.hideSubWindow('Login')
				self.app.show()
				self.logged = True
			else:
				print('Login incorrecto')
				self.app.errorBox("Login incorrecto", "Datos inválidos. Prueba de nuevo")
				return

	def stopExecution(self):
		print('Cerrando conexión con el servidor DS')
		self.discover_server.quit()
		print('Cerrando programa')
		return True

	# Función que captura el frame a mostrar en cada momento
	def capturaVideo(self):

		# Capturamos un frame de la cámara o del vídeo
		ret, frame = self.cap.read()
		frame = cv2.resize(frame, (640,480))
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

		# Lo mostramos en el GUI
		self.app.setImageData("video", img_tk, fmt = 'PhotoImage')

		# Aquí tendría que el código que envia el frame a la red
		# ...

	# Establece la resolución de la imagen capturada
	def setImageResolution(self, resolution):
		# Se establece la resolución de captura de la webcam
		# Puede añadirse algún valor superior si la cámara lo permite
		# pero no modificar estos
		if resolution == "LOW":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
		elif resolution == "MEDIUM":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
		elif resolution == "HIGH":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

	def setSocketEntrante(self, entrantes):
		self.socketEntrante = entrantes

	def notifyCall(self, socket, conn, mensaje):
		verbo, nick, puerto = mensaje.split(' ')

		ret = self.app.okBox('pregunta', 'Llamada entrante de: {}'.format(nick))

		if ret == True:
			# Establecer Llamada
			return 'ACCEPTED'
		else:
			return 'DENIED'

	# Función que gestiona los callbacks de los botones
	def buttonsCallback(self, button):
		if button == "Salir":
			# Salimos de la aplicación
			self.app.stop()
		elif button == "Conectar":
			# Entrada del nick del usuario a conectar
			# nick = self.app.textBox("Conexión", "Introduce el nick del usuario a buscar")
			# print('Se quiere conectar con el usuario {}'.format(nick))

			# Lista todos los usuarios en el sistema
			if self.lista == None:
				self.lista = self.discover_server.list_users()


			# Creamos nueva ventana con todos los usuarios disponibles
			# (o la mostramos si ya está creada)
			# TODO si se cierra con la X directamente
			# TODO ver si está en llamada
			try:
				self.app.startSubWindow('Usuarios', modal=True)
			except appjar.ItemLookupError:
				print('Ventana \'Usuarios\' ya abierta')
				self.app.showSubWindow('Usuarios')
				return

			self.app.setSize(550, 600)
			self.app.addLabel("l2", 'Usuarios disponibles para llamar')
			self.app.addTable('tabla', [['Nombre', 'Dirección IP', 'Puerto']], action = self.selecciona_lista_usuarios)
			self.app.addTableRows('tabla', self.lista)
			self.app.setTableWidth('tabla', 500)
			self.app.setTableHeight('tabla', 550)
			self.app.stopSubWindow()
			self.app.showSubWindow('Usuarios')

		elif button == 'Colgar':
			# De momento salimos directamente de la aplicación
			self.app.stop()

	def selecciona_lista_usuarios(self, index):
		nick, ip, puerto = self.lista[index][:-1]

		ret = self.app.okBox('Usuario seleccionado', 'Ha seleccionado al usuario {} con direccion {}:{}'.format(nick, ip, puerto))

		if ret == False:
			return
		else:
			self.app.hideSubWindow('Usuarios')
			# self.app.destroySubWindow('Usuarios')
			print('Ha seleccionado el usuario {} con direccion {}:{}'.format(nick, ip, puerto))

			# Obtiene datos del servidor DS
			usuario = self.discover_server.query(nick)
			if usuario == 'ERROR':
				# TODO
				print('Usuario {} no disponible'.format(nick))
				return

			# Establecer llamada

			# Decimos al thread encargado del socket de entrada que estamos ocupados
			# self.socket_entrante.setEnLlamada(true)


def funcion_entrantes(entrantes, gui, control_terminar):
	while entrantes.created == False:
		if control_terminar.terminar() == True:
			return
		entrantes.retry()
	entrantes.go()


if __name__ == '__main__':

	vc = VideoClient("640x520")
	vc.login()

	control_terminar = ControlTerminar()


	# Crear aquí los threads de lectura, de recepción y,
	# en general, todo el código de inicialización que sea necesario
	# ...
	entrantes = SocketEntrante(vc, control_terminar)
	hilo_llamadas_entrantes = threading.Thread(target = funcion_entrantes, args=(entrantes,vc,control_terminar,))
	hilo_llamadas_entrantes.start()


	vc.setSocketEntrante(entrantes)

	# Lanza el bucle principal del GUI
	# El control ya NO vuelve de esta función, por lo que todas las
	# acciones deberán ser gestionadas desde callbacks y threads
	vc.start()

	print('Terminando hilos')
	control_terminar.setTerminar(True)
	hilo_llamadas_entrantes.join()
	print('Hilos terminados')
