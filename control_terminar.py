class ControlTerminar:
    def __init__(self):
        self.flag_terminar = False

    def terminar(self):
        return self.flag_terminar

    def setTerminar(self, bool):
        self.flag_terminar = bool
