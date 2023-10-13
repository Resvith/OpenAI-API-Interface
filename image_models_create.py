import io
import json
import os
import threading
import tkinter as tk
import urllib.request
import webbrowser

import customtkinter
import openai
import requests
from PIL import Image

from controller_frame import ControllerFrame


def write_data_to_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


class ImageModelsCreate(ControllerFrame):
    # Variables:
    counter = 0

    def create_widgets(self):
        # Image Space
        self.image_space = customtkinter.CTkScrollableFrame(self, label_anchor="nw")
        self.image_space.grid(row=0, column=0, sticky="nsew", padx=10)

        # Input
        self.input = customtkinter.CTkTextbox(self, font=("New Times Rome", 24))
        self.input.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Option Bar
        self.option_bar_frame = customtkinter.CTkFrame(self)

        # Go to Menu
        self.menu_button = customtkinter.CTkButton(self.option_bar_frame, text="Menu", font=("New Times Rome", 24))
        self.menu_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.menu_button.bind("<Button-1>", command=self.go_to_menu)

        # Size
        self.size_frame = customtkinter.CTkFrame(self.option_bar_frame, fg_color="transparent")
        self.size_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.size_label = customtkinter.CTkLabel(self.size_frame, text="Size of Image:", font=("New Times Rome", 20))
        self.size_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.size = tk.StringVar()
        self.size_radiobutton_256 = customtkinter.CTkRadioButton(self.size_frame, text="256x256", font=("New Times Rome", 14), variable=self.size, value="256x256", command=self.on_size_radiobutton_change)
        self.size_radiobutton_256.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.size_radiobutton_512 = customtkinter.CTkRadioButton(self.size_frame, text="512x512", font=("New Times Rome", 14), variable=self.size, value="512x512", command=self.on_size_radiobutton_change)
        self.size_radiobutton_512.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.size_radiobutton_1024 = customtkinter.CTkRadioButton(self.size_frame, text="1024x1024", font=("New Times Rome", 14), variable=self.size, value="1024x1024", command=self.on_size_radiobutton_change)
        self.size_radiobutton_1024.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

        # Number of Images
        self.number_of_images_frame = customtkinter.CTkFrame(self.option_bar_frame, fg_color="transparent")
        self.number_of_images_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.number_of_images_label = customtkinter.CTkLabel(self.number_of_images_frame, text="Number of images:", font=("New Times Rome", 20))
        self.number_of_images_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.number_of_images_value = customtkinter.CTkEntry(self.number_of_images_frame, font=("New Times Rome", 14))
        self.number_of_images_value.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        # What to save
        self.save_frame = customtkinter.CTkFrame(self.option_bar_frame, fg_color="transparent")
        self.save_frame.grid(row=6, column=0, sticky="nsew", padx=10, pady=10)
        self.save_label = customtkinter.CTkLabel(self.save_frame, text="Save:", font=("New Times Rome", 20))
        self.save_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.save_links = customtkinter.CTkCheckBox(self.save_frame, text="links", font=("New Times Rome", 14))
        self.save_links.bind("<Button-1>", self.on_save_links_click)
        self.save_links.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.save_images = customtkinter.CTkCheckBox(self.save_frame, text="images", font=("New Times Rome", 14))
        self.save_images.bind("<Button-1>", self.on_save_image_click)
        self.save_images.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.option_bar_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Submit Button
        self.submit_button = customtkinter.CTkButton(self, text="Submit", font=("New Times Rome", 24), command=self.on_send_button_click)
        self.bind("<Return>", lambda event: self.controller.enter_clicked(event, "ImageModelsCreate"))
        self.submit_button.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Set default values
        self.set_default_values()

    def set_default_values(self):
        # Create config file if it doesn't exist
        # config_path = self.controller.resource_path("config.json")
        if not (os.path.exists("config.json")):
            self.controller.create_default_config()

        # Load config file to variables:
        with open("config.json", "r+") as config_file:
            config_data = json.load(config_file)
            self.size_of_image_pref = config_data["image_models"]["user_preferences"]["size_of_image"]
            self.number_of_images_pref = config_data["image_models"]["user_preferences"]["number_of_images"]
            self.save_links_pref = config_data["image_models"]["user_preferences"]["save_links"]
            self.save_images_pref = config_data["image_models"]["user_preferences"]["save_images"]

        # Set default values
        self.size.set(self.size_of_image_pref)
        self.number_of_images_value.insert(0, self.number_of_images_pref)
        if self.save_links_pref:
            self.save_links.select()
        if self.save_images_pref:
            self.save_images.select()

    def submit_async(self):
        def link_clicked(image_link):
            webbrowser.open_new_tab(image_link)

        openai.api_key = os.environ.get("OPENAI_API_KEY")
        prompt = self.input.get("1.0", tk.END)
        prompt = prompt.strip()

        # Check if prompt is empty:
        if prompt == "":
            return

        n = int(self.number_of_images_value.get())
        self.input.delete("1.0", tk.END)
        response = openai.Image.create(
            prompt=prompt,
            n=n,
            size=self.size_of_image_pref
        )

        for i in range(n):
            # Show image in tkinter:
            with urllib.request.urlopen(response["data"][i]["url"]) as image_url:
                f = io.BytesIO(image_url.read())
            img = Image.open(f)
            image = customtkinter.CTkImage(img, size=(512, 512))

            image_label = customtkinter.CTkLabel(self.image_space, text=prompt, font=("New Times Rome", 20), anchor="w", justify="left")
            image_label.grid(row=self.counter, column=0, pady=(5, 10), sticky="nsew")
            image_in_app = customtkinter.CTkLabel(self.image_space, text="", image=image)
            image_in_app.bind("<Button-1>", lambda event, url=response["data"][i]["url"]: link_clicked(url))
            image_in_app.bind("<Enter>", lambda event, hover=image_in_app: hover.configure(cursor="hand2"))
            image_in_app.grid(row=self.counter + 1, column=0, pady=(5, 10), sticky="nsew")
            self.counter += 2

            print(prompt, i, response["data"][i]["url"])

        # Saves:
        prompt = prompt[:40]
        self.save_links_to_file(response["data"], prompt, n)
        self.save_images_to_files(response["data"], prompt, n)

    def create_dir_if_not_exists(self):
        image_models_dir_path = self.controller.resource_path("image models")
        images_dir_path = self.controller.resource_path("image models/images")

        if not os.path.exists(image_models_dir_path):
            os.mkdir(image_models_dir_path)
        if not os.path.exists(images_dir_path):
            os.mkdir(images_dir_path)

    def save_images_to_files(self, images, prompt, n):
        # If option off then return
        if not self.save_images_pref:
            return

        self.create_dir_if_not_exists()
        links_path = self.controller.resource_path("image models/links.json")

        # Take id from links.json file:
        with open(links_path, "r+") as links_file:
            links_data = json.load(links_file)
            link_id = links_data["id"]

        # Save images to existing file:
        for i in range(n):
            response = requests.get(images[i]["url"])
            if response.status_code == 200:
                image_file_path = self.controller.resource_path(f"image models/images/{link_id+i}_{prompt}.png")
                with open(image_file_path, "wb") as file:
                    file.write(response.content)

        # Update id in links.json file:
        with open(links_path, "r+") as links_file:
            links_data = json.load(links_file)
            links_data["id"] = link_id + n
            write_data_to_json_file(links_data, links_path)

    def save_links_to_file(self, links, prompt, n):
        # If option off then return
        if not self.save_links_pref:
            return

        self.create_dir_if_not_exists()
        links_path = self.controller.resource_path("image models/links.json")

        # Save links to existing file:
        with open(links_path, "r+") as links_file:
            links_data = json.load(links_file)
            link_id = links_data["id"]

            # If prompt doesn't exist already then create it:
            if prompt not in links_data["links"]:
                links_data["links"][prompt] = {}

            for i in range(n):
                links_data["links"][prompt][link_id] = links[i]["url"]
                link_id += 1

            links_data["id"] = link_id
            write_data_to_json_file(links_data, links_path)

    def on_size_radiobutton_change(self):
        config_path = self.controller.resource_path("config.json")
        with open(config_path, "r+") as config_file:
            config_data = json.load(config_file)
            self.size_of_image_pref = config_data["image_models"]["user_preferences"]["size_of_image"] = self.size.get()
            write_data_to_json_file(config_data, config_path)

    def on_save_image_click(self, event):
        config_path = self.controller.resource_path("config.json")
        with open(config_path, "r+") as config_file:
            config_data = json.load(config_file)
            self.save_images_pref = config_data["image_models"]["user_preferences"]["save_images"] = self.save_images.get()
            write_data_to_json_file(config_data, config_path)

    def on_save_links_click(self, event):
        config_path = self.controller.resource_path("config.json")
        with open(config_path, "r+") as config_file:
            config_data = json.load(config_file)
            self.save_links_pref = config_data["image_models"]["user_preferences"]["save_links"] = self.save_links.get()
            write_data_to_json_file(config_data, config_path)

    def go_to_menu(self, event):
        self.controller.show_frame("Menu")
        self.controller.change_geometry(400, 400)
        self.controller.change_min_size(400, 400)
        self.controller.is_resizable(False)

    def on_send_button_click(self):
        threading.Thread(target=self.submit_async).start()

