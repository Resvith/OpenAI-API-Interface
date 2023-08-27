import customtkinter

from controller_frame import ControllerFrame


class Menu(ControllerFrame):
    def __init__(self, master, controller):
        ControllerFrame.__init__(self, master, controller)
        self.audio_models_button = None
        self.image_create_button = None
        self.text_models_button = None

    def create_widgets(self):
        self.menu_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.menu_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.menu_container.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.menu_container.grid_columnconfigure(0, weight=1)

        self.text_models_button = customtkinter.CTkButton(self.menu_container, text="Text Models", font=("New Times Rome", 24),
                                                          command=self.on_text_models_button_click)
        self.text_models_button.grid(row=0, column=0, padx=50, pady=10, sticky="nsew")

        self.image_models_frame = customtkinter.CTkFrame(self.menu_container, fg_color="transparent")
        self.image_models_frame.grid_columnconfigure((0, 1), weight=1)
        self.image_models_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.image_models_label = customtkinter.CTkLabel(self.image_models_frame, text="Image Models:", font=("New Times Rome", 24), justify="center", anchor="center")
        self.image_models_label.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(25, 0))
        self.image_create_button = customtkinter.CTkButton(self.image_models_frame, text="Create", font=("New Times Rome", 20),
                                                           command=self.on_image_models_button_click)
        self.image_create_button.grid(row=1, column=0, padx=10, pady=10, ipady=10)
        self.image_edit_button = customtkinter.CTkButton(self.image_models_frame, text="Edit", font=("New Times Rome", 20))
        self.image_edit_button.grid(row=1, column=1, padx=10, pady=10, ipady=10)

        self.audio_models_button = customtkinter.CTkButton(self.menu_container, text="Audio Models", font=("New Times Rome", 24))
        self.audio_models_button.grid(row=2, column=0, sticky="nsew", padx=50, pady=10)

    def on_text_models_button_click(self):
        self.controller.is_resizable(True)
        self.controller.show_frame("TextModels")
        self.controller.change_geometry(1400, 800)
        self.controller.change_min_size(1100, 580)

    def on_image_models_button_click(self):
        self.controller.is_resizable(True)
        self.controller.show_frame("ImageModels")
        self.controller.change_geometry(1400, 800)
        self.controller.change_min_size(1100, 580)
