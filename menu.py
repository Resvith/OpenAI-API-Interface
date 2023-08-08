import customtkinter

from controller_frame import ControllerFrame


class Menu(ControllerFrame):
    def __init__(self, master, controller):
        ControllerFrame.__init__(self, master, controller)
        self.audio_models_button = None
        self.image_models_button = None
        self.text_models_button = None

    def create_widgets(self):
        self.text_models_button = customtkinter.CTkButton(self, text="Text Models", font=("New Times Rome", 24),
                                                          command=self.on_text_models_button_click)
        self.text_models_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.image_models_button = customtkinter.CTkButton(self, text="Image Models", font=("New Times Rome", 24),
                                                           command=self.on_image_models_button_click)
        self.image_models_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.audio_models_button = customtkinter.CTkButton(self, text="Audio Models", font=("New Times Rome", 24))
        self.audio_models_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

    def on_text_models_button_click(self):
        print("Text Models Button Clicked")
        self.controller.show_frame("TextModels")
        self.controller.change_geometry(1400, 800)
        self.controller.change_min_size(1100, 580)

    def on_image_models_button_click(self):
        print("Image Models Button Clicked")
        self.controller.show_frame("ImageModels")
        self.controller.change_geometry(1400, 800)
        self.controller.change_min_size(1100, 580)
