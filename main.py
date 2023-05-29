import os
import random
import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageTk, Image
from datetime import datetime
from threading import Thread

class SlideshowConfig:
    def __init__(self, folder_path, interval, num_photos):
        self.folder_path = folder_path
        self.interval = interval
        self.num_photos = num_photos


class ImageSlider:
    def __init__(self, root):
        self.root = root
        self.images = []
        self.current_image = None
        self.interval = 2000  # Default interval in milliseconds
        self.num_photos = 20
        self.slideshow_queue = []
        self.displayed_sets = []
        self.export_folder = os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(self.export_folder, 'photos\wut-logo-196733998.png')  # Path to logo image
        self.total_time = 0  # Total time for all intervals in the queue

        self.setup_gui()

    def setup_gui(self):
        self.root.title("Road sign image visualizer")
        self.root.geometry("800x410")
        
        # Changing icon of the window
        self.icon = tk.PhotoImage(file=os.path.join(self.export_folder, 'photos\icon.png'))
        self.root.iconphoto(True, self.icon)

        # Top left logo placeholder
        logo_frame = ttk.Frame(self.root)
        logo_frame.grid(row=0, column=0, padx=1, pady=1, sticky=tk.NW)
        self.logo_image = self.resize_image(self.logo_path, (100, 100))
        logo_label = ttk.Label(logo_frame, image=self.logo_image)
        logo_label.pack()

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=1, rowspan=1, sticky=tk.NSEW)

        folder_label = ttk.Label(main_frame, text="Select Image Folder:")
        folder_label.grid(row=0, column=0, sticky=tk.E)

        folder_frame = ttk.Frame(main_frame, padding=(0, 5))
        folder_frame.grid(row=0, column=1, columnspan=8, sticky=tk.EW)

        self.folder_entry = ttk.Entry(folder_frame, state="readonly", width=80)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        folder_button = ttk.Button(folder_frame, text="Browse", command=self.select_folder)
        folder_button.pack(side=tk.LEFT)

        export_label = ttk.Label(main_frame, text="CSV Export Folder:")
        export_label.grid(row=1, column=0, sticky=tk.E)

        export_frame = ttk.Frame(main_frame, padding=(0, 5))
        export_frame.grid(row=1, column=1, columnspan=8, sticky=tk.EW)

        self.export_entry = ttk.Entry(export_frame, state="readonly", width=80)
        self.export_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.export_entry.insert(0, self.export_folder)

        export_button = ttk.Button(export_frame, text="Change", command=self.select_export_folder)
        export_button.pack(side=tk.LEFT)

        interval_label = ttk.Label(main_frame, text="Interval (in milliseconds):")
        interval_label.grid(row=4, column=1, sticky=tk.E)

        self.interval_entry = ttk.Entry(main_frame, width=6)
        self.interval_entry.grid(row=4, column=2, sticky=tk.S)
        self.interval_entry.insert(0, str(self.interval))

        num_photos_label = ttk.Label(main_frame, text="Number of Photos:")
        num_photos_label.grid(row=4, column=3, sticky=tk.E)

        self.num_photos_entry = ttk.Entry(main_frame, width=6)
        self.num_photos_entry.grid(row=4, column=4, sticky=tk.S)
        self.num_photos_entry.insert(0, str(self.num_photos))

        add_button = ttk.Button(main_frame, text="Add to Queue", command=self.add_to_queue, width=30)
        add_button.grid(row=6, column=0, columnspan=8, sticky=tk.NSEW, pady=(10, 0))

        queue_label = ttk.Label(main_frame, text="Slideshow Queue:")
        queue_label.grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

        self.queue_listbox = tk.Listbox(main_frame)
        self.queue_listbox.grid(row=8, column=0, columnspan=8, rowspan=5, sticky=tk.NSEW, pady=(0, 10))
        queue_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.queue_listbox.yview)
        queue_scrollbar.grid(row=8, column=8, rowspan=5, sticky=tk.NS)
        self.queue_listbox.config(yscrollcommand=queue_scrollbar.set)

        start_button = ttk.Button(main_frame, text="Start", command=self.start_slideshow)
        start_button.grid(row=13, column=0, sticky=tk.W, pady=(10, 0))

        exit_button = ttk.Button(main_frame, text="Exit", command=self.exit_program)
        exit_button.grid(row=13, column=7, sticky=tk.E, pady=(10, 0))

        self.timer_label = ttk.Label(main_frame, text="Total Time: 00:00:00")
        self.timer_label.grid(row=14, column=0, columnspan=8, pady=(10, 0))

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_path)
            self.folder_entry.configure(state="readonly")

            self.load_images(folder_path)

    def select_export_folder(self):
        export_folder = filedialog.askdirectory()
        if export_folder:
            self.export_folder = export_folder
            self.export_entry.configure(state="normal")
            self.export_entry.delete(0, tk.END)
            self.export_entry.insert(0, export_folder)
            self.export_entry.configure(state="readonly")

    def resize_image(self, image_path, size):
        image = Image.open(image_path)
        image = image.resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        return photo

    def load_images(self, folder_path):
        self.images = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(folder_path, filename)
                self.images.append(image_path)

        if not self.images:
            messagebox.showwarning("No Images", "No images found in the selected folder.")
            return

    def add_to_queue(self):
        folder_path = self.folder_entry.get()
        interval = self.interval_entry.get().strip()
        num_photos_str = self.num_photos_entry.get().strip()

        if not folder_path:
            messagebox.showerror("Invalid Folder", "Please select a folder.")
            return

        if not interval.isdigit():
            messagebox.showerror("Invalid Interval", "Please enter a valid numeric interval.")
            return

        if num_photos_str:
            if not num_photos_str.isdigit():
                messagebox.showerror("Invalid Number of Photos", "Please enter a valid numeric value for the number of photos.")
                return
            num_photos = int(num_photos_str)
        else:
            num_photos = None

        config = SlideshowConfig(folder_path, interval, num_photos)
        self.slideshow_queue.append(config)

        self.queue_listbox.insert(tk.END, f"{folder_path} (Interval: {interval}ms, Photos: {num_photos_str})")

        self.clear_inputs()

        # Update total time
        self.total_time += int(interval) / 1000  # Convert interval to seconds

        # Update timer label
        self.update_timer_label()

    def clear_inputs(self):
        self.folder_entry.configure(state="normal")
        self.folder_entry.delete(0, tk.END)
        self.interval_entry.delete(0, tk.END)
        self.num_photos_entry.delete(0, tk.END)

    def start_slideshow(self):
        if not self.slideshow_queue:
            messagebox.showwarning("Empty Queue", "The slideshow queue is empty.")
            return

        self.root.withdraw()

        self.slideshow_window = tk.Toplevel(self.root)
        self.slideshow_window.attributes('-fullscreen', True)
        self.slideshow_window.protocol("WM_DELETE_WINDOW", self.on_slideshow_close)

        self.slideshow_label = ttk.Label(self.slideshow_window)
        self.slideshow_label.pack(fill=tk.BOTH, expand=True)

        self.perform_next_slideshow()

    def perform_next_slideshow(self):
        if not self.slideshow_queue:
            self.stop_slideshow()
            self.export_displayed_sets()
            self.queue_listbox.delete(0, tk.END)  # Clear the queue from the GUI
            return

        config = self.slideshow_queue.pop(0)

        folder_path = config.folder_path
        interval = config.interval
        num_photos = config.num_photos

        self.load_images(folder_path)

        if not self.images:
            messagebox.showwarning("No Images", f"No images found in the folder: {folder_path}. Skipping to the next slideshow.")
            self.perform_next_slideshow()
            return

        self.interval = interval
        self.num_photos = num_photos

        self.show_next_image()

    def show_next_image(self):
        if not self.images:
            self.perform_next_slideshow()
            return

        if self.num_photos is not None and self.num_photos <= 0:
            self.perform_next_slideshow()
            return

        random_image = random.choice(self.images)
        image = Image.open(random_image)
        image = image.resize((self.slideshow_window.winfo_screenwidth(), self.slideshow_window.winfo_screenheight()), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        self.slideshow_label.configure(image=photo)
        self.slideshow_label.image = photo

        self.current_image = random_image

        if self.num_photos is not None:
            self.num_photos -= 1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        display_time = datetime.now().strftime("%H:%M:%S")
        image_filename = os.path.basename(random_image)
        parent_folder = os.path.basename(os.path.dirname(random_image))

        interval_seconds = int(self.interval) // 1000  # Convert interval to seconds
        self.displayed_sets.append([display_time, image_filename, interval_seconds, parent_folder])

        self.slideshow_window.after(int(self.interval), self.show_next_image)  # Convert interval to milliseconds


    def stop_slideshow(self):
        if self.slideshow_window:
            self.slideshow_window.destroy()
            self.slideshow_window = None

        self.root.deiconify()

    def on_slideshow_close(self):
        result = messagebox.askyesno("Confirm Exit", "Are you sure you want to stop the slideshow?")
        if result:
            self.stop_slideshow()

    def export_displayed_sets(self):
        if not self.displayed_sets:
            return

        export_folder = self.export_folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"displayed_sets_{timestamp}.csv"
        file_path = os.path.join(export_folder, file_name)

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Display Time', 'Image Filename', 'Interval (s)', 'Parent Folder'])
            writer.writerows(self.displayed_sets)

        messagebox.showinfo("Export Successful", f"The displayed sets have been exported to: {file_path}")

    def exit_program(self):
        result = messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?")
        if result:
            self.root.destroy()
    
    def update_timer_label(self):
        total_time_str = self.format_time(self.total_time)
        self.timer_label.configure(text=f"Total Time: {total_time_str}")

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSlider(root)
    root.mainloop()
