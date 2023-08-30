import tkinter as tk
import customtkinter
import threading
import openai

from tkinter import filedialog

from controller_frame import ControllerFrame


class AudioModels(ControllerFrame):
    def __init__(self, master, controller):
        ControllerFrame.__init__(self, master, controller)

    def create_widgets(self):
        self.audio_models_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.audio_models_container.grid(row=0, column=0, sticky="nsew")
        self.audio_models_container.grid_rowconfigure(1, weight=1)
        self.audio_models_container.grid_columnconfigure(0, weight=1)

        # Top frame:
        self.top_frame = customtkinter.CTkFrame(self.audio_models_container, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.select_file_label = customtkinter.CTkLabel(self.top_frame, text="Select File:", font=("New Times Rome", 24))
        self.select_file_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.select_file_button = customtkinter.CTkButton(self.top_frame, text="Select", font=("New Times Rome", 24))
        self.select_file_button.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.select_file_button.bind("<Button-1>", self.on_select_file_button_click)

        # Text frame:
        self.text_frame = customtkinter.CTkFrame(self.audio_models_container, fg_color="transparent")
        self.text_frame.grid(row=1, column=0, sticky="nsew")
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.textbox = customtkinter.CTkTextbox(self.text_frame, font=("New Times Rome", 20), wrap="word")
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Send button:
        self.send_button = customtkinter.CTkButton(self.audio_models_container, text="Send", font=("New Times Rome", 24))
        self.send_button.bind("<Button-1>", self.on_send_button_click)
        self.send_button.grid(row=1, column=1, sticky="sew", padx=10, pady=10)

    def on_select_file_button_click(self, event):
        self.file_path = filedialog.askopenfilename(title="Choose image file",
                                                    filetypes=[("Audio files", ".mp3")])
        if not self.file_path:
            return

        self.select_file_label.configure(text="Selected: " + self.file_path.split("/")[-1])


    def on_send_button_click(self, event):
        if not self.file_path:
            return

        threading.Thread(target=self.api_request).start()

    def api_request(self):
        audio_file = open(self.file_path, "rb")
        response = openai.Audio.transcribe("whisper-1", audio_file)

        print(response)
        self.textbox.insert(tk.END, response["text"])
