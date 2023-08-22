import tkinter as tk
import customtkinter
import os
import openai
import threading
import webbrowser

from controller_frame import ControllerFrame


class ImageModels(ControllerFrame):
    def create_widgets(self):
        # Image Space
        self.image_space = customtkinter.CTkScrollableFrame(self)
        self.image_space.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Input
        self.input = customtkinter.CTkTextbox(self, font=("New Times Rome", 24))
        self.input.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Option Bar
        self.option_bar_frame = customtkinter.CTkFrame(self)

        # Go to Menu
        self.menu_button = customtkinter.CTkButton(self.option_bar_frame, text="Menu", font=("New Times Rome", 24))
        self.menu_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.menu_button.bind("<Button-1>", lambda event: self.controller.show_frame("Menu"))

        # Size
        self.size_frame = customtkinter.CTkFrame(self.option_bar_frame, fg_color="transparent")
        self.size_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.size_label = customtkinter.CTkLabel(self.size_frame, text="Size of Image:", font=("New Times Rome", 20))
        self.size_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        size = tk.StringVar()
        self.size_radiobutton_256 = customtkinter.CTkRadioButton(self.size_frame, text="256x256", font=("New Times Rome", 14), variable=size, value="256x256")
        self.size_radiobutton_256.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.size_radiobutton_512 = customtkinter.CTkRadioButton(self.size_frame, text="512x512", font=("New Times Rome", 14), variable=size, value="512x512")
        self.size_radiobutton_512.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.size_radiobutton_1024 = customtkinter.CTkRadioButton(self.size_frame, text="1024x1024", font=("New Times Rome", 14), variable=size, value="1024x1024")
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
        self.save_links.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.save_images = customtkinter.CTkCheckBox(self.save_frame, text="images", font=("New Times Rome", 14))
        self.save_images.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.option_bar_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Submit Button
        self.submit_button = customtkinter.CTkButton(self, text="Submit", font=("New Times Rome", 24))
        self.submit_button.bind("<Button-1>", self.submit_button_click)
        self.submit_button.bind("<Return>", self.submit_enter)
        self.submit_button.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Set default values
        size.set("1024x1024")
        self.number_of_images_value.insert(0, "1")

    def submit_button_click(self, event):
        threading.Thread(target=self.submit_async).start()

    def submit_enter(self, event):
        threading.Thread(target=self.submit_async).start()

    counter = 0

    def submit_async(self):
        def link_clicked(link):
            webbrowser.open_new_tab(link)

        n = 1
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        prompt = self.input.get("1.0", tk.END)
        self.input.delete("1.0", tk.END)
        response = openai.Image.create(
            prompt=prompt,
            n=n,
            size="1024x1024"
        )

        for i in range(n):
            link = customtkinter.CTkLabel(self.image_space, text=prompt, font=("New Times Rome", 24), text_color="blue", justify="left")
            link.bind("<Button-1>", lambda event, url=response["data"][i]["url"]:
            link_clicked(url))
            print("test", i, response["data"][i]["url"])
            link.grid(row=self.counter, column=0, sticky="nsew", padx=10, pady=10)
            self.counter += 1





