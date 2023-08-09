import customtkinter

from text_models import TextModels
from menu import Menu
from image_models import ImageModels

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        customtkinter.CTk.__init__(self)
        self.class_mapping = None
        self.frames = None
        self.container = None
        self.title("OpenAI API Interface")
        self.create_widgets()

    def create_widgets(self):
        #   Frame Container
        self.container = customtkinter.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        print("Container created:", self.container.winfo_width(), self.container.winfo_height())

        #   Frames
        self.frames = {}
        self.class_mapping = {"Menu": Menu, "TextModels": TextModels, "ImageModels": ImageModels}
        for f in (Menu, TextModels, ImageModels):  # defined subclasses of BaseFrame
            frame = f(self.container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_columnconfigure(0, weight=1)
            self.frames[f] = frame

        self.show_frame("Menu")

    def show_frame(self, class_name):
        cls = self.class_mapping.get(class_name)
        if cls:
            self.frames[cls].tkraise()

    def change_geometry(self, width, height):
        self.geometry(f"{width}x{height}")

    def change_min_size(self, width, height):
        self.minsize(width, height)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    exit()
