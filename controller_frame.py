import customtkinter


class ControllerFrame(customtkinter.CTkFrame):
    def __init__(self, master, controller):
        customtkinter.CTkFrame.__init__(self, master)
        self.grid()
        print("Controller Frame created:", self.winfo_width(), self.winfo_height())
        self.controller = controller
        self.controller.grid_rowconfigure(0, weight=1)
        self.controller.grid_columnconfigure(0, weight=1)
        self.controller.configure(sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError

