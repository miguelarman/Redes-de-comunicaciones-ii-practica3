from src.interfaz import Interfaz

if __name__ == '__main__':
    gui = Interfaz("640x520")
    App.gui = gui
    App.gui.start()
