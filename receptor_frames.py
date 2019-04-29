import socket
import generales
import time

class ReceptorFrames:
    def __init__(self, gui, terminar):
        if gui.logged == False:
            self.created = False
            self.gui = gui
            self.terminar = terminar
            return
        self.created = True


    def retry(self):
        return self.__init__(self.gui, self.terminar)

    def go(self):
        while 1:
            if self.terminar.terminar() == True:
                return

            time.sleep(generales.sleep_bucle)
