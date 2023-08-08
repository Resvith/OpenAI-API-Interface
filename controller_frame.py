import customtkinter


class ControllerFrame(customtkinter.CTkFrame):
    def __init__(self, master, controller):
        customtkinter.CTkFrame.__init__(self, master)
        self.master = self
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError

