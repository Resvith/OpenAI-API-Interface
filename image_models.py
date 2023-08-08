import tkinter as tk
import customtkinter
import os
import openai
import threading
import webbrowser

from controller_frame import ControllerFrame


class ImageModels(ControllerFrame):
    def create_widgets(self):
        self.image_space = customtkinter.CTkScrollableFrame(self)
        self.image_space.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.input = customtkinter.CTkTextbox(self, font=("New Times Rome", 24))
        self.input.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.submit_button = customtkinter.CTkButton(self, text="Submit", font=("New Times Rome", 24))
        self.submit_button.bind("<Button-1>", self.submit_button_click)
        self.submit_button.bind("<Return>", self.submit_enter)
        self.submit_button.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

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





