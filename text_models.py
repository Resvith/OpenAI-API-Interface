import datetime
import json
import os
import re
import threading
import tkinter as tk
import tkinter.messagebox

import customtkinter
import openai
import tiktoken
from PIL import Image
from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkOptionMenu, CTkTextbox, CTkEntry, CTkSlider, CTkCheckBox, \
    CTkScrollableFrame, CTkImage
from pygments import lex, styles
from pygments.lexers import get_lexer_by_name

from controller_frame import ControllerFrame


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
    send_button: CTkButton
    theme_mode_options: CTkOptionMenu
    theme_mode_label: CTkLabel
    chat_history_frame: CTkScrollableFrame
    new_chat_button: CTkButton
    remember_previous_messages_pref: int
    full_screened_pref: bool
    window_height_pref: int
    window_width_pref: int
    theme_mode_pref: str
    temperature_pref: float
    max_tokens_pref: int
    model_pref: str
    left_chats_bar: CTkFrame
    class_container: CTkFrame
    chat_count: int
    number_of_all_messages: int
    sorted_chat_list: list[str]
    new_buttons_limit: int
    first_button_row: int
    last_button_row: int
    chat_space_empty_textbox: CTkTextbox
    center_frame = CTkFrame

    def __init__(self, master, controller):
        ControllerFrame.__init__(self, master, controller)
        self.is_scrolled_up = None
        self.master.class_container = None
        self.current_button_frame_selected = None
        self.currently_loaded_messages = 0
        self.currently_new_messages_count = 0
        self.number_of_all_messages = 0
        self.current_chat_row = 0
        self.button_row = 50
        self.max_chats = 30
        self.messages = []

    def create_widgets(self):
        # Create config file if no exists:
        if not (os.path.exists("config.json")):
            self.controller.create_default_config()
            print("Debug, created new config")

        config_path = self.controller.resource_path("config.json")
        print("Debug resource path:", config_path)
        # Load config file:
        with open("config.json", "r") as config_file:
            print("Debug, loaded config")
            config_data = json.load(config_file)
            self.chat_count = config_data["text_models"]["chats_counter"]
            self.model_pref = config_data["text_models"]["user_preferences"]["model"]
            self.max_tokens_pref = config_data["text_models"]["user_preferences"]["max_tokens"]
            self.temperature_pref = config_data["text_models"]["user_preferences"]["temperature"]
            self.theme_mode_pref = config_data["text_models"]["user_preferences"]["theme"]
            self.window_width_pref = config_data["text_models"]["user_preferences"]["window_width"]
            self.window_height_pref = config_data["text_models"]["user_preferences"]["window_height"]
            self.full_screened_pref = config_data["text_models"]["user_preferences"]["full-screened"]
            self.remember_previous_messages_pref = (
                config_data["text_models"]["user_preferences"]["remember_previous_messages"]
            )

        # Configure class container:
        self.class_container = CTkFrame(self, corner_radius=0)
        self.class_container.grid(row=0, column=0, sticky="nsew")
        self.class_container.grid_columnconfigure(1, weight=1)
        self.class_container.grid_columnconfigure(2, weight=0)
        self.class_container.grid_columnconfigure(3, weight=0)
        self.class_container.grid_rowconfigure(0, weight=1)
        self.class_container.grid_rowconfigure(1, weight=1)
        self.class_container.grid_rowconfigure(2, weight=1)

        # Create left bar frame for chat history and new chat button:
        self.left_chats_bar = CTkFrame(self.class_container, width=140, corner_radius=0)
        self.left_chats_bar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.left_chats_bar.grid_rowconfigure(1, weight=1)

        self.new_chat_button = CTkButton(self.left_chats_bar, command=self.new_chat_click)
        self.new_chat_button.grid(row=0, column=0)

        self.chat_history_frame = CTkScrollableFrame(self.left_chats_bar, corner_radius=0)
        self.chat_history_frame.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="nsew")
        self.chat_history_frame.grid_columnconfigure(0, weight=1)

        self.theme_mode_label = CTkLabel(self.left_chats_bar, text="Appearance Mode:")
        self.theme_mode_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.theme_mode_options = CTkOptionMenu(self.left_chats_bar,
                                                values=["Light", "Dark", "System"],
                                                command=change_theme_mode)
        self.theme_mode_options.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="s")

        # Create input and send button:
        self.input = CTkTextbox(self.class_container, height=60)
        self.input.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.input.bind("<FocusIn>", lambda _: self.on_input_focus_in)
        self.input.bind("<FocusOut>", lambda _: self.on_input_focus_out)

        self.send_button = CTkButton(master=self.class_container,
                                     fg_color="transparent",
                                     border_width=2,
                                     text_color=("gray10", "#DCE4EE"),
                                     text="Send",
                                     command=self.on_send_button_click)
        self.send_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.bind("<Return>", lambda event: self.controller.enter_clicked(event, "TextModels"))

        # Create chat space frame
        self.center_frame = CTkFrame(self.class_container)
        self.center_frame.grid(row=0, column=1, rowspan=3, columnspan=2, pady=(20, 0), sticky="nsew")

        self.selected_model_label = CTkLabel(self.center_frame,
                                             text="Selected Model:",
                                             anchor="center")
        self.selected_model_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky='ne')

        self.selected_model_options = CTkOptionMenu(self.center_frame,
                                                    values=["gpt-3.5-turbo",
                                                            "gpt-3.5-turbo-16k",
                                                            "gpt-4",
                                                            "gpt-4-0314",
                                                            "gpt-4-0613"],
                                                    command=self.change_model_event)
        self.selected_model_options.grid(row=0, column=1, padx=20, pady=(10, 10), sticky='nw')

        self.chat_space_frame = CTkScrollableFrame(self.center_frame)
        self.chat_space_frame.grid(row=1, rowspan=2, column=0, columnspan=3, sticky="nsew")

        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_columnconfigure(2, weight=1)

        # Create options frame:
        self.options_frame = CTkFrame(self.class_container)
        self.options_frame.grid(row=0, rowspan=3, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # Menu button:
        self.menu_button = CTkButton(self.options_frame,
                                     text="Go back to the Menu",
                                     font=("New Times Roman", 16),
                                     command=self.on_menu_button_click)
        self.menu_button.grid(row=0, column=0, columnspan=3, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # Max tokens and temperature:
        self.max_tokens_label = CTkLabel(self.options_frame,
                                         text="Max Tokens:",
                                         anchor="center")
        self.max_tokens_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky='ne')

        self.max_tokens_entry = CTkEntry(self.options_frame)
        self.max_tokens_entry.grid(row=1, column=1, padx=5, pady=10, sticky='nw')
        self.temperature_label = CTkLabel(self.options_frame, text="Temperature:", anchor="center")
        self.temperature_label.grid(row=2, column=0, padx=(10, 5), pady=10, sticky='ne')
        self.temperature_sidebar = CTkSlider(self.options_frame, from_=0, to=2)
        self.temperature_sidebar.grid(row=2, column=1, padx=5, pady=10, sticky='nw')
        self.temperature_value_label = CTkLabel(self.options_frame, text=str(self.temperature_pref), anchor="center")
        self.temperature_value_label.grid(row=2, column=2, padx=(10, 5), pady=10, sticky='nw')
        self.temperature_sidebar.bind("<B1-Motion>", lambda _: self.temperature_sidebar_event)

        # Roles:
        self.role_label = CTkLabel(self.options_frame, text="Roles:", anchor="center")
        self.role_label.grid(row=3, column=0, padx=5, pady=(10, 10), sticky='ne')
        self.role_textbox = CTkTextbox(self.options_frame)
        self.role_textbox.grid(row=3, column=0, columnspan=3, padx=5, pady=(10, 10), sticky='nsew')
        self.remember_previous_messages = CTkCheckBox(self.options_frame, text="Remember previous messages")
        self.remember_previous_messages.bind("<Button-1>", lambda _: self.on_remember_previous_messages_click)
        self.remember_previous_messages.grid(row=4, column=0, columnspan=3, padx=5, pady=(10, 10), sticky='nsew')
        self.debug_button = CTkButton(self.options_frame, text="Debug", command=self.debug)
        self.debug_button.grid(row=5, column=0, columnspan=3, padx=5, pady=(10, 10), sticky='nsew')

        # Set default values and configure:
        self.new_chat_button.configure(text="New Chat")
        self.theme_mode_options.set(self.theme_mode_pref)
        self.temperature_sidebar.set(self.temperature_pref)
        self.selected_model_options.set(self.model_pref)
        self.max_tokens_entry.insert(0, self.max_tokens_pref)
        if self.remember_previous_messages_pref:
            self.remember_previous_messages.select()
        if self.full_screened_pref:
            self.after(1, self.make_window_fullscreen)
        self.input.after(100, self.input.focus_set)
        self.chat_id = None
        self.currently_new_messages_count = 0     # 1 because, 0 is invisible textbox
        self.is_scrolled_up = False
        self.max_chats = 30

        # Bind events:
        self.controller.bind("<Configure>", self.make_window_responsive)
        self.chat_history_frame.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_in_chat_history(event))

        # Load previous chat to chat history:
        self.initialize_loading_chat_buttons()
        self.chat_space_frame_clear()

    def debug(self):
        pass
        # Debug, check models:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        model_list = openai.Model.list()
        for model in model_list.data:
            print(model.id)

    @staticmethod
    def frame_highlight_on_hover(button_frame):
        button_frame.configure(fg_color="#2F2F2F")

    @staticmethod
    def frame_clear_highlight(button_frame):
        button_frame.configure(fg_color="transparent")

    def add_newest_chat_button(self, prompt):
        title = self.return_title(prompt)
        self.first_button_row -= 1
        self.print_new_chat_button(title, self.first_button_row)

    def load_older_chats_buttons(self):
        latest_button_row = self.last_button_row - self.new_buttons_limit
        if latest_button_row >= len(self.sorted_chat_list):
            return

        with open("chats/" + self.sorted_chat_list[latest_button_row], "r") as chat_file:
            chat_data = json.load(chat_file)
            button_name = chat_data["parameters"]["chat_title"]

        self.print_new_chat_button(button_name, self.last_button_row)
        self.last_button_row += 1

    def print_new_chat_button(self, button_name, button_row):
        button_frame = CTkFrame(self.chat_history_frame, fg_color="transparent")
        button_frame.grid(row=button_row, column=0, pady=1, sticky="we")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)

        button_chat = CTkButton(button_frame,
                                text=button_name,
                                font=("New Times Roma", 12),
                                fg_color="transparent",
                                anchor="w",
                                hover=False,
                                cursor="hand2",
                                border_spacing=0,
                                border_width=0)
        button_chat.grid(row=0, column=0, padx=(8, 0), sticky="w")
        button_in_list_index = button_row - self.new_buttons_limit
        button_chat.bind("<Button-1>",
                         lambda _, br=button_in_list_index, bf=button_frame:
                         self.load_other_chat_config_and_chat_story(br, bf))
        button_chat.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_in_chat_history(event))
        button_chat.bind("<Enter>", lambda _, bf=button_frame: self.frame_highlight_on_hover(bf))
        button_chat.bind("<Leave>", lambda _, bf=button_frame: self.frame_clear_highlight(bf))

    def initialize_loading_chat_buttons(self):
        if os.path.exists("chats"):
            chats_list = os.listdir("chats")
            self.sorted_chat_list = sorted(chats_list,
                                           key=lambda x: os.path.getmtime(os.path.join("chats", x)),
                                           reverse=True)

            self.button_row = 0
            self.new_buttons_limit = 50    # limit for new chats in one session
            while len(self.sorted_chat_list) > self.button_row < self.max_chats:
                with open("chats/" + self.sorted_chat_list[self.button_row], "r") as chat_file:
                    chat_data = json.load(chat_file)
                    button_name = chat_data["parameters"]["chat_title"]
                self.print_new_chat_button(button_name, self.button_row + self.new_buttons_limit)
                self.button_row += 1
            self.first_button_row = self.new_buttons_limit
            self.last_button_row = self.button_row + self.new_buttons_limit

    def load_other_chat_config_and_chat_story(self, button_row, button_frame):
        self.chat_space_frame_clear()
        self.messages.clear()
        if self.current_button_frame_selected is not None:
            self.button_clear_highlight(self.current_button_frame_selected)
            self.delete_add_and_delete_from_button(self.current_button_frame_selected)
        self.current_button_frame_selected = button_frame
        self.button_highlight_on_click(button_frame)
        self.add_edit_and_delete_to_button(button_frame)
        self.currently_new_messages_count = 0
        self.current_chat_row = button_row

        with open("chats/" + self.sorted_chat_list[button_row], "r") as chat_file:
            chat_data = json.load(chat_file)

            # Load chat previous data:
            self.chat_id = chat_data["parameters"]["chat_id"]
            self.number_of_all_messages = chat_data["parameters"]["messages_counter"]
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
            self.currently_loaded_messages = 0
            i = self.number_of_all_messages // 2 - 1
            while self.number_of_all_messages > self.currently_loaded_messages < 10:
                message = chat_data["messages"][i]
                calculated_height_of_input = self.calculate_height_of_message(message["input"]["height"],
                                                                              message["input"]["width"])
                calculated_height_of_answer = self.calculate_height_of_message(message["answer"]["height"],
                                                                               message["input"]["width"])
                self.write_new_message(message["answer"]["content"], "ai", calculated_height_of_answer, False)
                self.write_new_message(message["input"]["content"], "user", calculated_height_of_input, False)
                i -= 1
            self.move_scrollbar_to_bottom()

    def calculate_height_of_message(self, height, width):
        self.chat_space_empty_textbox.update_idletasks()
        width_of_current_window = self.chat_space_empty_textbox.winfo_width()
        width_radio = width / width_of_current_window
        height_of_message = int(height * width_radio)
        return height_of_message

    @staticmethod
    def change_height_of_message_in_real_time(message):
        h = message.winfo_height()
        while message._textbox.yview() != (0.0, 1.0):
            h += 10
            message.configure(height=h)

    def make_window_responsive(self, _):
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
        textbox.configure(padx=10)
        self.highlight_code(textbox)

    def add_icon_to_message(self, role, row):
        dark_image_path = ""
        if role == "user":
            dark_image_path = "img/user_icon_64.png"
        elif role == "ai":
            dark_image_path = "img/ai_icon_64.png"

        dark_image = Image.open(self.controller.resource_path(dark_image_path))
        image = CTkImage(dark_image=dark_image, size=(32, 32))
        icon_in_app = CTkLabel(self.chat_space_frame, image=image, text="")
        icon_in_app.grid(row=row, column=0, padx=(0, 5), pady=(20, 0), sticky="ne")

    def write_new_message(self, message, role, height_of_message=35, is_new_message=True):
        if is_new_message:
            row = self.number_of_all_messages + self.currently_new_messages_count
            self.currently_new_messages_count += 1
        else:
            row = self.number_of_all_messages - self.currently_loaded_messages
            self.currently_loaded_messages += 1
        self.add_icon_to_message(role, row)
        new_message = CTkTextbox(self.chat_space_frame,
                                 font=("New Times Roman", 15),
                                 wrap="word",
                                 height=height_of_message,
                                 activate_scrollbars=False)
        new_message.grid(row=row, column=1, pady=(20, 0), sticky="new")
        self.chat_space_frame.grid_columnconfigure(1, weight=10)
        new_message.insert(tk.END, message)
        self.change_style_of_message(new_message)
        new_message.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_up_in_textbox(event))
        self.messages.append(new_message)
        new_message.configure(state="disabled")

    def api_request(self, prompt):
        # Get values:
        model = self.selected_model_options.get()
        max_tokens = int(self.max_tokens_entry.get())
        temperature = float(self.temperature_value_label.cget("text"))

        # Clear input:
        self.write_new_message(prompt, "user")
        self.input.delete("1.0", tkinter.END)
        self.change_style_of_message(self.messages[-1])

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

        # Expand input textbox:
        self.change_height_of_message_in_real_time(self.messages[-1])
        title = ""
        if self.chat_id is None:
            title = self.return_title(prompt)

        # Get response into chat space:
        complete_message = ""
        self.write_new_message("", "ai")
        self.messages[-1].configure(state="normal")
        self.messages[-1].unbind("<Configure>")
        for chunk in chat_completion:
            if chunk and chunk['choices'][0]['delta'] != {}:
                chunk_message = chunk['choices'][0]['delta']['content']
                complete_message += chunk_message

                self.messages[-1].insert(tk.END, chunk_message, "all_space_of_chat")
                self.change_height_of_message_in_real_time(self.messages[-1])
                self.move_scrollbar_to_bottom()

        self.highlight_code(self.messages[-1])
        self.messages[-1].configure(state="disable")

        height_of_input = self.messages[-2].winfo_height()
        self.increase_height_of_textbox(self.messages[-2], height_of_input)
        height_of_response = self.messages[-1].winfo_height()
        self.increase_height_of_textbox(self.messages[-1], height_of_response)

        self.save_chat_to_file(prompt, complete_message, height_of_response, height_of_input, title)

    @staticmethod
    def increase_height_of_textbox(textbox, height):
        if height < 40:
            return
        elif height < 100:
            height += 20
        else:
            height += 50
        textbox.configure(height=height)

    def save_chat_to_file(self, prompt, response, height_of_response, height_of_input, title):
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
                        "chat_title": title,
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

            self.add_newest_chat_button(prompt)

        with open(f"chats/chat_{self.chat_id}.json", "r+") as chat_file:
            chat_file_data = json.load(chat_file)
            message = {
                "input": {
                    "content": prompt,
                    "height": height_of_input + int(height_of_input * 0.1),
                    "width": self.chat_space_empty_textbox.winfo_width(),
                },
                "answer": {
                    "content": response,
                    "height": height_of_response + int(height_of_response * 0.1),
                    "width": self.chat_space_empty_textbox.winfo_width(),
                },
            }
            chat_file_data["messages"].append(message)
            chat_file_data["parameters"]["messages_counter"] += 2

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
                        messages.append({"role": "assistant", "content": chat_data["messages"][i]["answer"]["content"]})
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
            if self.chat_space_frame._scrollbar._start_value <= 0.025:
                self.load_more_chats_messages()
        elif self.chat_space_frame._scrollbar._end_value >= 0.975:
            self.is_scrolled_up = False

    def move_scrollbar_to_bottom(self):
        if self.is_scrolled_up:
            return
        self.chat_space_frame._scrollbar._command("moveto", 1.0)

    def on_mouse_scroll_up_in_textbox(self, event):
        if event.delta > 0:
            self.is_scrolled_up = True
            if self.chat_space_frame._scrollbar._start_value <= 0.025:
                self.load_more_chats_messages()

    def load_more_chats_messages(self):
        if self.current_chat_row is None:
            return
        with open("chats/" + self.sorted_chat_list[self.current_chat_row], "r") as chat_file:
            chat_data = json.load(chat_file)

            # Actually message:
            i = (self.number_of_all_messages - self.currently_loaded_messages) // 2 - 1
            j = 0
            while 0 <= i <= self.number_of_all_messages and j < 2:
                message = chat_data["messages"][i]
                calculated_height_of_input = self.calculate_height_of_message(message["input"]["height"],
                                                                              message["input"]["width"])
                calculated_height_of_answer = self.calculate_height_of_message(message["answer"]["height"],
                                                                               message["input"]["width"])
                self.write_new_message(message["answer"]["content"], "ai", calculated_height_of_answer, False)
                self.write_new_message(message["input"]["content"], "user", calculated_height_of_input, False)
                i -= 1
                j += 1

    @staticmethod
    def set_image_for_button(button, image_path, size=(18, 18)):
        image_open = Image.open(image_path)
        image = CTkImage(image_open, size=size)
        button.configure(image=image)

    @staticmethod
    def button_highlight_on_click(button_frame):
        button_frame.configure(fg_color="#3F3F3F")
        buttons = list(button_frame.children.keys())
        button_chat = buttons[1]
        button_frame.children[button_chat].unbind("<Enter>")
        button_frame.children[button_chat].unbind("<Leave>")

    def button_clear_highlight(self, button_frame):
        button_frame.configure(fg_color="#2B2B2B")
        buttons = list(button_frame.children.keys())
        button_chat = buttons[1]
        button_frame.children[button_chat].bind("<Enter>", lambda _, bf=button_frame: self.frame_highlight_on_hover(bf))
        button_frame.children[button_chat].bind("<Leave>", lambda _, bf=button_frame: self.frame_clear_highlight(bf))

    def add_edit_and_delete_to_button(self, button_frame):
        edit_icon_path = self.controller.resource_path("img/edit_icon.png")
        edit_icon_on_hover_path = self.controller.resource_path("img/edit_icon_on_hover.png")
        edit_icon_opened = Image.open(edit_icon_path)
        edit_icon = CTkImage(edit_icon_opened, size=(18, 18))
        button_edit = CTkButton(button_frame,
                                fg_color="transparent",
                                hover=False,
                                image=edit_icon,
                                text="",
                                width=18,
                                height=18,
                                cursor="hand2")
        button_edit.grid(row=0, column=1, sticky="e")
        button_edit.bind("<Enter>",
                         lambda _, button=button_edit: self.set_image_for_button(button, edit_icon_on_hover_path))
        button_edit.bind("<Leave>",
                         lambda _, button=button_edit: self.set_image_for_button(button, edit_icon_path))

        delete_icon_on_hover_path = self.controller.resource_path("img/delete_icon_on_hover.png")
        delete_icon_path = self.controller.resource_path("img/delete_icon.png")
        delete_icon_opened = Image.open(delete_icon_path)
        delete_icon = CTkImage(delete_icon_opened, size=(18, 18))
        button_delete = CTkButton(button_frame,
                                  fg_color="transparent",
                                  hover=False,
                                  image=delete_icon,
                                  text="",
                                  width=18,
                                  height=18,
                                  cursor="hand2")
        button_delete.grid(row=0, column=2, sticky="e")
        button_delete.bind("<Enter>",
                           lambda _, button=button_delete: self.set_image_for_button(button, delete_icon_on_hover_path))
        button_delete.bind("<Leave>",
                           lambda _, button=button_delete: self.set_image_for_button(button, delete_icon_path))

    @staticmethod
    def delete_add_and_delete_from_button(button_frame):
        buttons = button_frame.children.keys()
        buttons = list(buttons)
        button_frame.children[buttons[2]].destroy()
        button_frame.children[buttons[3]].destroy()

    def on_mouse_scroll_in_chat_history(self, event):
        if event.delta < 0 and self.chat_history_frame._scrollbar._end_value >= 0.975:
            self.load_older_chats_buttons()

    def check_correct_input(self):
        # Check if input is empty:
        prompt = self.input.get("1.0", tkinter.END)
        if prompt == "Send a message\n" or not prompt.strip():
            return
        self.api_request(prompt.strip())

    @staticmethod
    def return_title(prompt):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        message = []
        role = ("""A text will be provided to you. Based on this text, return a short title. Maximum 40 characters.
                    Return it in the format without anything else, just pure text.
                    If you encounter an error return 'New chat'""")
        message.append({"role": "system", "content": role})
        message.append({"role": "user", "content": prompt})
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.6,
            max_tokens=2000,
            stream=False,
            messages=message
        )

        title = chat_completion["choices"][0].message["content"]
        return title

    def new_chat_click(self):
        print("Debug: New chat clicked")
        self.chat_id = None
        self.messages.clear()
        self.currently_new_messages_count = 0
        self.number_of_all_messages = 0
        self.role_textbox.configure(state="normal")
        self.chat_space_frame_clear()
        if self.current_button_frame_selected is not None:
            self.button_clear_highlight(self.current_button_frame_selected)
            self.delete_add_and_delete_from_button(self.current_button_frame_selected)
        self.current_button_frame_selected = None

    def chat_space_frame_clear(self):
        self.chat_space_frame._scrollbar.grid_forget()
        self.chat_space_frame.destroy()
        self.chat_space_frame = CTkScrollableFrame(self.center_frame)
        self.chat_space_frame.grid(row=1, rowspan=2, column=0, columnspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.chat_space_frame.grid_columnconfigure(1, weight=10)
        self.chat_space_frame.bind("<MouseWheel>", lambda event: self.on_mouse_scroll_up(event))
        self.chat_space_empty_textbox = CTkTextbox(self.chat_space_frame, height=1, fg_color="transparent")
        self.chat_space_empty_textbox.grid(row=0, column=1, sticky="nsew")
        self.chat_space_empty_textbox.configure(state="disabled")

    def on_remember_previous_messages_click(self):
        with (open("config.json", "r+") as config_file):
            config_data = json.load(config_file)
            is_checked = self.remember_previous_messages.get()
            self.remember_previous_messages_pref = is_checked
            config_data["text_models"]["user_preferences"]["remember_previous_messages"] = is_checked
            write_data_to_json_file(config_data, "config.json")

    def on_input_focus_in(self):
        if self.input.get("1.0", tk.END) == "Send a message\n":
            self.input.delete("1.0", tk.END)

    def on_input_focus_out(self):
        if self.input.get("1.0", tk.END) == "\n":
            self.input.insert("1.0", "Send a message")

    def temperature_sidebar_event(self):
        formatted_value = format(self.temperature_sidebar.get(), '.2f')
        self.temperature_value_label.configure(text=str(formatted_value))

    def change_model_event(self, new_model: str):
        pass

    def count_tokens_for_text(self, text):
        try:
            encoding = tiktoken.encoding_for_model(self.selected_model_options.get())
            return len(encoding.encode(text))
        except ValueError:
            return 0

    def make_window_fullscreen(self):
        self.controller.state('zoomed')

    def on_menu_button_click(self):
        self.controller.show_frame("Menu")
        self.controller.change_geometry(400, 400)
        self.controller.change_min_size(400, 400)
        self.controller.is_resizable(False)

    def on_send_button_click(self):
        threading.Thread(target=self.check_correct_input).start()
