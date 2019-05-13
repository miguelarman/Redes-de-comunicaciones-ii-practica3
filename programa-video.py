from src.interfaz import Interfaz
from src.aplicacion import App

if __name__ == '__main__':
    gui = Interfaz("640x520", video='videos/video.mp4')
    App.gui = gui
    App.gui.start()
