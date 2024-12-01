import tkinter as tk 
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os
import re

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.url = None
        self.full_output = []  # Store complete output
        
        # Configure root window
        self.root.geometry("1280x720")
        self.root.minsize(1024, 600)
        
        # Top Frame
        top_frame = ttk.Frame(root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # URL Entry
        ttk.Label(top_frame, text="Video URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(top_frame, width=80)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        
        # List Formats Button
        self.list_button = ttk.Button(top_frame, text="List Formats", command=self.list_formats)
        self.list_button.pack(side=tk.LEFT, padx=5)

        # MP4 Only Checkbutton - 设置默认为True
        self.mp4_only = tk.BooleanVar(value=True)  # 修改这里，设置默认值为True
        self.mp4_check = ttk.Checkbutton(
            top_frame, 
            text="Show MP4 only", 
            variable=self.mp4_only,
            command=self.refresh_format_display
        )
        self.mp4_check.pack(side=tk.LEFT, padx=5)
        
        # Format List Display (Treeview)
        columns = ('id', 'codec', 'resolution', 'size', 'extra')
        self.format_display = ttk.Treeview(root, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.format_display.heading('id', text='ID')
        self.format_display.heading('codec', text='Codec')
        self.format_display.heading('resolution', text='Resolution')
        self.format_display.heading('size', text='Size')
        self.format_display.heading('extra', text='Additional Info')
        
        # Set column widths
        self.format_display.column('id', width=80, anchor='center')
        self.format_display.column('codec', width=100, anchor='center')
        self.format_display.column('resolution', width=120, anchor='center')
        self.format_display.column('size', width=100, anchor='center')
        self.format_display.column('extra', width=300)
        
        # Bind selection event
        self.format_display.bind('<<TreeviewSelect>>', self.on_select)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.format_display.yview)
        self.format_display.configure(yscrollcommand=scrollbar.set)
        
        # Pack the Treeview and scrollbar
        self.format_display.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom Frame
        self.bottom_frame = ttk.Frame(root, padding="10")
        self.bottom_frame.pack(fill=tk.X)
        self.bottom_frame.pack_forget()
        
        # Video ID Entry and Download Button
        id_frame = ttk.Frame(self.bottom_frame)
        id_frame.pack(fill=tk.X)
        
        ttk.Label(id_frame, text="Video ID:").pack(side=tk.LEFT)
        self.id_entry = ttk.Entry(id_frame, width=10)
        self.id_entry.pack(side=tk.LEFT, padx=5)
        
        self.download_button = ttk.Button(id_frame, text="Download", command=self.download_video)
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        # Progress Frame
        progress_frame = ttk.Frame(self.bottom_frame)
        progress_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            length=300,
            mode='determinate', 
            variable=self.progress_var
        )
        self.progress_bar.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        labels_frame = ttk.Frame(progress_frame)
        labels_frame.pack(side=tk.LEFT, padx=5)
        
        self.percent_label = ttk.Label(labels_frame, text="0%")
        self.percent_label.pack(anchor=tk.W)
        
        self.size_label = ttk.Label(labels_frame, text="0 MB / 0 MB")
        self.size_label.pack(anchor=tk.W)
        
        self.speed_label = ttk.Label(labels_frame, text="0 MB/s")
        self.speed_label.pack(anchor=tk.W)
        
        self.status_label = ttk.Label(root, text="")
        self.status_label.pack(pady=5)

    def parse_format_line(self, line):
        """Parse a format line from yt-dlp output and extract relevant information."""
        if not line.strip() or '[info]' in line or 'Available formats' in line:
            return None
            
        # Regular expressions for extracting information
        id_match = re.match(r'\s*(\d+)\s+', line)
        codec_match = re.search(r'(\w+)\s*\d+x\d+|(\w+)\s*\(', line)
        resolution_match = re.search(r'(\d+x\d+|\d+p)', line)
        size_match = re.search(r'~?\s*(\d+\.?\d*\s*[KMG]iB)', line)
        
        if id_match:
            video_id = id_match.group(1)
            codec = codec_match.group(1) if codec_match and codec_match.group(1) else \
                   codec_match.group(2) if codec_match and codec_match.group(2) else "N/A"
            resolution = resolution_match.group(1) if resolution_match else "N/A"
            size = size_match.group(1) if size_match else "N/A"
            
            # Everything else goes into extra
            extra = line.strip()
            for matched in [video_id, codec, resolution, size]:
                if matched and matched in extra:
                    extra = extra.replace(matched, "").strip()
            
            return {
                'id': video_id,
                'codec': codec,
                'resolution': resolution,
                'size': size,
                'extra': extra
            }
        return None

    def should_show_line(self, parsed_data):
        if not parsed_data:
            return False
        if self.mp4_only.get():
            return 'mp4' in parsed_data['codec'].lower()
        return True
        
    def on_select(self, event):
        """Handle treeview selection event"""
        selected_items = self.format_display.selection()
        if selected_items:
            item = selected_items[0]
            video_id = self.format_display.item(item)['values'][0]
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, str(video_id))

    def refresh_format_display(self):
        # Clear current display
        for item in self.format_display.get_children():
            self.format_display.delete(item)
            
        # Show filtered or full output
        for line in self.full_output:
            parsed_data = self.parse_format_line(line)
            if parsed_data and self.should_show_line(parsed_data):
                # Insert the item with all its values
                self.format_display.insert('', 'end', values=(
                    parsed_data['id'],
                    parsed_data['codec'],
                    parsed_data['resolution'],
                    parsed_data['size'],
                    parsed_data['extra']
                ))

    def list_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.config(text="Please enter a URL", foreground="red")
            return
            
        self.url = url
        self.list_button.config(state="disabled")
        for item in self.format_display.get_children():
            self.format_display.delete(item)
        self.status_label.config(text="Getting format list...", foreground="black")
        self.full_output = []
        
        self.bottom_frame.pack(fill=tk.X)
        command = f'yt-dlp -F "{url}"'
        
        def callback(output):
            self.full_output.append(output)
            parsed_data = self.parse_format_line(output)
            if parsed_data and self.should_show_line(parsed_data):
                self.format_display.insert('', 'end', values=(
                    parsed_data['id'],
                    parsed_data['codec'],
                    parsed_data['resolution'],
                    parsed_data['size'],
                    parsed_data['extra']
                ))
            
        self.run_command(command, callback)

    def reset_progress(self):
        self.progress_var.set(0)
        self.percent_label.config(text="0%")
        self.size_label.config(text="0 MB / 0 MB")
        self.speed_label.config(text="0 MB/s")

    def parse_progress(self, line):
        try:
            percent_match = re.search(r"(\d+\.?\d*)%", line)
            size_match = re.search(r"of\s+(\d+\.?\d*)(Mi?B|Ki?B|Gi?B)", line)
            speed_match = re.search(r"at\s+(\d+\.?\d*)(Mi?B|Ki?B|Gi?B)/s", line)
            
            if percent_match:
                percent = float(percent_match.group(1))
                self.progress_var.set(percent)
                self.percent_label.config(text=f"{percent:.1f}%")
            
            if size_match:
                size = float(size_match.group(1))
                unit = size_match.group(2)
                if unit.startswith('K'):
                    size /= 1024
                elif unit.startswith('G'):
                    size *= 1024
                total_mb = f"{size:.2f} MB"
                current_mb = f"{size * (self.progress_var.get() / 100):.2f} MB"
                self.size_label.config(text=f"{current_mb} / {total_mb}")
            
            if speed_match:
                speed = float(speed_match.group(1))
                unit = speed_match.group(2)
                if unit.startswith('K'):
                    speed /= 1024
                elif unit.startswith('G'):
                    speed *= 1024
                self.speed_label.config(text=f"{speed:.2f} MB/s")
                
        except Exception as e:
            print(f"Error parsing progress: {e}")

    def run_command(self, command, callback, capture_output=True):
        def thread_target():
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    shell=True,
                    bufsize=1
                )
                
                if capture_output:
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                        if line:
                            if "[download]" in line:
                                self.parse_progress(line)
                            callback(line)
                else:
                    process.wait()
                
                if process.returncode == 0:
                    self.status_label.config(text="Operation completed successfully", foreground="green")
                else:
                    stderr = process.stderr.read() if process.stderr else "Unknown error"
                    self.status_label.config(text=f"Error: {stderr}", foreground="red")
            except Exception as e:
                self.status_label.config(text=f"Error: {str(e)}", foreground="red")
            finally:
                self.list_button.config(state="normal")
                self.download_button.config(state="normal")
                
        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()

    def download_video(self):
        video_id = self.id_entry.get().strip()
        if not video_id or not self.url:
            self.status_label.config(text="Please enter a video ID", foreground="red")
            return
            
        self.download_button.config(state="disabled")
        self.status_label.config(text="Downloading...", foreground="black")
        self.reset_progress()
        
        command = f'yt-dlp -f "{video_id}[ext=mp4]+bestaudio[ext=m4a]" "{self.url}"'
        
        def callback(output):
            if "[download]" in output:
                parsed_data = self.parse_format_line(output)
                if parsed_data:
                    self.format_display.insert('', 'end', values=(
                        parsed_data['id'],
                        parsed_data['codec'],
                        parsed_data['resolution'],
                        parsed_data['size'],
                        parsed_data['extra']
                    ))
            
        self.run_command(command, callback)

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()