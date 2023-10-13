import json
import sys
import os

import customtkinter

from audio_models import AudioModels
from image_models_create import ImageModelsCreate
from image_models_edit import ImageModelsEdit
from menu import Menu
from text_models import TextModels

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        customtkinter.CTk.__init__(self)
        self.frames = None
        self.container = None
        self.title("OpenAI API Interface")
        self.create_widgets()

    def create_widgets(self):
        #   Frame Container
        self.container = customtkinter.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        #   Frames
        self.frames = {}
        for F in (Menu, TextModels, ImageModelsCreate, ImageModelsEdit, AudioModels):
            class_name = F.__name__
            frame = F(self.container, self)
            self.frames[class_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show start window
        # self.show_frame("Menu")
        # self.change_geometry(400, 400)
        # self.is_resizable(False)

        self.show_frame("TextModels")
        self.change_geometry(1400, 800)
        self.change_min_size(1100, 600)

        # When pressed enter, execute enter_clicked in actual frame:
        self.bind("<Return>", lambda event: self.enter_clicked(event, self.actual_frame.__class__.__name__))

    def show_frame(self, class_name):
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[class_name]
        frame.grid()
        frame.grid(row=0, column=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self.actual_frame = frame

    def enter_clicked(self, event, class_name):
        available_in = ["TextModels", "ImageModelsCreate", "ImageModelsEdit"]  # List of frames where event is available
        # If not pressed shift (also with CapsLock) and name in ^
        if not (event.state & (1 << 0) or event.state & (3 << 0)) and class_name in available_in:
            frame = self.frames[class_name]
            frame.on_send_button_click()

    @staticmethod
    def create_default_config():
        default_config_data = {
            "text_models": {
                "chats_counter": 0,
                "user_preferences": {
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 2500,
                    "temperature": 1.0,
                    "theme": "dark",
                    "window_width": 1400,
                    "window_height": 800,
                    "full-screened": False,
                    "remember_previous_messages": False
                }
            },

            "image_models": {
                "user_preferences": {
                    "size_of_image": "1024x1024",
                    "number_of_images": 1,
                    "save_links": True,
                    "save_images": False
                }
            }
        }

        with open("config.json", "w") as json_file:
            json.dump(default_config_data, json_file)

    @staticmethod
    def resource_path(relative_path):
        # if hasattr(sys, "_MEIPASS"):
        #     return os.path.join(sys._MEIPASS, relative_path)
        # else:
        #     return relative_path
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def change_geometry(self, width, height):
        self.geometry(f"{width}x{height}")

    def change_min_size(self, width, height):
        self.minsize(width, height)

    def is_resizable(self, boolean):
        self.resizable(boolean, boolean)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    exit()
