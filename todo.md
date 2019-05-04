## GUI:
 - [x] Al iniciar la aplicacion ventana para iniciar sesion
 - [ ] Guardar la lista de usuarios con un timestamp como argumento de la clase para no actualizarlo siempre
 - [x] Al seleccionar un usuario de la tabla y llamar
 - [ ] Botón de colgar funcional
 - [ ] Statusbar que muestre duración de la llamada y FPS
 - [ ] Mostrar los dos vídeos simultáneamente por pantalla

## TCP
 - [x] Conexión al servidor DS
 - [x] Implementar conexión de control
  - [ ] Implementar códigos de control
  - [x] Thread que lea constantemente del socket de control
  - [ ] Control del buffer de frames recibidos
  - [ ] Comandos de pausa, calidad...

## UDP
 - [x] Implementar intercambio de vídeo
  - [ ] Codificar los frames con las cabeceras pedidas: calidad, FPS, etc
