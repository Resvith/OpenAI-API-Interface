import customtkinter
import tkinter as tk

import TextModels

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


class ControllerFrame(customtkinter.CTkFrame):
    def __init__(self, master, controller):
        customtkinter.CTkFrame.__init__(self, master)
        self.controller = controller
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        raise NotImplementedError


class Menu(ControllerFrame):
    # def __init__(self, master, controller):
    #     super().__init__(master, controller)
    #     self.audio_models_button = None
    #     self.image_models_button = None
    #     self.text_models_button = None

    def create_widgets(self):
        self.text_models_button = customtkinter.CTkButton(self, text="Text Models", font=("New Times Rome", 24))
        self.text_models_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.image_models_button = customtkinter.CTkButton(self, text="Image Models", font=("New Times Rome", 24))
        self.image_models_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.audio_models_button = customtkinter.CTkButton(self, text="Audio Models", font=("New Times Rome", 24))
        self.audio_models_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        

class App(customtkinter.CTk):
    def __init__(self):
        customtkinter.CTk.__init__(self)
        self.title("OpenAI API Interface")
        self.geometry("400x400")
        self.create_widgets()
        self.resizable(0, 0)

    def create_widgets(self):
        #   Frame Container
        self.container = customtkinter.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky=tk.W + tk.E)

        #   Frames
        self.frames = {}
        for f in (Menu, TextModels.TextModels):  # defined subclasses of BaseFrame
            print(f)
            frame = f(self.container, self)
            frame.grid(row=2, column=2, sticky=tk.NW + tk.SE)
            self.frames[f] = frame
        self.show_frame(Menu)

    def show_frame(self, cls):
        self.frames[cls].tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
    exit()
