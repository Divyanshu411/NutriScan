import csv
import os
import tempfile
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
from PIL import Image, ImageTk, ExifTags
from CropApp import CropApp
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter.simpledialog import askstring
from OCR_extraction import process_image
from tkinter.filedialog import asksaveasfile
import sqlite3
import customtkinter as ctk
from tkinter import messagebox
import warnings

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", ".*CTk.*Warning: Given image is not CTkImage.*")


class NutriScanApp(TkinterDnD.Tk):
    """
    Application for extracting nutritional information from images.
    """

    def __init__(self, *args, **kwargs):
        TkinterDnD.Tk.__init__(self, *args, **kwargs)
        self.state("zoomed")
        self.title('NutriScan')
        self.img_file_path = None
        self.cropped_image_path = None

        self.minsize(800, 800)

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}

        for F in (PageOne, PageTwo):
            frame = F(container, self)
            self.frames[F] = frame
            frame.pack(side="top", fill="both", expand=True)

        self.show_frame(PageOne)

    def show_frame(self, cont):
        """
        Show the frame corresponding to the given controller.
        """
        for frame in self.frames.values():
            frame.pack_forget()

        frame = self.frames[cont]
        frame.pack(side="top", fill="both", expand=True)

        if cont == PageTwo:
            frame.initialize_OCR_extraction(self.img_file_path)
            frame.populate_treeview_from_csv()

        self.update_idletasks()

        if cont == CropPopup:
            self.popup_page_two()

    def popup_page_two(self):
        """
        Popup the second page.
        """
        top = tk.Toplevel(self)
        top.title("Page Two Popup")
        top.state("zoomed")

        page_two_frame = CropPopup(top, self)
        page_two_frame.pack(fill="both", expand=True)


class PageOne(ctk.CTkFrame):
    """
    First page of the application for selecting and cropping images.
    """

    def open_popup_page_two(self):
        """
        Open the popup for the second page.
        """
        self.controller.popup_page_two()

    def update_image(self, cropped_image_path):
        """
        Update the displayed image.
        """
        if not os.path.exists(cropped_image_path):
            print("Error: Cropped image file does not exist at:", cropped_image_path)
            return
        try:
            self.img = Image.open(cropped_image_path)
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

            label = ctk.CTkLabel(self.frame_image, image=self.img, text="")
            label.place(x=frame_width / 2 - new_width / 2, y=frame_height / 2 - new_height / 2)
        except Exception as e:
            print("Error:", e)

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller

        my_font1 = ('Times', 28, 'bold')
        Heading = ctk.CTkLabel(self, text='NutriScan', width=30, font=my_font1)
        Heading.pack(padx=10, pady=10)

        my_font2 = ('Arial', 12, 'bold')
        label_2 = ctk.CTkLabel(self, text='Please choose an Image to extract data', width=30, font=my_font2)
        label_2.pack()

        entry = ctk.CTkTextbox(self, height=50, width=300)
        entry.configure(state='normal')
        entry.insert(1.0, "Drag and Drop here")
        entry.configure(state='disabled')

        entry.drop_target_register(DND_FILES)
        entry.dnd_bind('<<Drop>>', lambda e: open_image(e.data))
        entry.pack(pady=10)

        my_font3 = ('Arial', 12, 'bold')
        label_3 = ctk.CTkLabel(self, text='OR', width=30, font=my_font3)
        label_3.pack()

        upload_file_button = ctk.CTkButton(self, text='Select File', width=200, command=lambda: upload_file())
        upload_file_button.pack(pady=10)

        def upload_file():
            """
            Upload the selected image
            """
            f_types = [('Image Files', '*.png *.jpg *.jpeg')]
            filename = filedialog.askopenfilename(filetypes=f_types)
            if filename:
                open_image(filename)

        def open_image(filepath):
            """
            Open the uploaded image
            """
            progress_bar = ctk.CTkProgressBar(self, mode='indeterminate')
            progress_bar.pack(pady=10)
            progress_bar.start()

            def process_image(filepath=filepath):
                """
                Process the uploaded image and fix the orientation and size of the image
                """
                filepath = filepath.strip('{}')
                global img
                img = Image.open(filepath)

                self.controller.original_file_name = os.path.basename(filepath)

                orientation_fixed = False
                if hasattr(img, '_getexif'):
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    e = img._getexif()
                    if e is not None:
                        exif = dict(e.items())
                        if orientation in exif:
                            orientation_fixed = True
                            if exif[orientation] == 3:
                                img = img.rotate(180, expand=True)
                            elif exif[orientation] == 6:
                                img = img.rotate(270, expand=True)
                            elif exif[orientation] == 8:
                                img = img.rotate(90, expand=True)

                if orientation_fixed:
                    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    temp_file_path = temp_file.name
                    img.save(temp_file_path)
                    original_img_file_path = temp_file_path
                else:
                    original_img_file_path = filepath

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
                label = ctk.CTkLabel(self.frame_image, image=img, text="")
                label.place(x=frame_width / 2 - new_width / 2, y=frame_height / 2 - new_height / 2)
                label.lift()
                controller.img_file_path = original_img_file_path
                controller.show_frame(PageOne)

                progress_bar.stop()
                progress_bar.pack_forget()

            threading.Thread(target=process_image).start()

        crop_button = ctk.CTkButton(self, text='Crop Image', width=20, command=self.open_crop_popup)
        crop_button.pack(pady=10)

        self.frame_image = ctk.CTkFrame(self, width=600, height=400)
        self.frame_image.pack(padx=10)

        next_page_button = ctk.CTkButton(self, text='Next', width=130,
                                         command=self.next_page)
        next_page_button.pack(pady=5)

    def open_crop_popup(self):
        """
        Open crop app popup if an image is selected.
        """
        if not self.controller.img_file_path:
            messagebox.showerror("Error", "Please select an image first.")
        else:
            self.controller.popup_page_two()

    def next_page(self):
        """
        Proceed to the next page if an image is selected.
        """
        if not self.controller.img_file_path:
            messagebox.showerror("Error", "Please select an image first.")
        else:
            self.progress_bar = ctk.CTkProgressBar(self, mode='indeterminate')
            self.progress_bar.pack(pady=10)
            self.progress_bar.start()

            def ocr_extraction():
                # Start the OCR extraction process
                self.controller.frames[PageTwo].initialize_OCR_extraction(self.controller.img_file_path)

                # Stop the progress bar and switch to the second page
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.controller.show_frame(PageTwo)

            threading.Thread(target=ocr_extraction).start()


class CropPopup(ctk.CTkFrame):
    """
    Popup window for cropping the image.
    """

    def initialize_crop_app(self):
        """
        Initialize the CropApp for cropping the image.
        """
        if self.controller.img_file_path:
            self.crop_app = CropApp(self, self.controller.img_file_path, self.on_image_cropped)

    def on_image_cropped(self, cropped_image_path):
        """
        Handle image cropping event.
        """
        self.controller.show_frame(PageOne)
        self.controller.frames[PageOne].update_image(cropped_image_path)
        self.controller.img_file_path = cropped_image_path
        self.master.destroy()

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        self.crop_app = None

        if controller.img_file_path:
            self.initialize_crop_app()


class PageTwo(ctk.CTkFrame):
    """
    Second page of the application for displaying OCR-extracted data.
    """

    def initialize_OCR_extraction(self, img_file_path):
        """
        Initialize OCR extraction process.
        """
        if self.controller.img_file_path:
            self.img_file_path = img_file_path
            self.process_image_result = process_image(self.controller.img_file_path)
            self.populate_treeview_from_csv()
            self.display_image(img_file_path)

    def populate_treeview_from_csv(self):
        """
        Populate treeview with data from a CSV file.
        """
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
        """
        Display the image on the UI.
        """
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
        self.label = ctk.CTkLabel(self.frame_image, image=self.img, text="")
        self.label.place(x=frame_width / 2 - new_width / 2, y=frame_height / 2 - new_height / 2)

    def edit(self, event=None):
        """
        Edit the selected item in the treeview.
        """
        selected_item = self.treeview.selection()[0]
        nutrient_name = self.treeview.item(selected_item, 'values')[0]
        new_value = askstring("Edit Value", f"Enter new value for {nutrient_name}:")
        if new_value is not None:
            self.treeview.item(selected_item, values=(
                self.treeview.item(selected_item, 'values')[0], new_value,
                self.treeview.item(selected_item, 'values')[2]))

    def delete(self):
        """
        Delete the selected item from the treeview.
        """
        selected_item = self.treeview.selection()[0]
        self.treeview.delete(selected_item)

    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.label = None
        self.img = None
        self.img_file_path = None
        self.process_image_result = None
        self.controller = controller

        my_font = ('Times', 28, 'bold')
        page_2_label_1 = ctk.CTkLabel(self, text='NutriScan', width=30, font=my_font)
        page_2_label_1.pack()

        back_img = tk.PhotoImage(file="./assets/back.png")

        prev_page_button = ctk.CTkButton(self, image=back_img, text='Back', width=20,
                                         command=lambda: controller.show_frame(PageOne))
        prev_page_button.pack(side="top", pady=10)

        treeview_button_frame = ctk.CTkFrame(self)
        treeview_button_frame.pack(side="right", padx=20, pady=20)

        edit_img = tk.PhotoImage(file="./assets/edit.png")
        delete_img = tk.PhotoImage(file="./assets/delete.png")
        edit_btn = ctk.CTkButton(treeview_button_frame, image=edit_img, text="Edit", command=self.edit)
        del_btn = ctk.CTkButton(treeview_button_frame, image=delete_img, text="Delete", command=self.delete)
        edit_btn.pack(side="top", padx=5, pady=5)
        del_btn.pack(side="top", padx=5, pady=5)

        self.frame_image = ctk.CTkFrame(self, width=600, height=400)
        self.frame_image.pack(side="left", padx=20)

        frame_table = ctk.CTkFrame(self)
        frame_table.pack(side="top", fill='both', pady=10)

        self.style = ttk.Style()
        self.style.configure("Treeview",
                             background="#202120",
                             foreground="white",
                             fieldbackground="silver")

        self.treeview = ttk.Treeview(frame_table, columns=('Column1', 'Column2', 'Column3'), show='headings', height=30)
        self.treeview.heading('Column1', text='Nutrient', anchor='center')
        self.treeview.heading('Column2', text='Value (g)', anchor='center')
        self.treeview.heading('Column3', text='Confidence Score', anchor='center')

        self.treeview.column('Column1', anchor=tk.CENTER)
        self.treeview.column('Column2', anchor=tk.CENTER)
        self.treeview.column('Column3', anchor=tk.CENTER)

        self.treeview.bind("<Double-1>", self.edit)

        vsb = ctk.CTkScrollbar(frame_table, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=vsb.set)

        self.treeview.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def save_csv():
            """
            Save the treeview data to a CSV file.
            """
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
            """
            Export appended data from SQLite database to a CSV file.
            """
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
            """
            Append data to a CSV file and SQLite database.
            """
            if self.controller.img_file_path is None:
                messagebox.showerror("Error", "No image file selected.")
                return

            image_file_name = self.controller.original_file_name
            print(image_file_name)

            data = []
            for child in self.treeview.get_children():
                values = self.treeview.item(child, 'values')
                data.append(values)

            with open('nutritional_info.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Nutrient', 'Value', 'Confidence Score'])
                writer.writerows(data)

            df = pd.read_csv('nutritional_info.csv')
            column_order = ['Food label'] + df['Nutrient'].drop_duplicates().tolist()
            if 'Confidence' in df.columns:
                df = df.drop(columns=['Confidence'])

            df['Food label'] = image_file_name

            df = df.pivot_table(index='Food label', columns='Nutrient', values='Value', aggfunc='first')
            df.reset_index(inplace=True)

            df = df[column_order]
            conn = sqlite3.connect('nutrition_data.db')

            cur = conn.cursor()
            create_table_sql = f"CREATE TABLE IF NOT EXISTS nutrition_table ({', '.join([f'`{col}` TEXT' for col in df.columns])});"
            cur.execute(create_table_sql)
            conn.commit()

            query = f"SELECT * FROM nutrition_table WHERE `Food label` = '{image_file_name}'"
            existing_df = pd.read_sql_query(query, conn)

            if not existing_df.empty:
                # Convert both dataframes to the same data type before comparison
                existing_df = existing_df.astype(str)
                df = df.astype(str)

                if existing_df.equals(df):
                    messagebox.showwarning("Warning", "Data for this food label already exists in the CSV.")
                else:
                    df.to_sql('nutrition_table', conn, if_exists='append', index=False)
                    messagebox.showinfo("Success", "Data appended to CSV successfully!")
            else:
                df.to_sql('nutrition_table', conn, if_exists='append', index=False)
                messagebox.showinfo("Success", "Data appended to CSV successfully!")

            cur.close()
            conn.close()

        frame_buttons = ctk.CTkFrame(self)
        frame_buttons.pack(side="top", padx=5, pady=5)

        export_img = tk.PhotoImage(file="./assets/export.png")
        append_img = tk.PhotoImage(file="./assets/append.png")
        download_img = tk.PhotoImage(file="./assets/downloads.png")

        export_csv_btn = ctk.CTkButton(frame_buttons, image=export_img, text="Export CSV", command=save_csv)
        export_csv_btn.pack(side="left", padx=5)

        append_csv_btn = ctk.CTkButton(frame_buttons, image=append_img, text="Append CSV", command=append_csv)
        append_csv_btn.pack(side="left", padx=5)

        export_append_csv_btn = ctk.CTkButton(frame_buttons, image=download_img, text="Export Append CSV",
                                              command=export_appended_csv)
        export_append_csv_btn.pack(side="left", padx=5)


if __name__ == "__main__":
    app = NutriScanApp()
    app.mainloop()
