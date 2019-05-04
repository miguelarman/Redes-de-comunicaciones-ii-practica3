# import the library
from appJar import gui, appjar
from PIL import Image, ImageTk
import numpy as np
import cv2
import time
import sys
from descubrimiento import DS_connection
import generales
import utiles_sockets
import threading
from llamadas_entrantes import SocketEntrante
from control_terminar import ControlTerminar
from receptor_frames import ReceptorFrames
from conexion_de_control import ConexionDeControl
from puerto_UDP_saliente import PuertoUDPSaliente

class VideoClient(object):

	def __init__(self, window_size, video=0):

		# Inicializamos la lista de usuarios
		# self.lista = Lista_Usuarios()
		self.lista = None
		self.login_puerto = None
		self.login_ip = None
		self.logged = False
		self.enLlamada = False

		self.buffer_frames_recibidos = []

		# Adjudicamos un puerto libre para el puerto UDP entrante
		self.puerto_UDP_origen = utiles_sockets.getPuertoLibre()

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
		# self.cap = cv2.VideoCapture('videos/video.mp4')
		self.cap = cv2.VideoCapture(video)
		self.app.setPollTime(20)
		self.app.registerEvent(self.capturaVideo)

		# TODO: Registramos la funcion que muestra los frames recibido
		self.app.setPollTime(20)
		self.app.registerEvent(self.recibeFrame)

		# Añadir los botones
		self.app.addButtons(["Conectar", "Colgar", "Salir"], self.buttonsCallback)

		# Barra de estado
		# Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
		self.app.addStatusbar(fields=2, side='RIGHT')
		self.app.setStatusbar("FPS: 0", 0)
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
		if self.enLlamada == False:
			# TODO: De momento reutilizamos el frame
			self.app.setImageData("video", img_tk, fmt = 'PhotoImage')

		# TODO: Si estamos en llamada, añadimos el frame
		# al buffer de envío del socket UDP
		if self.enLlamada == True:
			# TODO: Codificamos el frame para enviarlo
			# Compresión JPG al 50% de resolución (se puede variar)
			encode_param = [cv2.IMWRITE_JPEG_QUALITY,50]
			result, encimg = cv2.imencode('.jpg', frame, encode_param)
			if result == False:
				print('Error al codificar imagen')
				encimg = encimg.tobytes()
				# Los datos "encimg" ya están listos para su envío por la red

			# Enviamos el frame al thread encargado de enviarlos
			self.puerto_UDP_saliente.nuevoFrame(encimg)

	def recibeFrame(self):
		if self.enLlamada == True:
			if len(self.buffer_frames_recibidos) > 0:
				encimg = self.buffer_frames_recibidos.pop(0)

				# Descompresión de los datos, una vez recibidos
				decimg = cv2.imdecode(np.frombuffer(encimg,np.uint8), 1)

				# Conversión de formato para su uso en el GUI
				cv2_im = cv2.cvtColor(decimg,cv2.COLOR_BGR2RGB)
				img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

				self.app.setImageData("video", img_tk, fmt = 'PhotoImage')
			# else:
				# print('No hay más frames para mostrar por pantalla')


	def nuevoFrameRecibido(self, recibido):
		# Guardamos el frame en el buffer para mostrarlo por pantalla (sin descodificarlo)
		self.buffer_frames_recibidos.append(recibido)

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

	def setReceptorFrames(self, receptor):
		self.receptor_frames = receptor

	def setPuertoUDPSaliente(self, emisor):
		self.puerto_UDP_saliente = emisor

	def notifyCall(self, socket, conn, mensaje): # Ver qué argumentos necesita
		verbo, nick, puerto = mensaje.split(' ')

		ret = self.app.okBox('Llamada entrante', 'Llamada entrante de: {}'.format(nick))

		if ret == True:
			# Establecer Llamada
			self.socketEntrante.setEnLlamada(True)

			# Crear conexión de control, y preparar los sockets UDP salientes y entrantes
			self.conexion_de_control = ConexionDeControl(self, conn=conn)
			print('Recibido en el handsake: {}'.format(mensaje))
			self.puerto_UDP_destino = int(puerto)
			self.nick_destino = nick
			self.ip_destino = self.discover_server.query(nick)['ip']
			self.conexion_de_control.enviarPuertoUDP()

			self.receptor_frames.configura_puerto()
			print('Configurado el receptor de frames')
			self.puerto_UDP_saliente.crea_puerto()
			print('Configurado el puerto UDP saliente')

			self.enLlamada = True

			return 'ACCEPTED'
		else:
			return 'DENIED'

	# Función que gestiona los callbacks de los botones
	def buttonsCallback(self, button):
		if button == "Salir":
			# Si está en llamada, antes de salirse termina la llamada
			if self.enLlamada == True:
				self.terminaLlamada()
				return

			print('Salir: en llamada {}'.format(self.enLlamada))

			# Salimos de la aplicación
			self.app.stop()
		elif button == "Conectar":
			# Entrada del nick del usuario a conectar
			# nick = self.app.textBox("Conexión", "Introduce el nick del usuario a buscar")
			# print('Se quiere conectar con el usuario {}'.format(nick))

			# Si está en llamada no se muestra
			if self.enLlamada == True:
				return

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
			self.terminaLlamada()

	def terminaLlamada(self):
		if self.enLlamada == True:
			# TODO: De momento salimos directamente de la aplicación
			self.conexion_de_control.terminaConexion()
			self.receptor_frames.terminaConexion()
			self.puerto_UDP_saliente.terminaConexion()

			# Vaciamos el buffer de entrada
			self.buffer_frames_recibidos = []

			# self.app.stop()
			print('Llamada terminada')

			self.enLlamada = False
			self.socketEntrante.setEnLlamada(False)
		else:
			print('No estás en llamada')

	def selecciona_lista_usuarios(self, index):
		nick, ip, puerto = self.lista[index][:-1]
		puerto = int(puerto)

		ret = self.app.okBox('Usuario seleccionado', 'Ha seleccionado al usuario {} con direccion {}:{}'.format(nick, ip, puerto))

		if ret == False:
			return
		else:
			print('Ha seleccionado el usuario {} con direccion {}:{}'.format(nick, ip, puerto))

			self.ip_destino = ip
			self.puerto_TCP_destino = puerto
			self.nick_destino = nick

			# Obtiene datos del servidor DS
			usuario = self.discover_server.query(nick)
			if usuario == 'ERROR':
				# TODO
				print('Usuario {} no disponible (Error en el DS)'.format(nick))
				return

			# Avisamos al thread que se encarga de las llamadas entrantes
			# de que vamos a entrar en llamada
			self.socketEntrante.setEnLlamada(True)


			# Crear conexión de control con el otro usuario
			self.conexion_de_control = ConexionDeControl(self)
			ret, descr = self.conexion_de_control.conecta()
			if ret == 'TIMEOUT':
				self.app.infoBox('Timeout', 'No se ha podido conectar con el usuario {} (timeout)'.format(nick))
				self.conexion_de_control.cerrar()
				self.conexion_de_control = None
				self.socketEntrante.setEnLlamada(False)
				# self.enLlamada = False
				# self.app.hideSubWindow('Usuarios')
				return 'ERROR'
			elif ret == 'ERROR':
				self.app.errorBox('Error cdc', 'Se ha detectado un error al abrir la conexión de control ({})'.format(descr))
				self.conexion_de_control.cerrar()
				self.conexion_de_control = None
				self.socketEntrante.setEnLlamada(False)
				# self.enLlamada = False
				# self.app.hideSubWindow('Usuarios')
				return 'ERROR'

			while True:
				ret = self.conexion_de_control.getPuertoUDP()
				if ret == 'DENIED':
					self.app.infoBox('Denied', 'El usuario {} ha denegado la llamada'.format(nick))
					self.conexion_de_control.cerrar()
					self.conexion_de_control = None
					self.socketEntrante.setEnLlamada(False)
					# self.enLlamada = False
					self.app.hideSubWindow('Usuarios')
					return 'ERROR'
				elif ret == 'BUSY':
					self.app.infoBox('Busy', 'El usuario {} está ocupado'.format(nick))
					self.conexion_de_control.cerrar()
					self.conexion_de_control = None
					self.socketEntrante.setEnLlamada(False)
					# self.enLlamada = False
					self.app.hideSubWindow('Usuarios')
					return 'ERROR'
				elif ret == 'ERROR':
					self.app.errorBox('Error cdc', 'Se ha detectado un error al llamar al usuario {}'.format(nick))
					self.conexion_de_control.cerrar()
					self.conexion_de_control = None
					self.socketEntrante.setEnLlamada(False)
					# self.enLlamada = False
					self.app.hideSubWindow('Usuarios')
					return 'ERROR'
				elif ret == 'TIMEOUT':
					aux = self.app.yesNoBox('Timeout', 'El usuario {} no ha respondido a la llamada. ¿Reintentar?'.format(nick))
					if aux == True:
						continue
					else:
						self.conexion_de_control.cerrar()
						self.conexion_de_control = None
						self.socketEntrante.setEnLlamada(False)
						self.enLlamada = False
						self.app.hideSubWindow('Usuarios')
						return 'ERROR'
				else:
					self.puerto_UDP_destino = int(ret)
					self.app.hideSubWindow('Usuarios')
					break

			print('Puerto UDP destino obtenido: {}'.format(self.puerto_UDP_destino))

			self.app.hideSubWindow('Usuarios')

			self.receptor_frames.configura_puerto()
			print('Configurado el receptor de frames')
			self.puerto_UDP_saliente.crea_puerto()
			print('Configurado el puerto UDP saliente')

			# TODO: implementar finalizacion de llamada

			# Indicamos que estamos en llamada cuando se establece
			# correctamente para poder salir de la aplicación correctamente
			self.enLlamada = True

# Funciones auxiliares

def funcion_entrantes(entrantes, gui, control_terminar):
	while entrantes.created == False:
		if control_terminar.terminar() == True:
			return
		# print('Reintentando configurar el SocketEntrante')
		entrantes.retry()
		time.sleep(generales.sleep_creacion)
	print('SocketEntrante creado correctamente')
	entrantes.go()

def funcion_receptor_frames(receptor, gui, control_terminar):
	while receptor.created == False:
		if control_terminar.terminar() == True:
			return
		# print('Reintentando configurar el ReceptorFrames')
		receptor.retry()
		time.sleep(generales.sleep_creacion)
	print('ReceptorFrames creado correctamente')
	receptor.go()

def funcion_UDP_saliente_frames(puerto_UDP_saliente, gui, control_terminar):
	while puerto_UDP_saliente.created == False:
		if control_terminar.terminar() == True:
			return
		# print('Reintentando configurar el PuertoUDPSaliente')
		puerto_UDP_saliente.retry()
		time.sleep(generales.sleep_creacion)
	print('PuertoUDPSaliente creado correctamente')
	puerto_UDP_saliente.go()


if __name__ == '__main__':

	# vc = VideoClient("640x520", video='videos/video.mp4')
	vc = VideoClient("640x520", video='videos/video2.mp4')
	vc.login()

	control_terminar = ControlTerminar()


	# Crear aquí los threads de lectura, de recepción y,
	# en general, todo el código de inicialización que sea necesario
	# ...
	entrantes = SocketEntrante(vc, control_terminar)
	thread_llamadas_entrantes = threading.Thread(target = funcion_entrantes, args=(entrantes,vc,control_terminar,))
	vc.setSocketEntrante(entrantes)

	receptor = ReceptorFrames(vc, control_terminar)
	thread_receptor_frames = threading.Thread(target = funcion_receptor_frames, args=(receptor,vc,control_terminar,))
	vc.setReceptorFrames(receptor)

	puerto_UDP_saliente = PuertoUDPSaliente(vc, control_terminar)
	thread_UDP_saliente_frames = threading.Thread(target = funcion_UDP_saliente_frames, args=(puerto_UDP_saliente,vc,control_terminar,))
	vc.setPuertoUDPSaliente(puerto_UDP_saliente)

	thread_llamadas_entrantes.start()
	thread_receptor_frames.start()
	thread_UDP_saliente_frames.start()

	# Lanza el bucle principal del GUI
	# El control ya NO vuelve de esta función, por lo que todas las
	# acciones deberán ser gestionadas desde callbacks y threads
	vc.start()

	print('Terminando hilos')
	control_terminar.setTerminar(True)
	thread_llamadas_entrantes.join()
	thread_receptor_frames.join()
	thread_UDP_saliente_frames.join()
	print('Hilos terminados')
