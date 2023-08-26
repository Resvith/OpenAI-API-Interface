import customtkinter


class ControllerFrame(customtkinter.CTkFrame):
    def __init__(self, master, controller):
        customtkinter.CTkFrame.__init__(self, master)
        self.grid()
        self.controller = controller
        self.controller.grid_rowconfigure(0, weight=1)
        self.controller.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError
