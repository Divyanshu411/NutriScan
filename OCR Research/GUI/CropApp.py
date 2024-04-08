import os
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import cv2
from tkinter import ttk
import customtkinter as ctk


class CornerBox:
    """
    Class representing a draggable corner box used for cropping.
    """

    def __init__(self, pos, canvas, c_height, c_width):
        """
        Initialize the corner box.

        Args:
            pos (str): Position of the corner box ('NW', 'NE', 'SE', 'SW').
            canvas (tk.Canvas): Canvas where the corner box will be drawn.
            c_height (int): Height of the canvas.
            c_width (int): Width of the canvas.
        """
        # Set initial position of the corner box based on position argument
        if pos == 'NW':
            self.x, self.y = 5, 5
        elif pos == 'NE':
            self.x, self.y = c_width - 5, 5
        elif pos == 'SE':
            self.x, self.y = c_width - 5, c_height - 5
        elif pos == 'SW':
            self.x, self.y = 5, c_height - 5

        self.c_height, self.c_width = c_height, c_width
        self.canvas = canvas

        # Create the corner box rectangle
        self.cb_id = canvas.create_rectangle(
            self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill="blue")

        # Store initial position for resetting
        self.reset_x, self.reset_y = self.x, self.y

    def grab(self, event):
        """
        Callback function for when the corner box is clicked.
        """
        widget = event.widget
        self.x = widget.canvasx(event.x)
        self.y = widget.canvasy(event.y)
        self.widget = self.cb_id

    def drag(self, event):
        """
        Callback function for when the corner box is dragged.
        """
        widget = event.widget
        xc = widget.canvasx(event.x)
        yc = widget.canvasy(event.y)
        if xc < 5 or yc < 5 or xc > self.c_width - 5 or yc > self.c_height - 5:
            return

        # Move the corner box
        self.canvas.move(self.widget, xc - self.x, yc - self.y)
        self.x, self.y = xc, yc

        # Calculate new center coordinates of the corner box
        x1, y1, x2, y2 = self.canvas.coords(self.cb_id)
        self.x = (x1 + x2) / 2
        self.y = (y1 + y2) / 2

    @property
    def coords(self):
        """
        Get the coordinates of the corner box.

        Returns:
            tuple: (x, y) coordinates of the corner box.
        """
        return (self.x, self.y)

    @property
    def id(self):
        """
        Get the ID of the corner box.

        Returns:
            int: ID of the corner box.
        """
        return self.cb_id

    def reset(self):
        """
        Reset the position of the corner box to its initial position.
        """
        xc, yc = self.reset_x, self.reset_y
        self.canvas.move(self.cb_id, xc - self.x, yc - self.y)
        self.x, self.y = xc, yc

        # Calculate new center coordinates of the corner box
        x1, y1, x2, y2 = self.canvas.coords(self.cb_id)
        self.x = (x1 + x2) / 2
        self.y = (y1 + y2) / 2

    @coords.setter
    def coords(self, xc, yc):
        """
        Set the coordinates of the corner box.

        Args:
            xc (int): New x-coordinate.
            yc (int): New y-coordinate.
        """
        if xc < 5 or yc < 5 or xc > self.c_width - 5 or yc > self.c_height - 5:
            return
        self.canvas.move(self.cb_id, xc - self.x, yc - self.y)
        self.x, self.y = xc, yc

        # Calculate new center coordinates of the corner box
        x1, y1, x2, y2 = self.canvas.coords(self.cb_id)
        self.x = (x1 + x2) / 2
        self.y = (y1 + y2) / 2


class CropApp:
    """
    Class representing the main application for cropping images.
    """

    def __init__(self, master, img, on_cropped):
        """
        Initialize the CropApp.

        Args:
            master: Parent widget.
            img (str): Path to the image file to be cropped.
            on_cropped (function): Callback function to handle cropped image.
        """
        self.master = master
        self.on_cropped = on_cropped

        main_frame = tk.Frame(master)
        main_frame.pack(fill=tk.BOTH, expand=1)

        my_canvas = tk.Canvas(main_frame)
        my_canvas.pack(side="left", fill="both", expand=1)

        scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=my_canvas.yview)
        scrollbar.pack(side="right", fill="y")

        my_canvas.config(yscrollcommand=scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox('all')))

        second_frame = tk.Frame(my_canvas)

        my_canvas.create_window((0, 0), window=second_frame, anchor="nw")

        my_font1 = ('Times', 28, 'bold')
        Heading = tk.Label(second_frame, text='NutriScan', width=30, font=my_font1)
        Heading.pack(pady=10, padx=200)

        my_font2 = ('Arial', 16, 'bold')
        label_2 = tk.Label(second_frame, text='Crop Images', width=30, font=my_font2)
        label_2.pack()

        self.crop_directory = os.path.join(os.path.dirname(os.path.abspath(img)), "crop")
        if not os.path.exists(self.crop_directory):
            os.makedirs(self.crop_directory)

        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()

        self.img_file_name = img
        self.im = Image.open(img)
        self.img_width, self.img_height = self.im.size

        f1 = 0
        f2 = 0
        self.scale_factor = 1

        if self.img_width > self.screen_width:
            f1 = self.img_width // self.screen_width

        if self.img_height > self.screen_height:
            f2 = self.img_height // self.screen_height

        if f1 != 0 or f2 != 0:
            self.scale_factor = max(f1, f2)
            self.scale_factor += 1
            self.im = self.im.resize(
                (self.img_width // self.scale_factor, self.img_height // self.scale_factor))
            self.img_width, self.img_height = self.im.size

        self.c_width = self.img_width + 10
        self.c_height = self.img_height + 10

        self.canvas = tk.Canvas(second_frame, width=self.c_width, height=self.c_height)
        self.canvas.pack(pady=10)

        self.img_canvas = ImageTk.PhotoImage(self.im)
        self.img_canvas_img_id = self.canvas.create_image(
            5, 5, image=self.img_canvas, anchor=tk.NW)

        # Create corner boxes for cropping
        self.NW = CornerBox('NW', self.canvas, self.c_height, self.c_width)
        self.NE = CornerBox('NE', self.canvas, self.c_height, self.c_width)
        self.SE = CornerBox('SE', self.canvas, self.c_height, self.c_width)
        self.SW = CornerBox('SW', self.canvas, self.c_height, self.c_width)

        # Buttons for actions
        self.but_frame = tk.Frame(second_frame)
        self.but_frame.pack()

        self.reset_butt = ctk.CTkButton(
            self.but_frame, text="Reset", width=100, command=self.restCorners)
        self.reset_butt.pack(side=tk.LEFT, pady=5, padx=5)

        self.crop_and_sav_butt = ctk.CTkButton(
            self.but_frame, text="Crop and Save", width=100, command=self.cropImage)
        self.crop_and_sav_butt.pack(side=tk.LEFT, pady=5, padx=5)

        self.rotate_image_butt = ctk.CTkButton(
            self.but_frame, text="Rotate", width=100, command=self.rotate_image)
        self.rotate_image_butt.pack(side=tk.LEFT, pady=5, padx=5)

        # IDs for drawing the cropping box
        self.box_id = None
        self.p1_id = None
        self.p2_id = None
        self.p3_id = None
        self.p4_id = None

        # Draw the initial cropping box
        self.drawBox()

        # Bind events for corner box dragging
        for i in [self.NW, self.NE, self.SE, self.SW]:
            self.canvas.tag_bind(i.cb_id, "<Button-1>", i.grab)
            self.canvas.tag_bind(i.cb_id, "<B1-Motion>", i.drag)

    def printBoxDetails(self):
        print(self.NW.coords, self.NE.coords, self.SE.coords, self.SW.coords)

    def restCorners(self):
        """
        Reset the position of corner boxes.
        """
        self.NW.reset()
        self.NE.reset()
        self.SE.reset()
        self.SW.reset()

    def rotate_image(self):
        """
        Rotate the image by 90 degrees and redraw the cropping box.
        """
        self.im = self.im.rotate(90, expand=True)
        self.img_canvas = ImageTk.PhotoImage(self.im)
        self.canvas.itemconfig(self.img_canvas_img_id, image=self.img_canvas)
        self.NW.reset()
        self.NE.reset()
        self.SE.reset()
        self.SW.reset()
        self.drawBox()

    def cropImage(self):
        """
        Crop the image based on the selected area and save it.
        """
        A, B, C, D = self.NW.coords, self.NE.coords, self.SE.coords, self.SW.coords
        A = (A[0] * self.scale_factor, A[1] * self.scale_factor)
        B = (B[0] * self.scale_factor, B[1] * self.scale_factor)
        C = (C[0] * self.scale_factor, C[1] * self.scale_factor)
        D = (D[0] * self.scale_factor, D[1] * self.scale_factor)

        pts1 = np.float32([list(A), list(B), list(D), list(C)])

        widthA = np.sqrt(((D[0] - C[0])
                          ** 2) + ((D[1] - C[1]) ** 2))
        widthB = np.sqrt(((A[0] - B[0])
                          ** 2) + ((A[1] - B[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((A[0] - D[0]) ** 2) + (
                (A[1] - D[1]) ** 2))
        heightB = np.sqrt(((B[0] - C[0]) ** 2) + (
                (B[1] - C[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        pts2 = np.float32(
            [[0, 0],
             [maxWidth, 0],
             [0, maxHeight],
             [maxWidth, maxHeight]]
        )

        img = cv2.imread(self.img_file_name)
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        self.res = cv2.warpPerspective(img, matrix, (maxWidth, maxHeight))
        resized_image = cv2.resize(
            self.res, (0, 0), fx=1 / self.scale_factor, fy=1 / self.scale_factor)

        # Save the cropped image
        cropped_image_name = os.path.join(self.crop_directory,
                                          os.path.basename(self.img_file_name).replace('.', '_cropped.'))
        cv2.imwrite(cropped_image_name, self.res)
        self.on_cropped(cropped_image_name)

    def drawBox(self, event=None):
        """
        Draw the cropping box on the canvas.
        """
        if self.box_id != None:
            self.canvas.delete(self.box_id)
        if self.p1_id != None:
            self.canvas.delete(self.p1_id)
        if self.p2_id != None:
            self.canvas.delete(self.p2_id)
        if self.p3_id != None:
            self.canvas.delete(self.p3_id)
        if self.p4_id != None:
            self.canvas.delete(self.p4_id)

        # Draw the cropping box
        self.box_id = self.canvas.create_line(
            *self.NW.coords,
            *self.NE.coords,
            *self.SE.coords,
            *self.SW.coords,
            *self.NW.coords,
            fill="blue", width=2)

        # Draw polygons to cover the cropped areas outside the box
        self.p1_id = self.canvas.create_polygon(
            0, 0, *self.NW.coords, *self.SW.coords, 0, self.c_height, fill="blue", stipple="gray25")
        self.p2_id = self.canvas.create_polygon(
            0, 0, *self.NW.coords, *self.NE.coords, self.c_width, 0, fill="blue", stipple="gray25")
        self.p3_id = self.canvas.create_polygon(
            self.c_width, 0, *self.NE.coords, *self.SE.coords, self.c_width, self.c_height, fill="blue",
            stipple="gray25")
        self.p4_id = self.canvas.create_polygon(
            self.c_width, self.c_height, *self.SE.coords, *self.SW.coords, 0, self.c_height, fill="blue",
            stipple="gray25")

        self.canvas.tag_raise(self.NW.cb_id, 'all')
        self.canvas.tag_raise(self.NE.cb_id, 'all')
        self.canvas.tag_raise(self.SE.cb_id, 'all')
        self.canvas.tag_raise(self.SW.cb_id, 'all')

        # Redraw the cropping box after a short delay
        self.canvas.after(1, self.drawBox)