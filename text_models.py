import tkinter as tk
import os
import openai
import tkinter.messagebox
import customtkinter
import threading
import json
import datetime
import tiktoken
import re
from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkOptionMenu, CTkTextbox, CTkEntry, CTkSlider, CTkCheckBox, CTkScrollableFrame

from controller_frame import ControllerFrame
from PIL import Image
from pygments.lexers import get_lexer_by_name
from pygments import lex, styles


def write_data_to_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


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
    chat_space_frame: CTkScrollableFrame
    selected_model_options: CTkOptionMenu
    selected_model_label: CTkLabel
    center_frame: CTkFrame
    send_button: CTkButton
    theme_mode_options: CTkOptionMenu
    theme_mode_label: CTkLabel
    chat_history_frame: CTkScrollableFrame
    new_chat_button: CTkButton
    remember_previous_messages_pref: int
    fullscreened_pref: bool
    window_height_pref: int
    window_width_pref: int
    theme_mode_pref: str
    temperature_pref: float
    max_tokens_pref: int
    model_pref: str
    left_chats_bar: CTkFrame
    class_container: CTkFrame
    chat_count: int

    def __init__(self, master, controller):
        ControllerFrame.__init__(self, master, controller)
        self.master.class_container = None
        self.messages = []

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
        self.class_container.grid_columnconfigure(2, weight=0)
        self.class_container.grid_columnconfigure(3, weight=0)
        self.class_container.grid_rowconfigure(0, weight=1)
        self.class_container.grid_rowconfigure(1, weight=1)
        self.class_container.grid_rowconfigure(2, weight=1)

        # Create left bar frame for chat history and new chat button:
        self.left_chats_bar = customtkinter.CTkFrame(self.class_container, width=140, corner_radius=0)
        self.left_chats_bar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.left_chats_bar.grid_rowconfigure(1, weight=1)
        self.new_chat_button = customtkinter.CTkButton(self.left_chats_bar, command=self.new_chat_click)
        self.new_chat_button.grid(row=0, column=0)
        self.chat_history_frame = customtkinter.CTkScrollableFrame(self.left_chats_bar, corner_radius=0)
        self.chat_history_frame.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="nsew")
        self.chat_history_frame.grid_columnconfigure(0, weight=1)
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
        self.bind("<Return>", lambda event: self.controller.enter_clicked(event, "TextModels"))
        self.send_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Create chat space frame
        self.center_frame = customtkinter.CTkFrame(self.class_container)
        self.center_frame.grid(row=0, column=1, rowspan=3, columnspan=2, pady=(20, 0), sticky="nsew")
        self.selected_model_label = customtkinter.CTkLabel(self.center_frame, text="Selected Model:",
                                                           anchor="center")
        self.selected_model_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky='ne')
        self.selected_model_options = customtkinter.CTkOptionMenu(self.center_frame, values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"], command=self.change_model_event)
        self.selected_model_options.grid(row=0, column=1, padx=20, pady=(10, 10), sticky='nw')
        self.chat_space_frame = customtkinter.CTkScrollableFrame(self.center_frame)
        self.chat_space_frame.grid(row=1, rowspan=2, column=0, columnspan=3, sticky="nsew")

        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_columnconfigure(2, weight=1)

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
        self.temperature_sidebar.set(self.temperature_pref)
        self.selected_model_options.set(self.model_pref)
        self.max_tokens_entry.insert(0, self.max_tokens_pref)
        if self.remember_previous_messages_pref:
            self.remember_previous_messages.select()
        if self.fullscreened_pref:
            self.after(1, self.make_window_fullscreen)
        self.input.after(100, self.input.focus_set)
        self.chat_id = None
        self.current_messages_count = 0
        self.is_scrolled_up = False
        self.max_chats = 30

        # Bind events:
        self.controller.bind("<Configure>", self.make_window_responsive)
        self.chat_history_frame.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_in_chat_history(event))

        # Load previous chat to chat history:
        self.load_previous_chats_to_chat_history()
        self.chat_space_frame_clear()

    def debug(self):
        pass
        # Debug, check models:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        model_list = openai.Model.list()
        for model in model_list.data:
            print(model.id)

    def load_previous_chats_to_chat_history(self):
        if os.path.exists("chats"):
            chats_list = os.listdir("chats")
            self.sorted_chat_list = sorted(chats_list, key=lambda x: os.path.getmtime(os.path.join("chats", x)), reverse=True)
            i = 0

            while len(self.sorted_chat_list) > i < self.max_chats:
                button_name = self.sorted_chat_list[i]
                button_name = button_name.replace(".json", "")
                button = customtkinter.CTkButton(self.chat_history_frame, text=button_name, anchor="center", font=("New Times Roma", 12), fg_color="transparent")
                button.bind("<Button-1>", lambda event, bn=button_name: self.load_other_chat_config_and_chat_story(bn))
                button.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_in_chat_history(event))
                button.grid(row=i, column=0, pady=1, sticky="we")
                i += 1

    def load_other_chat_config_and_chat_story(self, file_name):
        self.chat_space_frame_clear()
        self.messages.clear()
        self.current_messages_count = 0

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
                self.write_new_message(message["input"]["content"], "user")
                self.write_new_message(message["answer"]["content"], "ai")

            self.update_idletasks()
            self.after(10, threading.Thread(target=self.change_height_of_messages).start())

    def change_height_of_messages(self):
        for i in range(len(self.messages) - 1, -1, -1):
            self.change_height_of_message(self.messages[i])

    def change_height_of_message(self, message):
        h = message.winfo_height()
        while not self.is_scrollbar_exist(message):
            h += 25
            message.configure(height=h)
            self.move_scrollbar_to_bottom()

    def change_height_of_message_in_real_time(self, message):
        h = message.winfo_height()
        while not message._hide_y_scrollbar:
            h += 10
            message.configure(height=h)

    @staticmethod
    def is_scrollbar_exist(message):
        message._y_scrollbar.update()
        return message._hide_y_scrollbar

    def make_window_responsive(self, event):
        width = self.master.winfo_width()
        if not self.chat_space_frame.children:
            return
        if width < 1300:
            self.chat_space_frame.grid_columnconfigure(0, weight=0)
            self.chat_space_frame.grid_columnconfigure(2, weight=0)
        elif width < 1700:
            self.chat_space_frame.grid_columnconfigure(0, weight=2)
            self.chat_space_frame.grid_columnconfigure(2, weight=2)
        else:
            self.chat_space_frame.grid_columnconfigure(0, weight=5)
            self.chat_space_frame.grid_columnconfigure(2, weight=5)

    @staticmethod
    def find_code_to_highlight(textbox):
        matches = []
        language = ""
        text = textbox.get("1.0", tk.END).splitlines()
        pattern = "```"
        for i, line in enumerate(text):
            for match in re.finditer(pattern, line):
                matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))

        if matches:
            lang_end = matches[0][0].split(".")[0] + ".end"
            language = textbox.get(matches[0][1], lang_end)

        if language == "":
            language = "shell"

        return matches, language

    def highlight_code(self, textbox):
        def colorize_syntax(first_match_pair, second_match_pair):
            # Load style and formatter:
            textbox.mark_set(first_match_pair[0], "1.0")
            range_start = first_match_pair[1]
            range_end = second_match_pair[0]
            textbox.mark_set("range_start", range_start)
            text = textbox.get(range_start, range_end)
            selected_style = styles.get_style_by_name("github-dark")     # Get specific style
            style_items = selected_style.styles.items()
            text_color_style = []
            for key, value in style_items:
                if value is not None:
                    pattern = r"(?:bold|no|border|italic|underline|bg)\s*|:#[a-fA-F0-9]+\s*"
                    result = re.sub(pattern, '', value)
                    text_color_style.append((key, result.strip()))

            # Configure for tags:
            for key, value in text_color_style:
                textbox.tag_config(str(key), foreground=str(value))

            # Add tags to specific tokens:
            for token, content in lex(text, get_lexer_by_name(language)):
                textbox.mark_set("range_end", "range_start + %dc" % len(content))
                textbox.tag_add(str(token), "range_start", "range_end")
                textbox.mark_set("range_start", "range_end")

            # Cleaning:
            textbox.mark_unset(first_match_pair[0])
            textbox.mark_unset("range_start")

        def create_window_for_code(first_match_pair, second_match_pair):
            # Black background:
            textbox.tag_config("code_background", background="#000000", lmargin1=15)
            textbox.tag_add("code_background", first_match_pair[1], str(float(second_match_pair[0])+1.0))
            textbox.tag_add("code_background", first_match_pair[1], second_match_pair[0])
            # Title:
            textbox.tag_config("code_title", background="#2C3032", foreground="#F5F5F5", spacing1=5, spacing3=5)
            textbox.tag_add("code_title", first_match_pair[0], str(float(first_match_pair[0])+1.0))
            # ``` tag delete:
            textbox.delete(first_match_pair[0], first_match_pair[1])
            textbox.delete(second_match_pair[0], second_match_pair[1])

        # Find code to highlight and highlight it:
        matches, language = self.find_code_to_highlight(textbox)
        for i in range(0, len(matches), 2):
            if not matches[i + 1]:
                break
            colorize_syntax(matches[i], matches[i + 1])
            create_window_for_code(matches[i], matches[i + 1])

    def change_style_of_message(self, textbox):
        textbox.tag_config("all_space_of_chat", spacing2=6)
        textbox.tag_add("all_space_of_chat", "1.0", tk.END)
        self.highlight_code(textbox)

    def add_icon_to_message(self, role):
        dark_image_path = ""
        if role == "user":
            dark_image_path = "img/user_icon_64.png"
        elif role == "ai":
            dark_image_path = "img/ai_icon_64.png"

        dark_image = Image.open(dark_image_path)
        image = customtkinter.CTkImage(dark_image=dark_image, size=(32, 32))
        icon_in_app = customtkinter.CTkLabel(self.chat_space_frame, image=image, text="")
        icon_in_app.grid(row=self.current_messages_count, column=0, padx=(0, 5), pady=(20, 0), sticky="ne")

    def write_new_message(self, message, role):
        self.add_icon_to_message(role)
        new_message = customtkinter.CTkTextbox(self.chat_space_frame, font=("New Times Roman", 15), wrap="word", height=35)
        new_message.grid(row=self.current_messages_count, column=1, pady=(20, 0), sticky="new")
        self.chat_space_frame.grid_columnconfigure(1, weight=10)
        new_message.insert(tk.END, message)
        self.change_style_of_message(new_message)
        new_message.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_up_in_textbox(event))
        self.messages.append(new_message)

        self.current_messages_count += 1

    def api_request(self, prompt):
        # Get values:
        model = self.selected_model_options.get()
        max_tokens = int(self.max_tokens_entry.get())
        temperature = float(self.temperature_value_label.cget("text"))

        # Clear input:
        self.write_new_message(prompt, "user")
        self.input.delete("1.0", tkinter.END)
        self.move_scrollbar_to_bottom()

        messages = self.remember_previous_messages_and_count_its_tokens(prompt)

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
        self.write_new_message("", "ai")
        self.messages[-1].configure(state="normal")
        self.messages[-1].unbind("<Configure>")
        for chunk in chat_completion:
            if chunk and chunk['choices'][0]['delta'] != {}:
                chunk_message = chunk['choices'][0]['delta']['content']
                complete_message += chunk_message

                self.messages[-1].insert(tk.END, chunk_message)
                self.change_height_of_message_in_real_time(self.messages[-1])
                self.move_scrollbar_to_bottom()

        self.highlight_code(self.messages[-1])
        height_of_response = self.messages[-1].winfo_height()
        width_of_response = self.messages[-1].winfo_width()
        height_of_input = self.messages[-2].winfo_height()
        width_of_input = self.messages[-2].winfo_width()

        self.messages[-1].configure(state="disable")
        self.save_chat_to_file(prompt, complete_message, height_of_response, width_of_response, height_of_input, width_of_input)

    def save_chat_to_file(self, prompt, response, height_of_response, width_of_response, height_of_input, width_of_input):
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

            delete_elements_in_frame(self.chat_history_frame)
            self.load_previous_chats_to_chat_history()

        with open(f"chats/chat_{self.chat_id}.json", "r+") as chat_file:
            chat_file_data = json.load(chat_file)
            message = {
                "input": {
                    "content": prompt,
                    "height": height_of_input,
                    "width": width_of_input,
                },
                "answer": {
                    "content": response,
                    "height": height_of_response,
                    "width": width_of_response,
                }
            }
            chat_file_data["messages"].append(message)
            chat_file_data["parameters"]["messages_counter"] += 1

            # Count tokens for prompt and response:
            tokens_consumed = self.count_tokens_for_text(prompt + response)
            chat_file_data["parameters"]["tokens_counter"] += tokens_consumed

            write_data_to_json_file(chat_file_data, f"chats/chat_{self.chat_id}.json")

    def remember_previous_messages_and_count_its_tokens(self, prompt):
        messages = []
        if self.chat_id and self.remember_previous_messages_pref:
            tokens_limit = 1000
            tokens_counter = 0

            with open(f"chats/chat_{self.chat_id}.json", "r+") as chat_file:
                chat_data = json.load(chat_file)
                messages.append({"role": "system", "content": chat_data["parameters"]["role"]})
                tokens_counter += self.count_tokens_for_text(chat_data["parameters"]["role"])
                for i in range(len(chat_data["messages"]) - 1, -1, -1):
                    tokens_counter += self.count_tokens_for_text(chat_data["messages"][i]["input"]["content"])
                    tokens_counter += self.count_tokens_for_text(chat_data["messages"][i]["answer"]["content"])
                    if tokens_limit > tokens_counter:
                        messages.append({"role": "user", "content": chat_data["messages"][i]["input"]["content"]})
                        messages.append({"role": "system", "content": chat_data["messages"][i]["answer"]["content"]})
                    else:
                        break

                # Save counted tokens (prompt and response are counted later):
                chat_data["parameters"]["tokens_counter"] += tokens_counter

                messages.append({"role": "user", "content": prompt})
                write_data_to_json_file(chat_data, f"chats/chat_{self.chat_id}.json")

        else:  # If the conversation hasn't started yet:
            messages.append({"role": "system", "content": self.role_textbox.get("1.0", tkinter.END)})
            messages.append({"role": "user", "content": prompt})

        return messages

    def on_mouse_scroll_up(self, event):
        if event.delta > 0:
            self.is_scrolled_up = True
        elif self.chat_space_frame._scrollbar._end_value >= 0.975:
            self.is_scrolled_up = False

    def move_scrollbar_to_bottom(self):
        if self.is_scrolled_up:
            return
        self.chat_space_frame._scrollbar._command("moveto", 1.0)

    def on_mouse_scroll_up_in_textbox(self, event):
        if event.delta > 0:
            self.is_scrolled_up = True

    def load_more_chats_to_chat_history(self):
        # Don't forget previously loaded chats
        number_of_chats = len(self.sorted_chat_list)
        now_is_loaded_chats = min(number_of_chats, self.max_chats)
        if number_of_chats <= self.max_chats:
            return
        self.max_chats += 3
        if self.max_chats > number_of_chats:
            self.max_chats = number_of_chats

        # Load more chats:
        for i in range(now_is_loaded_chats, self.max_chats):
            button_name = self.sorted_chat_list[i]
            button_name = button_name.replace(".json", "")
            button = customtkinter.CTkButton(self.chat_history_frame, text=button_name, anchor="center",
                                             font=("New Times Roma", 12), fg_color="transparent")
            button.bind("<Button-1>", lambda event, bn=button_name: self.load_other_chat_config_and_chat_story(bn))
            button.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_in_chat_history(event))
            button.grid(row=i, column=0, pady=1, sticky="we")

    def on_mouse_scroll_in_chat_history(self, event):
        if event.delta < 0 and self.chat_history_frame._scrollbar._end_value >= 0.975:
            self.load_more_chats_to_chat_history()

    def check_correct_input(self):
        # Check if input is empty:
        prompt = self.input.get("1.0", tkinter.END)
        if prompt == "Send a message\n" or not prompt.strip():
            return
        self.api_request(prompt.strip())

    def new_chat_click(self):
        print("Debug: New chat clicked")
        self.chat_id = None
        self.messages.clear()
        self.current_messages_count = 0
        self.role_textbox.configure(state="normal")
        self.chat_space_frame_clear()

    def chat_space_frame_clear(self):
        self.chat_space_frame._scrollbar.grid_forget()
        self.chat_space_frame.destroy()
        self.chat_space_frame = customtkinter.CTkScrollableFrame(self.center_frame)
        self.chat_space_frame.grid(row=1, rowspan=2, column=0, columnspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.chat_space_frame.grid_columnconfigure(1, weight=10)
        self.chat_space_frame.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_up(event))

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
        print("Debug: Enter clicked")
        if not (event.state and 0x1):  # Check if Shift key is not pressed
            print("Debug: Prompt send")
            threading.Thread(target=self.check_correct_input).start()

    def on_menu_button_click(self):
        self.controller.show_frame("Menu")
        self.controller.change_geometry(400, 400)
        self.controller.change_min_size(400, 400)
        self.controller.is_resizable(False)

    def on_send_button_click(self):
        threading.Thread(target=self.check_correct_input).start()
