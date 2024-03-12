import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from CropApp import CropApp
from tkinterdnd2 import DND_FILES, TkinterDnD


class NutriScanApp(TkinterDnD.Tk):
    def __init__(self, *args, **kwargs):
        TkinterDnD.Tk.__init__(self, *args, **kwargs)
        self.geometry("700x500")
        self.title('NutriScan')
        self.img_file_path = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>",
                        lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        container = tk.Frame(self.canvas)

        self.frames = {}

        for F in (PageOne, PageTwo, PageThree):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PageOne)
        self.canvas.create_window((0, 0), window=container, anchor="nw")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if cont == PageTwo:
            frame.initialize_crop_app()

        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        my_font1 = ('times', 18, 'bold')
        Heading = tk.Label(self, text='NutriScan', width=30, font=my_font1)
        Heading.grid(row=0, column=0, columnspan=2)

        my_font2 = ('Ariel', 14, 'bold')
        lable_1 = tk.Label(self, text='Upload the Nutritional label', width=30, font=my_font2)
        lable_1.grid(row=1, column=0, columnspan=2)

        entry = tk.Text(self, height=3, width=30)
        entry.configure(state='normal')
        entry.insert(1.0, "Drag and Drop files here")
        entry.configure(state='disabled')

        entry.drop_target_register(DND_FILES)
        entry.dnd_bind('<<Drop>>', lambda e: open_image(e.data))

        entry.grid(row=2, column=0, columnspan=2)

        my_font3 = ('Ariel', 14, 'bold')
        label_2 = tk.Label(self, text='OR', width=30, font=my_font3)
        label_2.grid(row=3, column=0, columnspan=2)

        upload_file_button = tk.Button(self, text='Upload File', width=20, command=lambda: upload_file())
        upload_file_button.grid(row=4, column=0, columnspan=2)

        def upload_file():
            global img
            global filename
            f_types = [('Image Files', '*.png *.jpg *.jpeg *.gif')]
            filename = filedialog.askopenfilename(filetypes=f_types)
            if filename:
                open_image(filename)

        def open_image(filename):
            global img
            filename = filename.strip('{}')
            img = Image.open(filename)
            width, height = img.size
            width_new = int(width / 3)
            height_new = int(height / 3)
            img_resized = img.resize((width_new, height_new))
            img = ImageTk.PhotoImage(img_resized)
            l2 = tk.Label(self, image=img)
            l2.grid(row=3, column=0, columnspan=2)
            controller.img_file_path = filename
            controller.show_frame(PageOne)

        next_page_button = tk.Button(self, text='Next', width=20, command=lambda: controller.show_frame(PageTwo))
        next_page_button.grid(row=5, column=0, columnspan=2)


class PageTwo(tk.Frame):
    def initialize_crop_app(self):
        if self.controller.img_file_path:
            self.crop_app = CropApp(self, self.controller.img_file_path)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        my_font = ('Ariel', 18, 'bold')
        page_2_label_1 = tk.Label(self, text='Page 2', width=30, font=my_font)
        page_2_label_1.grid(row=0, column=0, columnspan=2)

        self.crop_app = None

        if controller.img_file_path:
            self.crop_app = CropApp(self, controller.img_file_path)

        prev_page_button = tk.Button(self, text='Back', width=20, command=lambda: controller.show_frame(PageOne))
        prev_page_button.grid(row=1, column=0, columnspan=2)

        next_page_button = tk.Button(self, text='Next', width=20, command=lambda: controller.show_frame(PageThree))
        next_page_button.grid(row=2, column=0, columnspan=2)


class PageThree(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        my_font = ('Ariel', 18, 'bold')
        page_2_label_1 = tk.Label(self, text='Page 3', width=30, font=my_font)
        page_2_label_1.grid(row=0, column=0, columnspan=2)

        prev_page_button = tk.Button(self, text='Back', width=20, command=lambda: controller.show_frame(PageTwo))
        prev_page_button.grid(row=5, column=0, columnspan=2)


if __name__ == "__main__":
    app = NutriScanApp()
    app.mainloop()
