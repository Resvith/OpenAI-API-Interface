import openai
import os
import tkinter as tk
from tkinter import ttk


MAX_TOKENS = 1000
ROLE = 'Assistant'
MODEL = 'gpt-3.5-turbo'
TEMPERATURE = 0.5


class ChatHistory(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Button(self, text='New Chat', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        tk.Button(self, text='Chat 2', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top', pady=(30, 0))
        tk.Button(self, text='Chat 3', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        tk.Button(self, text='Chat 4', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        tk.Button(self, text='Chat 5', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        tk.Button(self, text='Chat 6', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        tk.Button(self, text='Chat 7', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        tk.Button(self, text='Chat 8', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        tk.Button(self, text='Chat 9', font=('Arial', 16), background='#F5F5F5', padx=10, pady=10).pack(fill='both', side='top')
        self.pack(fill='both', side='left')


class ChatSpace(ttk.Frame):

    # Debug, remove later, THIS IS FINE:
    def on_combobox_change(self, event):
        global MODEL
        MODEL = self.model.get()

    def __init__(self, parent):
        super().__init__(parent)
        chat_label_frame = ttk.Frame(self)

        # Selected Model:
        selected_model_label = tk.Label(chat_label_frame, background='#F5F5F5', font=('Arial', 16), text='Selected Model:')
        selected_model_label.pack(fill='both', side='left', padx=30, pady=30)
        options = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"]
        self.model = ttk.Combobox(chat_label_frame, values=options)
        self.model.set(options[0])
        self.model.pack(fill='both', side='left', padx=30, pady=30)
        self.model.bind("<<ComboboxSelected>>", self.on_combobox_change)
        chat_label_frame.pack(fill='both', side='top')

        # Chat space:
        chat_space_frame = ttk.Frame(self)
        self.chat_space = tk.Message(chat_space_frame, background='#F5F5F5', font=('Arial', 16), text='Hello World',
                                anchor=tk.NW)
        self.chat_space.pack(expand=True, fill='both', side='top', padx=30, pady=30)
        chat_space_frame.pack(fill='both', side='top')

        # Pack Chat Space:
        self.pack(fill='both', side='top', expand=True)


class OptionsBar(ttk.Frame):
    def on_max_tokens_changed(self, event):
        global MAX_TOKENS
        MAX_TOKENS = int(self.max_tokens_textbox.get('1.0', tk.END))

    def on_temperature_change(self, value):
        rounded_value = round(float(value), 2)
        self.temperature_value['text'] = str(format(rounded_value, '.2f'))
        global TEMPERATURE
        TEMPERATURE = rounded_value

    def __init__(self, parent):
        super().__init__(parent)

        # Temperature:
        temperature_frame = ttk.Frame(self)
        temperature_label = ttk.Label(temperature_frame, text='Temperature: ')
        temperature_label.pack(side='left', padx=10, pady=10)
        temperature_slider = ttk.Scale(temperature_frame, from_=0, to=2.0, value=0.5, orient=tk.HORIZONTAL, command=self.on_temperature_change)
        temperature_slider.pack(fill='both', side='left', padx=10, pady=10)
        self.temperature_value = (tk.Label(temperature_frame, text='0.50'))
        self.temperature_value.pack(side='left', padx=10, pady=10)
        temperature_frame.pack(fill='both', side='top')

        # Max Tokens:
        max_tokens_frame = ttk.Frame(self)
        max_tokens_label = ttk.Label(max_tokens_frame, text='Max Tokens:')
        max_tokens_label.pack(side='left', padx=10, pady=10)
        self.max_tokens_textbox = tk.Text(max_tokens_frame, height=1, width=7, font=('Arial', 16), background='#F5F5F5', padx=10, pady=10, relief=tk.FLAT, borderwidth=1, highlightthickness=1)
        self.max_tokens_textbox.insert(tk.END, str(MAX_TOKENS))
        self.max_tokens_textbox.pack(side='left', padx=10, pady=10)
        self.max_tokens_textbox.bind('<KeyRelease>', self.on_max_tokens_changed)
        max_tokens_frame.pack(side='top')

        # Role:
        role_label = ttk.Label(self, text='Role:', font=('Arial', 16))
        role_label.pack(side='top', padx=10)

        role_textbox = tk.Text(self, height=5, width=20, font=('Arial', 16), background='#F5F5F5', padx=10, pady=10, relief=tk.FLAT, borderwidth=2, highlightthickness=2)
        role_textbox.insert(tk.END, str(ROLE))
        role_textbox.pack(side='top', padx=10, pady=10)

        # Role Binds:
        role_binds_row_1_frame = ttk.Frame(self)
        button_1 = tk.Button(role_binds_row_1_frame, font=('Arial', 16), background='red', padx=5, pady=5)
        button_1.pack(side='left', padx=10, pady=10)
        button_2 = tk.Button(role_binds_row_1_frame, font=('Arial', 16), background='red', padx=5, pady=5)
        button_2.pack(side='left', padx=10, pady=10)
        button_3 = tk.Button(role_binds_row_1_frame, font=('Arial', 16), background='red', padx=5, pady=5)
        button_3.pack(side='left', padx=10, pady=10)
        role_binds_row_1_frame.pack(side='top')

        role_binds_row_2_frame = ttk.Frame(self)
        button_4 = tk.Button(role_binds_row_2_frame, font=('Arial', 16), background='red', padx=5, pady=5)
        button_4.pack(side='left', padx=10, pady=10)
        button_5 = tk.Button(role_binds_row_2_frame, font=('Arial', 16), background='red', padx=5, pady=5)
        button_5.pack(side='left', padx=10, pady=10)
        button_6 = tk.Button(role_binds_row_2_frame, font=('Arial', 16), background='red', padx=5, pady=5)
        button_6.pack(side='left', padx=10, pady=10)
        role_binds_row_2_frame.pack(side='top')

        # Pack OptionsBar
        self.pack(fill='y', side='right')


class Input(ttk.Frame):
    def submit_prompt(self):
        prompt = (self.textbox.get('1.0', tk.END))
        openai.api_key = os.getenv("OPENAI_API_KEY")
        completion = openai.ChatCompletion.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {"role": "system", "content": ROLE},
                {"role": "user", "content": prompt}
            ]
        )

        response_message = completion.choices[0].message
        response_content = response_message["content"]


    def __init__(self, parent):
        super().__init__(parent)
        input_frame = ttk.Frame(self)
        self.textbox = tk.Text(input_frame, background='#F5F5F5', font=('Arial', 16), height=3)
        self.textbox.pack(fill='both', side='left', padx=30, pady=30)
        submit = tk.Button(input_frame, text='Send', font=('Arial', 16), background='Green', padx=10, pady=10, command=self.submit_prompt)
        submit.pack(fill='both', side='right', padx=20, pady=30)
        input_frame.pack(fill='both', side='left')

        # Pack Input
        self.pack(fill='both', side='bottom')


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('OpenAI API Interface')
        self.geometry('1600x800')

        # ChatsBar
        self.chats_bar = ChatHistory(self)

        # OptionsBar
        self.options_bar = OptionsBar(self)

        # Input
        self.input = Input(self)

        # ChatSpace
        self.chat_space = ChatSpace(self)

        # run
        self.mainloop()


if __name__ == "__main__":
    App()


class GUI:
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("1400x800")
        self.root.title("OpenAI API Interface")

        self.frame = tk.Frame( self.root)
        self.frame.grid()
        self.frame.columnconfigure(0, weight=10)
        self.frame.columnconfigure(1, weight=15)
        self.frame.columnconfigure(2, weight=5)
        self.frame.columnconfigure(3, weight=5)
        self.frame.columnconfigure(4, weight=5)

        self.role_label = tk.Label(self.frame, text="Role:")
        self.role_label.grid(row=0, column=0)

        self.role = tk.Text(self.frame)
        self.role.grid(row=1, column=0, sticky="ew", padx=10)

        self.prompt_label = tk.Label(self.frame, text="Prompt:")
        self.prompt_label.grid(row=0, column=1, columnspan=3, sticky="ew")

        self.prompt = tk.Text(self.frame)
        self.prompt.grid(row=1, column=1, columnspan=3, sticky="ew", padx=10)

        self.output_label = tk.Label(self.frame, text="Output:")
        self.output_label.grid(row=2, column=0, sticky="ew")

        self.output = tk.Text(self.frame)
        self.output.grid(row=3, rowspan=5, column=0, columnspan=2, sticky="ew", padx=10)

        self.label_model = tk.Label(self.frame, text="Model")
        self.label_model.grid(row=3, column=2, sticky="ew", padx=10, pady=10)

        self.options = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"]
        self.model = ttk.Combobox(self.frame, values=self.options)
        self.model.set(self.options[0])
        self.model.grid(row=3, column=3, sticky="ew", padx=10, pady=10)

        self.temperature_label = tk.Label(self.frame, text="Temperature")
        self.temperature_label.grid(row=4, column=2, sticky="ew", padx=10, pady=10)

        self.temperature_slider = ttk.Scale(self.frame, from_=0, to=2, value=0.5, orient=tk.HORIZONTAL,
                                            command=self.on_temperature_change)

        self.temperature_slider.grid(row=4, column=3, sticky="ew", padx=10, pady=10)

        self.temperature = tk.Label(self.frame, text="0")
        self.temperature.grid(row=4, column=4, sticky="ew", padx=10, pady=10)
        self.on_temperature_change(0.5)

        self.max_tokens_label = tk.Label(self.frame, text="Max Tokens:")
        self.max_tokens_label.grid(row=5, column=2, sticky="ew", padx=10, pady=10)

        self.max_tokens = tk.Entry(self.frame, textvariable=tk.StringVar(value="250"))
        self.max_tokens.grid(row=5, column=3, sticky="ew", padx=10, pady=10)

        self.submit = tk.Button(self.frame, text="Submit", font=("Arial", 24), foreground="Black", background="Green", command=self.submit)
        self.submit.grid(row=6, rowspan=3, column=2, columnspan=3, sticky="ew", padx=10, pady=10, ipady=20)

        self.root.mainloop()

    def on_temperature_change(self, value):
        rounded = round(float(value), 2)
        self.temperature.config(text=str(rounded))

    def submit(self):
        prompt = self.prompt.get("1.0", tk.END)
        role = self.role.get("1.0", tk.END)
        output = self.output.get("1.0", tk.END)
        model = self.model.get()
        max_tokens = int(self.max_tokens.get())
        temperature = float(self.temperature_slider.get())

        openai.api_key = os.getenv("OPENAI_API_KEY")
        models = openai.Model.list()
        completion = openai.ChatCompletion.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt}
            ]
        )

        response = completion.choices[0].message
        content = response["content"]
        self.output.insert(tk.END, content)

