import tkinter as tk
from tkinter import ttk, TOP, SUNKEN
from tkinter import filedialog
import pandas as pd
from PIL import Image, ImageTk
from CropApp import CropApp
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter.simpledialog import askstring
from OCR_extraction import process_image


class NutriScanApp(TkinterDnD.Tk):
    def __init__(self, *args, **kwargs):
        TkinterDnD.Tk.__init__(self, *args, **kwargs)
        self.state('zoomed')
        self.title('NutriScan')
        self.img_file_path = None

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>",
                             lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        container = tk.Frame(self.canvas)

        self.frames = {}

        for F in (PageOne, PageThree):
            frame = F(container, self)
            self.frames[F] = frame
            frame.pack(side="top", fill="both", expand=True)

        self.show_frame(PageOne)
        self.canvas.create_window((0, 0), window=container, anchor="nw")

    def show_frame(self, cont):
        for frame in self.frames.values():
            frame.pack_forget()

        frame = self.frames[cont]
        frame.pack(side="top", fill="both", expand=True)

        if cont == PageThree:
            frame.initialize_OCR_extraction(self.img_file_path)

        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        if cont == PageTwo:
            self.popup_page_two()

    def popup_page_two(self):
        top = tk.Toplevel(self)
        top.title("Page Two Popup")
        top.geometry("700x500")

        page_two_frame = PageTwo(top, self)
        page_two_frame.pack(fill="both", expand=True)


class PageOne(tk.Frame):
    def open_popup_page_two(self):
        self.controller.popup_page_two()

    def update_image(self, cropped_image):
        pil_image = Image.fromarray(cropped_image)

        self.img = ImageTk.PhotoImage(image=pil_image)

        for widget in self.frame_image.winfo_children():
            widget.destroy()
        label = tk.Label(self.frame_image, image=self.img)
        label.pack()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        my_font1 = ('times', 18, 'bold')
        Heading = tk.Label(self, text='NutriScan', width=30, font=my_font1)
        Heading.pack()

        my_font2 = ('Arial', 14, 'bold')
        label_1 = tk.Label(self, text='Upload the Nutritional label', width=30, font=my_font2)
        label_1.pack()

        entry = tk.Text(self, height=3, width=30)
        entry.configure(state='normal')
        entry.insert(1.0, "Drag and Drop files here")
        entry.configure(state='disabled')

        entry.drop_target_register(DND_FILES)
        entry.dnd_bind('<<Drop>>', lambda e: open_image(e.data))
        entry.pack()

        my_font3 = ('Arial', 14, 'bold')
        label_2 = tk.Label(self, text='OR', width=30, font=my_font3)
        label_2.pack()

        upload_file_button = ttk.Button(self, text='Upload File', width=20, command=lambda: upload_file())
        upload_file_button.pack()

        def upload_file():
            f_types = [('Image Files', '*.png *.jpg *.jpeg *.gif')]
            filename = filedialog.askopenfilename(filetypes=f_types)
            if filename:
                open_image(filename)

        def open_image(filename):
            global img
            img = Image.open(filename)
            frame_width, frame_height = 600, 400
            width_ratio = frame_width / img.width
            height_ratio = frame_height / img.height
            resize_ratio = min(width_ratio, height_ratio)
            new_width = int(img.width * resize_ratio)
            new_height = int(img.height * resize_ratio)
            img = img.resize((new_width, new_height))
            img = ImageTk.PhotoImage(img)
            for widget in self.frame_image.winfo_children():
                widget.destroy()
            label = tk.Label(self.frame_image, image=img)
            label.pack()
            controller.img_file_path = filename
            controller.show_frame(PageOne)

        crop_button = ttk.Button(self, text='Crop Image', width=20, command=self.open_crop_popup)
        crop_button.pack()

        next_page_button = ttk.Button(self, text='Next', width=20, command=lambda: controller.show_frame(PageThree))
        next_page_button.pack()

        self.frame_image = tk.Frame(self, width=600, height=400)
        self.frame_image.pack(pady=20)

    def open_crop_popup(self):
        self.controller.popup_page_two()


class PageTwo(tk.Frame):
    def initialize_crop_app(self):
        if self.controller.img_file_path:
            self.crop_app = CropApp(self, self.controller.img_file_path, self.on_image_cropped)

    def on_image_cropped(self, cropped_image):
        self.controller.show_frame(PageOne)
        self.controller.frames[PageOne].update_image(cropped_image)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.crop_app = None

        if controller.img_file_path:
            self.initialize_crop_app()


class PageThree(tk.Frame):
    def initialize_OCR_extraction(self, img_file_path):
        if self.controller.img_file_path:
            self.img_file_path = img_file_path
            self.process_image_result = process_image(self.controller.img_file_path)
            self.populate_treeview_from_csv()
            self.display_image(img_file_path)

    def populate_treeview_from_csv(self):
        try:
            df = pd.read_csv('nutritional_info.csv', index_col=0)
            for index, row in df.iterrows():
                self.treeview.insert('', 'end', values=(index, row['Value'], row['Confidence']))
        except FileNotFoundError:
            print("CSV file not found.")

    def display_image(self, filename):
        self.img = Image.open(filename)
        frame_width, frame_height = 600, 400
        width_ratio = frame_width / self.img.width
        height_ratio = frame_height / self.img.height
        resize_ratio = min(width_ratio, height_ratio)
        new_width = int(self.img.width * resize_ratio)
        new_height = int(self.img.height * resize_ratio)
        self.img = self.img.resize((new_width, new_height))
        self.img = ImageTk.PhotoImage(self.img)
        for widget in self.frame_image.winfo_children():
            widget.destroy()
        self.label = tk.Label(self.frame_image, image=self.img)
        self.label.pack()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = None
        self.img = None
        self.img_file_path = None
        self.process_image_result = None
        self.controller = controller

        my_font = ('Arial', 18, 'bold')
        page_2_label_1 = tk.Label(self, text='Page 3', width=30, font=my_font)
        page_2_label_1.pack()

        prev_page_button = ttk.Button(self, text='Back', width=20, command=lambda: controller.show_frame(PageOne))
        prev_page_button.pack()

        frame_table = ttk.Frame(self)

        self.treeview = ttk.Treeview(frame_table, columns=('Column1', 'Column2', 'Column3'), show='headings', height=10)
        self.treeview.heading('Column1', text='Nutrient')
        self.treeview.heading('Column2', text='Value')
        self.treeview.heading('Column3', text='Confidence Score')

        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=vsb.set)

        self.treeview.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def edit():
            selected_item = self.treeview.selection()[0]
            new_value = askstring("Edit Value", "Enter new value:")
            if new_value is not None:
                self.treeview.item(selected_item, values=(
                    self.treeview.item(selected_item, 'values')[0], new_value,
                    self.treeview.item(selected_item, 'values')[2]))

        def delete():
            selected_item = self.treeview.selection()[0]
            self.treeview.delete(selected_item)

        edit_btn = ttk.Button(self, text="Edit", command=edit)
        del_btn = ttk.Button(self, text="Delete", command=delete)

        self.frame_image = tk.Frame(self, width=600, height=400)
        self.frame_image.pack(side="left", pady=20, padx=20)
        frame_table.pack(side="left", fill='both', expand=True, pady=20)
        edit_btn.pack(pady=20)
        del_btn.pack()


if __name__ == "__main__":
    app = NutriScanApp()
    app.mainloop()
