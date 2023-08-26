import tkinter as tk
import os
import openai
import tkinter.messagebox
import customtkinter
import threading
import json
import datetime
import tiktoken
from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkOptionMenu, CTkTextbox, CTkEntry, CTkSlider, CTkCheckBox

from controller_frame import ControllerFrame


def write_data_to_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file)


def change_theme_mode(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)


def delete_elements_in_frame(frame):
    frame.children.clear()


def change_temperature_event(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)


class TextModels(ControllerFrame):
    debug_button: CTkButton
    chat_id: None
    remember_previous_messages: CTkCheckBox
    role_textbox: CTkTextbox
    role_label: CTkLabel
    temperature_value_label: CTkLabel
    temperature_sidebar: CTkSlider
    temperature_label: CTkLabel
    max_tokens_entry: CTkEntry
    max_tokens_label: CTkLabel
    menu_button: CTkButton
    input: CTkTextbox
    options_frame: CTkFrame
    chat_space: CTkTextbox
    selected_model_options: CTkOptionMenu
    selected_model_label: CTkLabel
    chat_space_frame: CTkFrame
    send_button: CTkButton
    theme_mode_options: CTkOptionMenu
    theme_mode_label: CTkLabel
    chat_history_frame: CTkFrame
    new_chat_button: CTkButton
    remember_previous_messages_pref: object
    fullscreened_pref: object
    window_height_pref: object
    window_width_pref: object
    theme_mode_pref: object
    temperature_pref: object
    max_tokens_pref: object
    model_pref: object
    left_chats_bar: CTkFrame
    class_container: CTkFrame
    chat_count: object

    def __init__(self, master, controller):
        ControllerFrame.__init__(self, master, controller)
        self.master.class_container = None

    def create_widgets(self):
        # Create config file if no exists:
        if not (os.path.exists("config.json")):
            self.controller.create_default_config()

        # Load config file:
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)
            self.chat_count = config_data["text_models"]["chats_counter"]
            self.model_pref = config_data["text_models"]["user_preferences"]["model"]
            self.max_tokens_pref = config_data["text_models"]["user_preferences"]["max_tokens"]
            self.temperature_pref = config_data["text_models"]["user_preferences"]["temperature"]
            self.theme_mode_pref = config_data["text_models"]["user_preferences"]["theme"]
            self.window_width_pref = config_data["text_models"]["user_preferences"]["window_width"]
            self.window_height_pref = config_data["text_models"]["user_preferences"]["window_height"]
            self.fullscreened_pref = config_data["text_models"]["user_preferences"]["full-screened"]
            self.remember_previous_messages_pref = config_data["text_models"]["user_preferences"]["remember_previous_messages"]

        # Configure class container:
        self.class_container = customtkinter.CTkFrame(self, corner_radius=0)
        self.class_container.grid(row=0, column=0, sticky="nsew")
        self.class_container.grid_columnconfigure(1, weight=1)
        self.class_container.grid_columnconfigure((2, 3), weight=0)
        self.class_container.grid_rowconfigure((0, 1, 2), weight=1)

        # Create left bar frame for chat history and new chat button:
        self.left_chats_bar = customtkinter.CTkFrame(self.class_container, width=140, corner_radius=0)
        self.left_chats_bar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.left_chats_bar.grid_rowconfigure(1, weight=1)
        self.new_chat_button = customtkinter.CTkButton(self.left_chats_bar, command=self.new_chat_click)
        self.new_chat_button.grid(row=0, column=0)
        self.chat_history_frame = customtkinter.CTkFrame(self.left_chats_bar, corner_radius=0)
        self.chat_history_frame.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="nsew")
        self.theme_mode_label = customtkinter.CTkLabel(self.left_chats_bar, text="Appearance Mode:")
        self.theme_mode_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.theme_mode_options = customtkinter.CTkOptionMenu(self.left_chats_bar, values=["Light", "Dark", "System"],
                                                              command=change_theme_mode)
        self.theme_mode_options.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="s")

        # Create input and send button:
        self.input = customtkinter.CTkTextbox(self.class_container, height=60)
        self.input.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.input.bind("<FocusIn>", self.on_input_focus_in)
        self.input.bind("<FocusOut>", self.on_input_focus_out)
        self.send_button = customtkinter.CTkButton(master=self.class_container, fg_color="transparent", border_width=2,
                                                   text_color=("gray10", "#DCE4EE"), text="Send",
                                                   command=self.on_send_button_click)
        self.controller.bind("<Return>", lambda event: self.enter_clicked(event))
        self.send_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Create chat space frame
        self.chat_space_frame = customtkinter.CTkFrame(self.class_container)
        self.chat_space_frame.grid(row=0, column=1, rowspan=3, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.selected_model_label = customtkinter.CTkLabel(self.chat_space_frame, text="Selected Model:",
                                                           anchor="center")
        self.selected_model_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky='ne')
        self.selected_model_options = customtkinter.CTkOptionMenu(self.chat_space_frame, values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"], command=self.change_model_event)
        self.selected_model_options.grid(row=0, column=1, padx=20, pady=(10, 10), sticky='nw')
        self.chat_space = customtkinter.CTkTextbox(self.chat_space_frame, wrap="word", font=("New Times Roma", 14))
        self.chat_space.grid(row=1, rowspan=2, column=0, columnspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.chat_space_frame.grid_rowconfigure(1, weight=1)
        self.chat_space_frame.grid_columnconfigure(2, weight=1)

        # Create options frame:
        self.options_frame = customtkinter.CTkFrame(self.class_container)
        self.options_frame.grid(row=0, rowspan=3, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # Menu button:
        self.menu_button = customtkinter.CTkButton(self.options_frame, text="Go back to the Menu", font=("New Times Roman", 16), command=self.on_menu_button_click)
        self.menu_button.grid(row=0, column=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # Max tokens and temperature:
        self.max_tokens_label = customtkinter.CTkLabel(self.options_frame, text="Max Tokens:", anchor="center")
        self.max_tokens_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky='ne')
        self.max_tokens_entry = customtkinter.CTkEntry(self.options_frame)
        self.max_tokens_entry.grid(row=1, column=1, padx=5, pady=10, sticky='nw')
        self.temperature_label = customtkinter.CTkLabel(self.options_frame, text="Temperature:", anchor="center")
        self.temperature_label.grid(row=2, column=0, padx=(10, 5), pady=10, sticky='ne')
        self.temperature_sidebar = customtkinter.CTkSlider(self.options_frame, from_=0, to=2)
        self.temperature_sidebar.grid(row=2, column=1, padx=5, pady=10, sticky='nw')
        self.temperature_value_label = customtkinter.CTkLabel(self.options_frame, text=str(self.temperature_pref), anchor="center")
        self.temperature_value_label.grid(row=2, column=2, padx=(10, 5), pady=10, sticky='nw')
        self.temperature_sidebar.bind("<B1-Motion>", self.temperature_sidebar_event)

        # Roles:
        self.role_label = customtkinter.CTkLabel(self.options_frame, text="Roles:", anchor="center")
        self.role_label.grid(row=3, column=0, padx=5, pady=(10, 10), sticky='ne')
        self.role_textbox = customtkinter.CTkTextbox(self.options_frame)
        self.role_textbox.grid(row=3, column=0, columnspan=3, padx=5, pady=(10, 10), sticky='nsew')
        self.remember_previous_messages = customtkinter.CTkCheckBox(self.options_frame, text="Remember previous messages")
        self.remember_previous_messages.bind("<Button-1>", self.on_remember_previous_messages_click)
        self.remember_previous_messages.grid(row=4, column=0, columnspan=3, padx=5, pady=(10, 10), sticky='nsew')
        self.debug_button = customtkinter.CTkButton(self.options_frame, text="Debug", command=self.debug)
        self.debug_button.grid(row=5, column=0, columnspan=3, padx=5, pady=(10, 10), sticky='nsew')

        # Set default values and configure:
        self.new_chat_button.configure(text="New Chat")
        self.theme_mode_options.set(self.theme_mode_pref)
        self.chat_space.configure(state="disabled")
        self.temperature_sidebar.set(self.temperature_pref)
        self.selected_model_options.set(self.model_pref)
        self.max_tokens_entry.insert(0, self.max_tokens_pref)
        if self.remember_previous_messages_pref:
            self.remember_previous_messages.select()
        if self.fullscreened_pref:
            self.after(1, self.make_window_fullscreen)
        self.input.after(100, self.input.focus_set)
        self.chat_id = None

        # Load previous chat to chat history:
        self.load_previous_chats_to_chat_history()

    def debug(self):
        pass
        # Debug, check models:
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        # model_list = openai.Model.list()
        # for model in model_list.data:
        #     print(model.id)

    def load_previous_chats_to_chat_history(self):
        if os.path.exists("chats"):
            chats_list = os.listdir("chats")
            chats_list.reverse()
            max_chats = 30
            i = 0

            while len(chats_list) > i < max_chats:
                button_name = chats_list[i]
                button_name = button_name.replace(".json", "")
                button = customtkinter.CTkButton(self.chat_history_frame, text=button_name, anchor="center", font=("New Times Roma", 12), fg_color="transparent")
                button.bind("<Button-1>", lambda event, bn=button_name: self.load_other_chat_config_and_chat_story(bn))
                button.grid(row=i, column=0, pady=1, sticky="we")
                i += 1

    def load_other_chat_config_and_chat_story(self, file_name):
        self.chat_space.configure(state="normal")
        self.chat_space.delete("1.0", tkinter.END)

        with open("chats/" + file_name + ".json", "r") as chat_file:
            chat_data = json.load(chat_file)

            # Load chat previous data:
            self.chat_id = chat_data["parameters"]["chat_id"]
            self.max_tokens_entry.delete(0, tkinter.END)
            self.max_tokens_entry.insert(0, chat_data["parameters"]["max_tokens"])
            self.temperature_sidebar.set(float(chat_data["parameters"]["temperature"]))
            self.temperature_value_label.configure(text=str(chat_data["parameters"]["temperature"]))
            self.selected_model_options.set(chat_data["parameters"]["model"])
            self.role_textbox.configure(state="normal")
            self.role_textbox.delete("1.0", tkinter.END)
            self.role_textbox.insert("1.0", chat_data["parameters"]["role"])
            self.role_textbox.configure(state="disabled")

            # Load chat messages:
            for message in chat_data["messages"]:
                self.chat_space.insert(tk.END, (message["content"] + message["answer"]))

        self.chat_space.configure(state="disable")

    def api_request(self, prompt):
        # Get values:
        model = self.selected_model_options.get()
        max_tokens = int(self.max_tokens_entry.get())
        temperature = float(self.temperature_value_label.cget("text"))

        # Clear input:
        self.chat_space.configure(state="normal")
        self.chat_space.insert(tk.END, prompt)
        self.input.delete("1.0", tkinter.END)

        messages = self.load_previous_messages_and_count_its_tokens(prompt)

        # Execute prompt:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        chat_completion = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            messages=messages
        )

        # Get response into chat space:
        complete_message = ""
        for chunk in chat_completion:
            if chunk and chunk['choices'][0]['delta'] != {}:
                chunk_message = chunk['choices'][0]['delta']['content']
                complete_message += chunk_message
                self.chat_space.insert(tk.END, chunk_message)
                self.chat_space.see(tk.END)

        self.chat_space.insert(tk.END, "\n\n")
        self.chat_space.configure(state="disabled")
        self.save_chat_to_file(prompt, complete_message)

    def save_chat_to_file(self, prompt, response):
        if self.chat_id is None:
            with open("config.json", "r+") as config_file:
                config_parameters = json.load(config_file)
                config_parameters["text_models"]["chats_counter"] += 1
                write_data_to_json_file(config_parameters, "config.json")

            self.chat_id = config_parameters["text_models"]["chats_counter"]

            is_folder_chats_exist = os.path.exists("chats")
            if not is_folder_chats_exist:
                os.mkdir("chats")

            with open(f"chats/chat_{self.chat_id}.json", "a") as chat_file:
                chat_file_data = {
                    "parameters": {
                        "chat_id": self.chat_id,
                        "model": self.selected_model_options.get(),
                        "max_tokens": self.max_tokens_entry.get(),
                        "temperature": self.temperature_value_label.cget("text"),
                        "role": self.role_textbox.get("1.0", tkinter.END),
                        "tokens_counter": 0,
                        "messages_counter": 0,
                        "date": f"{datetime.datetime.now().strftime('%d/%m/%Y')}"
                    },
                    "messages": []
                }
                json.dump(chat_file_data, chat_file)
                self.role_textbox.configure(state="disabled")   # Disable role textbox after first message

            # self.delete_elements_in_frame(self.class_container.children["!ctkframe"])
            delete_elements_in_frame(self.chat_history_frame)
            self.load_previous_chats_to_chat_history()

        with open(f"chats/chat_{self.chat_id}.json", "r+") as chat_file:
            chat_file_data = json.load(chat_file)
            message = {
                "content": prompt,
                "answer": response
            }
            chat_file_data["messages"].append(message)
            chat_file_data["parameters"]["messages_counter"] += 1

            # Count tokens for prompt and response:
            tokens_consumed = self.count_tokens_for_text(prompt + response)
            chat_file_data["parameters"]["tokens_counter"] += tokens_consumed

            write_data_to_json_file(chat_file_data, f"chats/chat_{self.chat_id}.json")

    def load_previous_messages_and_count_its_tokens(self, prompt):
        messages = []
        if self.chat_id and self.remember_previous_messages_pref:
            tokens_limit = 1000
            tokens_counter = 0

            with open(f"chats/chat_{self.chat_id}.json", "r+") as chat_file:
                chat_data = json.load(chat_file)
                messages.append({"role": "system", "content": chat_data["parameters"]["role"]})
                tokens_counter += self.count_tokens_for_text(chat_data["parameters"]["role"])
                for i in range(len(chat_data["messages"]) - 1, -1, -1):
                    tokens_counter += self.count_tokens_for_text(chat_data["messages"][i]["content"])
                    tokens_counter += self.count_tokens_for_text(chat_data["messages"][i]["answer"])
                    if tokens_limit > tokens_counter:
                        messages.append({"role": "user", "content": chat_data["messages"][i]["content"]})
                        messages.append({"role": "system", "content": chat_data["messages"][i]["answer"]})
                    else:
                        break

                # Save counted tokens (prompt and response are counted later):
                chat_data["parameters"]["tokens_counter"] += tokens_counter

                messages.append({"role": "user", "content": "\n" + prompt})
                write_data_to_json_file(chat_data, f"chats/chat_{self.chat_id}.json")

        else:  # If the conversation hasn't started yet:
            messages.append({"role": "system", "content": self.role_textbox.get("1.0", tkinter.END)})
            messages.append({"role": "user", "content": prompt})

        return messages

    def check_correct_input(self):
        # Check if input is empty:
        prompt = self.input.get("1.0", tkinter.END)
        if prompt == "Send a message\n" or not prompt.strip():
            return
        self.api_request(prompt)

    def new_chat_click(self):
        self.chat_id = None
        self.role_textbox.configure(state="normal")
        self.chat_space.configure(state="normal")
        self.chat_space.delete("1.0", tkinter.END)
        self.chat_space.configure(state="disabled")

    def on_remember_previous_messages_click(self, event):
        with open("config.json", "r+") as config_file:
            config_data = json.load(config_file)
            self.remember_previous_messages_pref = config_data["text_models"]["user_preferences"]["remember_previous_messages"] = self.remember_previous_messages.get()
            write_data_to_json_file(config_data, "config.json")

    def on_input_focus_in(self, event):
        if self.input.get("1.0", tk.END) == "Send a message\n":
            self.input.delete("1.0", tk.END)

    def on_input_focus_out(self, event):
        if self.input.get("1.0", tk.END) == "\n":
            self.input.insert("1.0", "Send a message")

    def temperature_sidebar_event(self, event):
        formatted_value = format(self.temperature_sidebar.get(), '.2f')
        self.temperature_value_label.configure(text=str(formatted_value))

    def change_model_event(self, new_model: str):
        pass

    def count_tokens_for_text(self, text):
        encoding = tiktoken.encoding_for_model(self.selected_model_options.get())
        return len(encoding.encode(text))

    def make_window_fullscreen(self):
        self.controller.state('zoomed')

    def enter_clicked(self, event):
        if not (event.state and 0x1):  # Check if Shift key is not pressed
            threading.Thread(target=self.check_correct_input).start()

    def on_menu_button_click(self):
        self.controller.show_frame("Menu")
        self.controller.change_geometry(400, 400)
        self.controller.change_min_size(400, 400)

    def on_send_button_click(self):
        threading.Thread(target=self.check_correct_input).start()
