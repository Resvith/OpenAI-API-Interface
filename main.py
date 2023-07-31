import tkinter as tk
from tkinter import ttk
import openai
import os


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


if __name__ == "__main__":
    gui = GUI()

