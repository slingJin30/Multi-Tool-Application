import os
import subprocess
import logging
from tkinter import Tk, Label, Button, Entry, StringVar, filedialog, ttk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("application.log"),
        logging.StreamHandler()
    ]
)

class MultiToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Tool Application")

        # Initialize variables
        self.link_var = StringVar()
        self.output_dir = StringVar()
        self.output_dir.set(os.getcwd())

        # Layout
        Label(root, text="YouTube URL:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        Entry(root, textvariable=self.link_var, width=50).grid(row=0, column=1, padx=10, pady=5)

        Label(root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        Entry(root, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=10, pady=5)
        Button(root, text="Browse", command=self.browse_directory).grid(row=1, column=2, padx=5, pady=5)

        Button(root, text="Download Audio", command=self.download_audio).grid(row=2, column=0, padx=10, pady=10)
        Button(root, text="Download Video", command=self.download_video).grid(row=2, column=1, padx=10, pady=10)
        Button(root, text="Batch Process", command=self.batch_process).grid(row=2, column=2, padx=10, pady=10)

        Label(root, text="File Conversion:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        Button(root, text="Convert Files", command=self.convert_files).grid(row=3, column=1, padx=10, pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def download_audio(self):
        url = self.link_var.get()
        output_path = self.output_dir.get()
        if url:
            self.run_command([
                'yt-dlp', '-x', '--audio-format', 'mp3', '-o', os.path.join(output_path, '%(title)s.%(ext)s'), url
            ])

    def download_video(self):
        url = self.link_var.get()
        output_path = self.output_dir.get()
        if url:
            self.run_command([
                'yt-dlp', '-f', 'bestvideo+bestaudio[ext=m4a]/best', '-o', os.path.join(output_path, '%(title)s.%(ext)s'), url
            ])

    def batch_process(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        output_path = self.output_dir.get()
        if file_path:
            with open(file_path, 'r') as file:
                links = [line.strip() for line in file if line.strip()]
            self.progress["maximum"] = len(links)
            for i, link in enumerate(links, start=1):
                self.download_audio() if link else None
                self.progress["value"] = i
                self.root.update_idletasks()

    def convert_files(self):
        source_dir = filedialog.askdirectory(title="Select Source Directory")
        target_dir = filedialog.askdirectory(title="Select Target Directory")
        if source_dir and target_dir:
            files = [f for f in os.listdir(source_dir) if f.endswith((".mp4", ".mkv"))]
            self.progress["maximum"] = len(files)
            for i, file in enumerate(files, start=1):
                input_file = os.path.join(source_dir, file)
                output_file = os.path.join(target_dir, os.path.splitext(file)[0] + ".mp3")
                self.run_command([
                    'ffmpeg', '-i', input_file, '-q:a', '0', '-map', 'a', output_file
                ])
                self.progress["value"] = i
                self.root.update_idletasks()

    def run_command(self, command):
        try:
            subprocess.run(command, check=True)
            logging.info(f"Command succeeded: {' '.join(command)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {e}")

if __name__ == "__main__":
    root = Tk()
    app = MultiToolApp(root)
    root.mainloop()
