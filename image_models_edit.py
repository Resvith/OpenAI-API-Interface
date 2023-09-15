import json
import os
import tkinter as tk
from tkinter import filedialog

import customtkinter
import cv2 as cv
import numpy as np
import openai
from PIL import Image

from controller_frame import ControllerFrame

file_mask_path = ""


def write_data_to_json_file(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def delete_temp_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


class ImageModelsEdit(ControllerFrame):

    def __init__(self, master, controller):
        super().__init__(master, controller)

    def create_widgets(self):
        # Container for all widgets:
        self.class_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.class_container.grid(row=0, rowspan=2, column=0, sticky="nsew", padx=20, pady=20)
        self.class_container.grid_columnconfigure(0, weight=1)
        self.class_container.grid_columnconfigure(1, weight=0)
        self.class_container.grid_rowconfigure(0, weight=1)
        self.class_container.grid_rowconfigure(1, weight=20)
        self.class_container.grid_rowconfigure(2, weight=1)
        self.class_container.grid_rowconfigure(3, weight=0)

        # Top frame:
        self.top_frame = customtkinter.CTkFrame(self.class_container, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=10)
        self.top_frame.grid_columnconfigure(2, weight=2)
        self.top_frame.grid_rowconfigure(0, weight=1)

        # Loaded file info:
        self.loaded_file_info_label = customtkinter.CTkLabel(self.top_frame, text="No file loaded", font=("New Times Rome", 20), anchor="w")
        self.loaded_file_info_label.grid(row=0, column=1, sticky="nsew", padx=10)

        # Switch variations frame and label:
        self.switch_variations = customtkinter.CTkFrame(self.top_frame, fg_color="transparent")
        self.switch_variations.grid(row=0, column=2, sticky="e", padx=10)
        self.switch_variations_label = customtkinter.CTkLabel(self.switch_variations, text="0/0", font=("New Times Rome", 20))
        self.switch_variations_label.grid(row=0, column=0, sticky="e", padx=10)

        # Switch variations buttons:
        self.switch_variations_back_button = customtkinter.CTkButton(self.switch_variations, text="<", font=("New Times Rome", 20), width=50, height=50)
        self.switch_variations_back_button.grid(row=0, column=1, sticky="e", padx=10)
        self.switch_variations_next_button = customtkinter.CTkButton(self.switch_variations, text=">", font=("New Times Rome", 20), width=50, height=50)
        self.switch_variations_next_button.grid(row=0, column=2, sticky="e", padx=10)

        # Image frame:
        self.image_frame = customtkinter.CTkFrame(self.class_container)
        self.image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Buttons to select and edit image:
        add_image_dark_mode = Image.open("img\\add_image_button_dark_mode.png")
        add_image_light_mode = Image.open("img\\add_image_button_light_mode.png")
        add_image_image = customtkinter.CTkImage(add_image_light_mode, add_image_dark_mode, size=(512, 512))
        self.add_file_button = customtkinter.CTkButton(self.image_frame, text="", image=add_image_image, fg_color="transparent", command=self.on_add_file_button_click)
        self.add_file_button.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        add_mask_dark_mode = Image.open("img\\add_mask_button_dark_mode.png")
        add_mask_light_mode = Image.open("img\\add_mask_button_light_mode.png")
        add_mask_image = customtkinter.CTkImage(add_mask_light_mode, add_mask_dark_mode, size=(512, 512))
        self.add_mask_button = customtkinter.CTkButton(self.image_frame, text="", image=add_mask_image, fg_color="transparent", command=self.on_add_mask_button_click)
        self.add_mask_button.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        # Input:
        self.input_textbox = customtkinter.CTkTextbox(self.class_container, font=("New Times Rome", 20))
        self.input_textbox.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Options frame:
        self.options_frame = customtkinter.CTkFrame(self.class_container, fg_color="transparent")
        self.options_frame.grid(row=0, rowspan=2, column=1, sticky="nsew", padx=10)

        # Menu button:
        self.go_to_menu_button = customtkinter.CTkButton(self.options_frame, text="Menu", font=("New Times Rome", 20), command=self.go_to_menu)
        self.go_to_menu_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=(5, 10))

        # Show original image button:
        self.show_original_image_button = customtkinter.CTkButton(self.options_frame, text="Show original image", font=("New Times Rome", 20))
        self.show_original_image_button.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Show edited image button:
        self.show_edited_image_button = customtkinter.CTkButton(self.options_frame, text="Show edited image", font=("New Times Rome", 20))
        self.show_edited_image_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Save as button:
        self.save_as_button = customtkinter.CTkButton(self.options_frame, text="Save as", font=("New Times Rome", 20))
        self.save_as_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Save in images button:
        self.save_in_images_button = customtkinter.CTkButton(self.options_frame, text="Save in images", font=("New Times Rome", 20))
        self.save_in_images_button.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        # Request parameter frame:
        self.request_parameter_frame = customtkinter.CTkFrame(self.options_frame, fg_color="transparent")
        self.request_parameter_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)

        # Number of variations:
        self.number_of_variations_label = customtkinter.CTkLabel(self.request_parameter_frame, text="Number of variations:", font=("New Times Rome", 20), anchor="w")
        self.number_of_variations_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.number_of_variations_option_menu = customtkinter.CTkOptionMenu(self.request_parameter_frame, font=("New Times Rome", 20), values=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
        self.number_of_variations_option_menu.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Size of generated image:
        self.size_of_generated_image_label = customtkinter.CTkLabel(self.request_parameter_frame, text="Size of generated image:", font=("New Times Rome", 20), anchor="w")
        self.size_of_generated_image_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.size_of_generated_image_option_menu = customtkinter.CTkOptionMenu(self.request_parameter_frame, font=("New Times Rome", 20), values=['256x256', '512x512', '1024x1024'])
        self.size_of_generated_image_option_menu.set("1024x1024")   # Debug
        self.size_of_generated_image_option_menu.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Send button:
        self.send_button = customtkinter.CTkButton(self.class_container, text="Send", font=("New Times Rome", 20), command=self.on_send_button_click)
        self.send_button.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

    def on_add_mask_button_click(self):
        global file_mask_path
        if not self.file_path:
            return

        # Mask editor instance:
        file_mask_path = self.file_path
        MaskEditorWindow()

        # Load mask image:
        img_data = Image.open("image models\\temp.png")
        image = customtkinter.CTkImage(img_data, size=(512, 512))
        image_in_app = customtkinter.CTkLabel(self.image_frame, image=image, text="")
        image_in_app.grid(row=0, column=1, sticky="nsew")

    def on_send_button_click(self):
        self.api_request()

    def check_if_request_is_possible(self) -> bool:
        if not self.file_path:
            return False

        if not os.path.exists("image models\\temp.png"):
            return False

        return True

    def api_request(self):
        if not self.file_path:
            return

        # Get request parameters:
        number_of_variations = self.number_of_variations_option_menu.get()
        size_of_generated_image = self.size_of_generated_image_option_menu.get()
        input_text = self.input_textbox.get("1.0", tk.END)
        openai.api_key = os.getenv("OPENAI_API_KEY")

        if not self.check_if_request_is_possible():
            print("Request is not possible")
            return

        response = openai.Image.create_edit(
            image=open("image models\\temp.png", "rb"),
            prompt=input_text,
            n=number_of_variations,
            size=size_of_generated_image
        )

        os.remove("image models\\temp.png")
        print(response["data"][0]["url"])

    def on_add_file_button_click(self):
        self.file_path = filedialog.askopenfilename(title="Choose image file", filetypes=[("Image files", ".jpg .jpeg .png")])
        if not self.file_path:
            return

        self.loaded_file_info_label.configure(text=f"Selected: {self.file_path.split('/')[-1]}")
        img_data = Image.open(self.file_path)

        self.image_frame.children.clear()
        image = customtkinter.CTkImage(img_data, size=(512, 512))
        image_in_app = customtkinter.CTkLabel(self.image_frame, image=image, text="")
        image_in_app.bind("<Button-1>", command=self.on_add_mask_button_click)
        image_in_app.grid(row=0, column=0, sticky="nsew")

    def set_default_values(self):
        # Create config file if it doesn't exist
        if not (os.path.exists("config.json")):
            self.controller.create_default_config()

        # Load config file to variables:
        with open("config.json", "r") as config_file:
            pass

    def go_to_menu(self):
        self.controller.show_frame("Menu")
        self.controller.change_geometry(400, 400)
        self.controller.change_min_size(400, 400)
        self.controller.is_resizable(False)
        delete_temp_file("image models\\temp.png")


class MaskEditorWindow:
    def __init__(self):
        super().__init__()

        # variables
        self.circle_size = 8
        self.ix = -1
        self.iy = -1
        self.drawing = False
        self.all_coordinates = []

        self.show_editable_window(file_mask_path)

    def show_editable_window(self, file_path):
        self.img_original = cv.imread(file_path)
        self.img_alpha = cv.cvtColor(self.img_original, cv.COLOR_RGB2RGBA)
        self.img_editable = self.img_alpha.copy()
        self.img_front = self.img_alpha.copy()

        cv.namedWindow(winname="Mark it what you want edit")
        cv.setMouseCallback("Mark it what you want edit",
                            self.draw_outline_with_lines)

        # Show editable window until it is closed
        while True:
            cv.imshow("Mark it what you want edit", self.img_front)
            cv.waitKey(10)
            if cv.getWindowProperty('Mark it what you want edit', cv.WND_PROP_VISIBLE) < 1:
                self.save_image_like_png(self.img_alpha)
                break

    cv.destroyAllWindows()

    @staticmethod
    def save_image_like_png(image):
        cv.imwrite("image models\\temp.png", image)

    def check_if_it_is_last_coordinate(self, radius):
        first_point = self.all_coordinates[0]
        last_point = self.all_coordinates[-1]

        if abs(first_point[0] - last_point[0]) < radius and abs(first_point[1] - last_point[1] < radius):
            self.drawing = False
            self.cut_image()

    def cut_image(self):
        self.all_coordinates.pop()
        coordinates_array = np.array(self.all_coordinates, dtype=np.int32)
        cv.fillPoly(self.img_front, [coordinates_array], (0, 0, 0, 0))
        cv.fillPoly(self.img_alpha, [coordinates_array], (0, 0, 0, 0))
        self.all_coordinates.clear()

    def draw_outline_with_lines(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix = x
            self.iy = y
            self.all_coordinates.append((x, y))
            if len(self.all_coordinates) == 1:
                cv.circle(self.img_front, center=(x, y), radius=self.circle_size, color=(0,0,255), thickness=self.circle_size)
                self.img_editable = self.img_front.copy()

            else:
                cv.line(self.img_front, pt1=(self.ix, self.iy),
                                  pt2=(x, y),
                                  color=(0, 255, 255),
                                  thickness=5)
                self.img_editable = self.img_front.copy()
                self.check_if_it_is_last_coordinate(self.circle_size)

        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing:
                self.img_front = self.img_editable.copy()
                cv.line(self.img_front, pt1=(self.ix, self.iy),
                                  pt2=(x, y),
                                  color=(0, 255, 255),
                                  thickness=5)


