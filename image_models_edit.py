import tkinter as tk
import customtkinter
import os
import openai
import threading
import webbrowser
import json
import io
import urllib.request
import requests

from tkinter import filedialog

from controller_frame import ControllerFrame
from PIL import Image


def write_data_to_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


class ImageModelsEdit(ControllerFrame):

    def create_widgets(self):
        # Container for all widgets:
        self.class_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.class_container.grid(row=0, rowspan=2, column=0, sticky="nsew", padx=20, pady=20)
        self.class_container.grid_columnconfigure(0, weight=1)
        self.class_container.grid_columnconfigure(1, weight=0)
        self.class_container.grid_rowconfigure(0, weight=1)
        self.class_container.grid_rowconfigure(1, weight=20)
        self.class_container.grid_rowconfigure(2, weight=1)
        self.class_container.grid_rowconfigure(3, weight=0)


        # Top frame:
        self.top_frame = customtkinter.CTkFrame(self.class_container, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=10)
        self.top_frame.grid_columnconfigure(2, weight=2)
        self.top_frame.grid_rowconfigure(0, weight=1)

        # Add file button:
        self.add_file_button = customtkinter.CTkButton(self.top_frame, text="+", font=("New Times Rome", 20), width=50, height=50, command=self.on_add_file_button_click)
        self.add_file_button.grid(row=0, column=0, sticky="w", padx=10)

        # Loaded file info:
        self.loaded_file_info_label = customtkinter.CTkLabel(self.top_frame, text="No file loaded", font=("New Times Rome", 20), anchor="w")
        self.loaded_file_info_label.grid(row=0, column=1, sticky="nsew", padx=10)

        # Switch variations frame and label:
        self.switch_variations = customtkinter.CTkFrame(self.top_frame, fg_color="transparent")
        self.switch_variations.grid(row=0, column=2, sticky="e", padx=10)
        self.switch_variations_label = customtkinter.CTkLabel(self.switch_variations, text="0/0", font=("New Times Rome", 20))
        self.switch_variations_label.grid(row=0, column=0, sticky="e", padx=10)

        # Switch variations buttons:
        self.switch_variations_back_button = customtkinter.CTkButton(self.switch_variations, text="<", font=("New Times Rome", 20), width=50, height=50)
        self.switch_variations_back_button.grid(row=0, column=1, sticky="e", padx=10)
        self.switch_variations_next_button = customtkinter.CTkButton(self.switch_variations, text=">", font=("New Times Rome", 20), width=50, height=50)
        self.switch_variations_next_button.grid(row=0, column=2, sticky="e", padx=10)

        # Image frame:
        self.image_frame = customtkinter.CTkFrame(self.class_container)
        self.image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.image_frame.grid_columnconfigure(0, weight=1)

        # Input:
        self.input_textbox = customtkinter.CTkTextbox(self.class_container, font=("New Times Rome", 20))
        self.input_textbox.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Options frame:
        self.options_frame = customtkinter.CTkFrame(self.class_container, fg_color="transparent")
        self.options_frame.grid(row=0, rowspan=2, column=1, sticky="nsew", padx=10)

        # Menu button:
        self.go_to_menu_button = customtkinter.CTkButton(self.options_frame, text="Menu", font=("New Times Rome", 20), command=self.go_to_menu)
        self.go_to_menu_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=(5, 10))

        # Show original image button:
        self.show_original_image_button = customtkinter.CTkButton(self.options_frame, text="Show original image", font=("New Times Rome", 20))
        self.show_original_image_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Show edited image button:
        self.show_edited_image_button = customtkinter.CTkButton(self.options_frame, text="Show edited image", font=("New Times Rome", 20))
        self.show_edited_image_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Save as button:
        self.save_as_button = customtkinter.CTkButton(self.options_frame, text="Save as", font=("New Times Rome", 20))
        self.save_as_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Save in images button:
        self.save_in_images_button = customtkinter.CTkButton(self.options_frame, text="Save in images", font=("New Times Rome", 20))
        self.save_in_images_button.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        # Request parameter frame:
        self.request_parameter_frame = customtkinter.CTkFrame(self.options_frame, fg_color="transparent")
        self.request_parameter_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)

        # Number of variations:
        self.number_of_variations_label = customtkinter.CTkLabel(self.request_parameter_frame, text="Number of variations:", font=("New Times Rome", 20), anchor="w")
        self.number_of_variations_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.number_of_variations_option_menu = customtkinter.CTkOptionMenu(self.request_parameter_frame, font=("New Times Rome", 20), values=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
        self.number_of_variations_option_menu.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Size of generated image:
        self.size_of_generated_image_label = customtkinter.CTkLabel(self.request_parameter_frame, text="Size of generated image:", font=("New Times Rome", 20), anchor="w")
        self.size_of_generated_image_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.size_of_generated_image_option_menu = customtkinter.CTkOptionMenu(self.request_parameter_frame, font=("New Times Rome", 20), values=['256x256', '512x512', '1024x1024'])
        self.size_of_generated_image_option_menu.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Send button:
        self.send_button = customtkinter.CTkButton(self.class_container, text="Send", font=("New Times Rome", 20))
        self.send_button.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

    def on_add_file_button_click(self):
        self.file_path = filedialog.askopenfilename(title="Choose image file", filetypes=[("Image files", ".jpg .jpeg .png")])
        if not self.file_path:
            print("zamkniety")
            return

        self.loaded_file_info_label.configure(text=f"Selected: {self.file_path.split('/')[-1]}")
        img_data = Image.open(self.file_path)

        self.image_frame.children.clear()
        image = customtkinter.CTkImage(img_data, size=(512, 512))
        image_in_app = customtkinter.CTkLabel(self.image_frame, image=image, text="")
        image_in_app.grid(row=0, column=0, sticky="nsew")


    def set_default_values(self):
        # Create config file if it doesn't exist
        if not (os.path.exists("config.json")):
            self.controller.create_default_config()

        # Load config file to variables:
        with open("config.json", "r") as config_file:
            pass

    def go_to_menu(self):
        self.controller.show_frame("Menu")
        self.controller.change_geometry(400, 400)
        self.controller.change_min_size(400, 400)
        self.controller.is_resizable(False)
