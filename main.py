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

        #   Frames
        self.frames = {}
        for F in (Menu, TextModels, ImageModels):  # defined subclasses of BaseFrame
            class_name = F.__name__
            frame = F(self.container, self)
            self.frames[class_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show start window
        # self.show_frame("Menu")
        # self.change_geometry(400, 400)
        # self.change_min_size(400, 400)
        self.show_frame("ImageModels")
        self.change_geometry(1400, 800)
        self.change_min_size(1100, 580)

    def show_frame(self, class_name):
        for frame in self.frames.values():
            frame.grid_remove()
        frame = self.frames[class_name]
        frame.grid()
        frame.grid(row=0, column=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

    def change_geometry(self, width, height):
        self.geometry(f"{width}x{height}")

    def change_min_size(self, width, height):
        self.minsize(width, height)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    exit()
