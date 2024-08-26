import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfMerger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger")
        self.pdf_files = []
        self.watched_directory = None

        # Setup GUI components
        self.setup_ui()

    def setup_ui(self):
        # Frame for the listbox and scrollbar
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Listbox for displaying PDFs
        self.listbox = tk.Listbox(frame, selectmode=tk.SINGLE, height=15, width=50, bg="white")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        watch_button = tk.Button(button_frame, text="Watch Directory", command=self.watch_directory)
        watch_button.pack(side=tk.LEFT, padx=5)

        remove_button = tk.Button(button_frame, text="Remove Selected", command=self.remove_selected)
        remove_button.pack(side=tk.LEFT, padx=5)

        move_up_button = tk.Button(button_frame, text="Move Up", command=self.move_up)
        move_up_button.pack(side=tk.LEFT, padx=5)

        move_down_button = tk.Button(button_frame, text="Move Down", command=self.move_down)
        move_down_button.pack(side=tk.LEFT, padx=5)

        merge_button = tk.Button(button_frame, text="Merge PDFs", command=self.merge_pdfs)
        merge_button.pack(side=tk.LEFT, padx=5)

        # Checkbox for deleting files after merge
        self.delete_after_merge_var = tk.BooleanVar()
        delete_checkbutton = tk.Checkbutton(self.root, text="Delete files after merging", variable=self.delete_after_merge_var)
        delete_checkbutton.pack(pady=5)

    def watch_directory(self):
        directory = filedialog.askdirectory()
        if not directory:
            return

        self.watched_directory = directory
        self.start_watching(directory)

    def start_watching(self, directory):
        event_handler = PDFDirectoryEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=directory, recursive=False)
        observer.start()

        # Load initial PDF files from the directory
        self.load_pdfs_from_directory(directory)

    def load_pdfs_from_directory(self, directory):
        self.pdf_files.clear()
        self.listbox.delete(0, tk.END)
        for filename in os.listdir(directory):
            if filename.endswith(".pdf"):
                file_path = os.path.join(directory, filename)
                self.pdf_files.append(file_path)
                self.listbox.insert(tk.END, filename)

    def add_pdf(self, file_path):
        if file_path not in self.pdf_files:
            self.pdf_files.append(file_path)
            self.listbox.insert(tk.END, os.path.basename(file_path))

    def remove_pdf(self, file_path):
        if file_path in self.pdf_files:
            index = self.pdf_files.index(file_path)
            self.pdf_files.remove(file_path)
            self.listbox.delete(index)

    def remove_selected(self):
        selected_indices = list(self.listbox.curselection())
        for index in reversed(selected_indices):
            self.pdf_files.pop(index)  # Remove from list
            self.listbox.delete(index)  # Remove from listbox

    def move_up(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        if index > 0:
            # Swap in the list
            self.pdf_files[index], self.pdf_files[index - 1] = self.pdf_files[index - 1], self.pdf_files[index]
            # Update Listbox
            self.update_listbox()

    def move_down(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
        index = selected_index[0]
        if index < len(self.pdf_files) - 1:
            # Swap in the list
            self.pdf_files[index], self.pdf_files[index + 1] = self.pdf_files[index + 1], self.pdf_files[index]
            # Update Listbox
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)  # Clear current Listbox
        for file_path in self.pdf_files:
            self.listbox.insert(tk.END, os.path.basename(file_path))

    def merge_pdfs(self):
        if not self.pdf_files:
            messagebox.showwarning("No PDFs", "No PDFs to merge.")
            return

        # Define the output file path
        output_file = os.path.join(os.getcwd(), "Output_Merge.pdf")

        # Merge the PDFs in the order they appear in the list
        merger = PdfMerger()
        for pdf_file in self.pdf_files:
            merger.append(pdf_file)

        merger.write(output_file)
        merger.close()

        messagebox.showinfo("Success", f"Merged PDF saved to {output_file}")

        # Check if we need to delete the files
        if self.delete_after_merge_var.get():
            self.delete_files()

    def delete_files(self):
        for pdf_file in self.pdf_files:
            try:
                os.remove(pdf_file)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file {pdf_file}: {str(e)}")

        self.pdf_files.clear()  # Clear the list
        self.update_listbox()   # Update the Listbox

class PDFDirectoryEventHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            self.app.add_pdf(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            self.app.remove_pdf(event.src_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()
