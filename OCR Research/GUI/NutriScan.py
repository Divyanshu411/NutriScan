import csv
import os
import tempfile
import tkinter as tk
from tkinter import ttk, TOP, SUNKEN
from tkinter import filedialog
import pandas as pd
from PIL import Image, ImageTk, ExifTags
from CropApp import CropApp
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter.simpledialog import askstring
from OCR_extraction import process_image
from tkinter.filedialog import asksaveasfile
import sqlite3


class NutriScanApp(TkinterDnD.Tk):
    def __init__(self, *args, **kwargs):
        TkinterDnD.Tk.__init__(self, *args, **kwargs)
        self.state('zoomed')
        self.title('NutriScan')
        self.img_file_path = None
        self.cropped_image_path = None

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

        for F in (PageOne, PageTwo):
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

        if cont == PageTwo:
            frame.initialize_OCR_extraction(self.img_file_path)
            frame.populate_treeview_from_csv()

        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        if cont == CropPopup:
            self.popup_page_two()

    def popup_page_two(self):
        top = tk.Toplevel(self)
        top.title("Page Two Popup")
        top.state("zoomed")

        page_two_frame = CropPopup(top, self)
        page_two_frame.pack(fill="both", expand=True)


class PageOne(tk.Frame):
    def open_popup_page_two(self):
        self.controller.popup_page_two()

    def update_image(self, cropped_image_path):
        if not os.path.exists(cropped_image_path):
            print("Error: Cropped image file does not exist at:", cropped_image_path)
            return
        try:
            self.img = Image.open(cropped_image_path)
            self.img = self.img.resize((600, 400))
            self.img = ImageTk.PhotoImage(self.img)

            for widget in self.frame_image.winfo_children():
                widget.destroy()

            label = tk.Label(self.frame_image, image=self.img)
            label.pack()
        except Exception as e:
            print("Error:", e)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        my_font1 = ('times', 18, 'bold')
        Heading = tk.Label(self, text='NutriScan', width=30, font=my_font1)
        Heading.pack()

        my_font2 = ('Arial', 12, 'bold')
        label_1 = tk.Label(self, text='Upload Image', width=30, font=my_font2)
        label_1.pack()

        entry = tk.Text(self, height=3, width=30)
        entry.configure(state='normal')
        entry.insert(1.0, "Drag and Drop files here")
        entry.configure(state='disabled')

        entry.drop_target_register(DND_FILES)
        entry.dnd_bind('<<Drop>>', lambda e: open_image(e.data))
        entry.pack(pady=10)

        my_font3 = ('Arial', 12, 'bold')
        label_2 = tk.Label(self, text='OR', width=30, font=my_font3)
        label_2.pack(pady=5)

        upload_file_button = ttk.Button(self, text='Upload File', width=20, command=lambda: upload_file())
        upload_file_button.pack()

        def upload_file():
            f_types = [('Image Files', '*.png *.jpg *.jpeg')]
            filename = filedialog.askopenfilename(filetypes=f_types)
            if filename:
                open_image(filename)

        def open_image(filepath):
            filepath = filepath.strip('{}')
            global img
            img = Image.open(filepath)

            orientation_fixed = False
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(img._getexif().items())

            if 'Orientation' in exif:
                orientation_fixed = True
                if exif[orientation] == 3:
                    img = img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    img = img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    img = img.rotate(90, expand=True)

            frame_width, frame_height = 600, 400
            width_ratio = frame_width / img.width
            height_ratio = frame_height / img.height
            resize_ratio = min(width_ratio, height_ratio)
            new_width = int(img.width * resize_ratio)
            new_height = int(img.height * resize_ratio)
            img = img.resize((new_width, new_height))

            if orientation_fixed:
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                temp_file_path = temp_file.name
                img.save(temp_file_path)
                img_file_path = temp_file_path
            else:
                img_file_path = filepath

            img = ImageTk.PhotoImage(img)
            for widget in self.frame_image.winfo_children():
                widget.destroy()
            label = tk.Label(self.frame_image, image=img)
            label.pack()
            controller.img_file_path = img_file_path
            controller.show_frame(PageOne)

        crop_button = ttk.Button(self, text='Crop Image', width=20, command=self.open_crop_popup)
        crop_button.pack()

        next_page_button = ttk.Button(self, text='Next', width=20, command=lambda: controller.show_frame(PageTwo))
        next_page_button.pack()

        self.frame_image = tk.Frame(self, width=600, height=400)
        self.frame_image.pack(pady=20, padx=10)

    def open_crop_popup(self):
        self.controller.popup_page_two()


class CropPopup(tk.Frame):
    def initialize_crop_app(self):
        if self.controller.img_file_path:
            self.crop_app = CropApp(self, self.controller.img_file_path, self.on_image_cropped)

    def on_image_cropped(self, cropped_image_path):
        self.controller.show_frame(PageOne)
        self.controller.frames[PageOne].update_image(cropped_image_path)
        self.controller.img_file_path = cropped_image_path
        self.master.destroy()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.crop_app = None

        if controller.img_file_path:
            self.initialize_crop_app()


class PageTwo(tk.Frame):
    def initialize_OCR_extraction(self, img_file_path):
        if self.controller.img_file_path:
            self.img_file_path = img_file_path
            self.process_image_result = process_image(self.controller.img_file_path)
            self.populate_treeview_from_csv()
            self.display_image(img_file_path)

    def populate_treeview_from_csv(self):
        x = self.treeview.get_children()
        for item in x:
            self.treeview.delete(item)
        try:
            df = pd.read_csv('nutritional_info.csv', index_col=0)
            for index, row in df.iterrows():
                values = (index, row['Value'], row['Confidence'])
                if row['Confidence'] < 90 and row['Confidence'] != 0:
                    self.treeview.insert('', 'end', values=values, tags=('orange_row',))
                else:
                    self.treeview.insert('', 'end', values=values)
            self.treeview.tag_configure('orange_row', background='orange')
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

    def edit(self):
        selected_item = self.treeview.selection()[0]
        nutrient_name = self.treeview.item(selected_item, 'values')[0]
        new_value = askstring("Edit Value", f"Enter new value for {nutrient_name}:")
        if new_value is not None:
            self.treeview.item(selected_item, values=(
                self.treeview.item(selected_item, 'values')[0], new_value,
                self.treeview.item(selected_item, 'values')[2]))

    def delete(self):
        selected_item = self.treeview.selection()[0]
        self.treeview.delete(selected_item)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = None
        self.img = None
        self.img_file_path = None
        self.process_image_result = None
        self.controller = controller

        my_font = ('Arial', 18, 'bold')
        page_2_label_1 = tk.Label(self, text='NutriScan', width=30, font=my_font)
        page_2_label_1.pack()

        prev_page_button = ttk.Button(self, text='Back', width=20, command=lambda: controller.show_frame(PageOne))
        prev_page_button.pack()

        self.frame_image = tk.Frame(self, width=600, height=400)
        self.frame_image.pack(side="left", pady=20, padx=20)

        treeview_button_frame = ttk.Frame(self)
        treeview_button_frame.pack(side="right", padx=20, pady=20)

        edit_btn = ttk.Button(treeview_button_frame, text="Edit", command=self.edit)
        del_btn = ttk.Button(treeview_button_frame, text="Delete", command=self.delete)
        edit_btn.pack(side="top", padx=5, pady=5)
        del_btn.pack(side="top", padx=5, pady=5)

        frame_table = ttk.Frame(self)
        frame_table.pack(side="top", fill='both', pady=20)

        self.treeview = ttk.Treeview(frame_table, columns=('Column1', 'Column2', 'Column3'), show='headings', height=30)
        self.treeview.heading('Column1', text='Nutrient')
        self.treeview.heading('Column2', text='Value (g)')
        self.treeview.heading('Column3', text='Confidence Score')

        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=vsb.set)

        self.treeview.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def save_csv():
            file_path = asksaveasfile(initialfile='Untitled.csv',
                                      defaultextension=".csv", filetypes=[("All files", "*.*"), ("csv", "*.csv")])
            if file_path:
                file_path = file_path.name
                data = []
                for child in self.treeview.get_children():
                    values = self.treeview.item(child, 'values')
                    data.append(values)

                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Nutrient', 'Value', 'Confidence Score'])
                    writer.writerows(data)

        def export_appended_csv():
            conn = sqlite3.connect('nutrition_data.db')

            # Read the table into a DataFrame
            df = pd.read_sql_query("SELECT * FROM nutrition_table", conn)

            # Close the database connection
            conn.close()
            file_path = asksaveasfile(initialfile='Untitled_appended.csv',
                                      defaultextension=".csv", filetypes=[("All files", "*.*"), ("csv", "*.csv")])
            if file_path is not None:
                df.to_csv(file_path.name, index=False)

        def append_csv():
            image_file_name = os.path.basename(self.controller.img_file_path)

            df = pd.read_csv('nutritional_info.csv')
            column_order = ['Food label'] + df['Nutrient'].drop_duplicates().tolist()
            df = df.drop(columns=['Confidence'])

            df['Food label'] = image_file_name

            df = df.pivot_table(index='Food label', columns='Nutrient', values='Value', aggfunc='first')
            df.reset_index(inplace=True)

            df = df[column_order]
            conn = sqlite3.connect('nutrition_data.db')

            query = f"SELECT * FROM nutrition_table WHERE `Food label` = '{image_file_name}'"
            existing_df = pd.read_sql_query(query, conn)

            if existing_df.empty:
                df.to_sql('nutrition_table', conn, if_exists='append', index=False)

            conn.close()

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(side="top", padx=5, pady=5)

        export_csv_btn = ttk.Button(frame_buttons, text="Export CSV", command=save_csv)
        export_csv_btn.pack(side="left", padx=5)

        append_csv_btn = ttk.Button(frame_buttons, text="Append CSV", command=append_csv)
        append_csv_btn.pack(side="left", padx=5)

        export_append_csv_btn = ttk.Button(frame_buttons, text="Export Append CSV", command=export_appended_csv)
        export_append_csv_btn.pack(side="left", padx=5)


if __name__ == "__main__":
    app = NutriScanApp()
    app.mainloop()
