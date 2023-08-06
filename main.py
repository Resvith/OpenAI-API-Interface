import tkinter as tk
import os
import openai
import tkinter.messagebox
import customtkinter
import threading
import json
import datetime
import tiktoken

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Create config file if no exists:
        if not (os.path.exists("config.json")):
            self.create_default_config()
            print("Debug, config file created.")

        # Load config file:
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)
            self.chat_count = config_data["chats_counter"]
            self.model_pref = config_data["user_preferences"]["model"]
            self.max_tokens_pref = config_data["user_preferences"]["max_tokens"]
            self.temperature_pref = config_data["user_preferences"]["temperature"]
            self.theme_mode_pref = config_data["user_preferences"]["theme"]
            self.window_width_pref = config_data["user_preferences"]["window_width"]
            self.window_height_pref = config_data["user_preferences"]["window_height"]
            self.fullscreened_pref = config_data["user_preferences"]["full-screened"]

        # Configure window:
        self.title("OpenAI API Interface")
        self.minsize(1100, 580)
        self.geometry(f"{self.window_width_pref}x{self.window_height_pref}")
        self.state("normal")

        # Configure grid layout (4x4):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Create chat history frame:
        self.chat_history_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.chat_history_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.chat_history_frame.grid_rowconfigure(4, weight=1)
        self.new_chat_button = customtkinter.CTkButton(self.chat_history_frame, command=self.new_chat_click)
        self.new_chat_button.grid(row=1, column=0)
        self.theme_mode_label = customtkinter.CTkLabel(self.chat_history_frame, text="Appearance Mode:", anchor="w")
        self.theme_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.theme_mode_options = customtkinter.CTkOptionMenu(self.chat_history_frame, values=["Light", "Dark", "System"],
                                                              command=self.change_theme_mode)
        self.theme_mode_options.grid(row=6, column=0, padx=20, pady=(10, 10))

        # Create input and send button:
        self.input = customtkinter.CTkTextbox(self, height=60)
        self.input.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.input.bind("<FocusIn>", self.on_input_focus_in)
        self.input.bind("<FocusOut>", self.on_input_focus_out)
        self.send_button = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Send", command=self.on_send_button_click)
        self.bind("<Return>", lambda event: self.enter_clicked(event))
        self.send_button.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Create chat space frame
        self.chat_space_frame = customtkinter.CTkFrame(self)
        self.chat_space_frame.grid(row=0, column=1, rowspan=3, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.selected_model_label = customtkinter.CTkLabel(self.chat_space_frame, text="Selected Model:", anchor="center")
        self.selected_model_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky='ne')
        self.selected_model_options = customtkinter.CTkOptionMenu(self.chat_space_frame, values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"], command=self.change_model_event)
        self.selected_model_options.grid(row=0, column=1, padx=20, pady=(10, 10), sticky='nw')
        self.chat_space = customtkinter.CTkTextbox(self.chat_space_frame, wrap="word")
        self.chat_space.grid(row=1, rowspan=2, column=0, columnspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.chat_space_frame.grid_rowconfigure(1, weight=1)
        self.chat_space_frame.grid_columnconfigure(2, weight=1)

        # Create options frame:
        self.options_frame = customtkinter.CTkFrame(self)
        self.options_frame.grid(row=0, rowspan=3, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # Max tokens and temperature:
        self.max_tokens_label = customtkinter.CTkLabel(self.options_frame, text="Max Tokens:", anchor="center")
        self.max_tokens_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky='ne')
        self.max_tokens_entry = customtkinter.CTkEntry(self.options_frame)
        self.max_tokens_entry.grid(row=0, column=1, padx=5, pady=10, sticky='nw')
        self.temperature_label = customtkinter.CTkLabel(self.options_frame, text="Temperature:", anchor="center")
        self.temperature_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky='ne')
        self.temperature_sidebar = customtkinter.CTkSlider(self.options_frame, from_=0, to=2)
        self.temperature_sidebar.grid(row=1, column=1, padx=5, pady=10, sticky='nw')
        self.temperature_value_label = customtkinter.CTkLabel(self.options_frame, text=str(self.temperature_pref), anchor="center")
        self.temperature_value_label.grid(row=1, column=2, padx=(10, 5), pady=10, sticky='nw')
        self.temperature_sidebar.bind("<B1-Motion>", self.temperature_sidebar_event)

        # Roles:
        self.role_label = customtkinter.CTkLabel(self.options_frame, text="Roles:", anchor="center")
        self.role_label.grid(row=2, column=0, padx=5, pady=(10, 10), sticky='ne')
        self.role_enabled = customtkinter.CTkCheckBox(self.options_frame, text="Enabled")
        self.role_enabled.grid(row=2, column=1, padx=5, pady=(10, 10), sticky='nw')
        self.role_textbox = customtkinter.CTkTextbox(self.options_frame)
        self.role_textbox.grid(row=3, column=0, columnspan=3, padx=5, pady=(10, 10), sticky='nsew')

        # Set default values and configure:
        self.new_chat_button.configure(text="New Chat")
        self.theme_mode_options.set(self.theme_mode_pref)
        self.chat_space.configure(state="disabled")
        self.temperature_sidebar.set(self.temperature_pref)
        self.selected_model_options.set(self.model_pref)
        self.max_tokens_entry.insert(0, self.max_tokens_pref)
        if self.fullscreened_pref:
            self.after(1, self.make_window_fullscreen)
        self.input.after(25, self.input.focus_set)
        self.chat_id = None

    def api_request(self, prompt):
        # Get values:
        model = self.selected_model_options.get()
        max_tokens = int(self.max_tokens_entry.get())
        temperature = float(self.temperature_value_label.cget("text"))
        role = self.role_textbox.get("1.0", tkinter.END)

        # Clear input:
        self.chat_space.configure(state="normal")
        self.chat_space.insert(tk.END, prompt)
        self.input.delete("1.0", tkinter.END)

        tokens_counter = 0
        messages = []
        # Load previous messages to request if chat_id exists:
        if self.chat_id:
            tokens_limit = 1000
            with open(f"chat_{self.chat_id}.json", "r+") as chat_file:
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

                messages.append({"role": "user", "content": prompt})
                tokens_counter += self.count_tokens_for_text(prompt)
                chat_data["parameters"]["tokens_counter"] += tokens_counter
                self.write_data_to_json_file(chat_data, f"chat_{self.chat_id}.json")
                print("Debug, sum of tokens:", tokens_counter)

        else:   # If the conversation hasn't started yet:
            messages.append({"role": "system", "content": role})
            messages.append({"role": "user", "content": prompt})

        # Execute prompt:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        chat_completion = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            messages=messages
        )

        # Debug, check models:
        # model_list = openai.Model.list()
        # for model in model_list.data:
        #     print(model.id)

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
            self.chat_id = self.chat_count

            with open("config.json", "r+") as config_file:
                config_parameters = json.load(config_file)
                config_parameters["chats_counter"] += 1
                self.write_data_to_json_file(config_parameters, "config.json")

            with open(f"chat_{self.chat_id}.json", "a") as chat_file:
                chat_file_data = {
                    "parameters": {
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

        with open(f"chat_{self.chat_id}.json", "r+") as chat_file:
            chat_file_data = json.load(chat_file)
            message = {
                "content": prompt,
                "answer": response
            }
            chat_file_data["messages"].append(message)
            chat_file_data["parameters"]["messages_counter"] += 1

            # Count tokens:
            tokens_consumed = self.count_tokens_for_text(prompt + response)
            chat_file_data["parameters"]["tokens_counter"] += tokens_consumed

            self.write_data_to_json_file(chat_file_data, f"chat_{self.chat_id}.json")

    def count_tokens_for_text(self, text):
        encoding = tiktoken.encoding_for_model(self.selected_model_options.get())
        return len(encoding.encode(text))

    def create_default_config(self):
        default_config_data = {
            "chats_counter": 1,
            "user_preferences": {
                "model": "gpt-3.5-turbo",
                "max_tokens": 1000,
                "temperature": 1.0,
                "theme": "dark",
                "window_width": 1400,
                "window_height": 800,
                "full-screened": False
            }
        }

        with open("config.json", "w") as json_file:
            json.dump(default_config_data, json_file)

    def write_data_to_json_file(self, data, file_path):
        with open(file_path, "w") as file:
            json.dump(data, file)

    def make_window_fullscreen(self):
        self.state('zoomed')

    def enter_clicked(self, event):
        if not (event.state & 0x1):  # Check if Shift key is not pressed
            threading.Thread(target=self.check_correct_input).start()

    def on_send_button_click(self):
        threading.Thread(target=self.check_correct_input).start()

    def check_correct_input(self):
        # Check if input is empty:
        prompt = self.input.get("1.0", tkinter.END)
        if prompt == "Send a message\n" or not prompt.strip():
            return
        self.api_request(prompt)

    def write_message_to_file(self, ):
        pass

    def on_input_focus_in(self, event):
        if self.input.get("1.0", tk.END) == "Send a message\n":
            self.input.delete("1.0", tk.END)

    def on_input_focus_out(self, event):
        if self.input.get("1.0", tk.END) == "\n":
            self.input.insert("1.0", "Send a message")

    def temperature_sidebar_event(self, event):
        formatted_value = format(self.temperature_sidebar.get(), '.2f')
        self.temperature_value_label.configure(text=str(formatted_value))

    def change_temperature_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def change_model_event(self, new_model: str):
        pass

    def change_theme_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def new_chat_click(self):
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
