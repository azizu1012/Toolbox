import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from PIL import Image
import threading
import time
import os

class GifToAsciiConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("GIF to ASCII Art Converter")
        master.geometry("800x700")
        master.resizable(True, True)

        self.ascii_chars = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.', ' ']
        self.ascii_frames = []
        self.current_frame_index = 0
        self.animation_thread = None
        self.stop_animation_event = threading.Event()

        # --- Top Frame for Controls ---
        control_frame = tk.Frame(master, padx=10, pady=10)
        control_frame.pack(fill="x")

        tk.Label(control_frame, text="GIF File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.gif_path_entry = tk.Entry(control_frame, width=50)
        self.gif_path_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Browse", command=self.browse_gif).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(control_frame, text="ASCII Width:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ascii_width_scale = ttk.Scale(control_frame, from_=20, to=200, orient="horizontal", command=self.update_ascii_width)
        self.ascii_width_scale.set(80) # Default width
        self.ascii_width_scale.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.ascii_width_label = tk.Label(control_frame, text="80")
        self.ascii_width_label.grid(row=1, column=2, sticky="w", padx=5, pady=5)

        tk.Button(control_frame, text="Convert GIF", command=self.start_conversion, bg="#4CAF50", fg="white").grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

        # --- Animation Display Area ---
        tk.Label(master, text="ASCII Art Animation:").pack(anchor="w", padx=10, pady=(5,0))
        self.ascii_text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, font=("Consolas", 8), bg="#1E1E1E", fg="#F8F8F2", insertbackground="white")
        self.ascii_text_area.pack(fill="both", expand=True, padx=10, pady=5)
        self.ascii_text_area.config(state=tk.DISABLED)

        # --- Control Buttons for Animation ---
        anim_control_frame = tk.Frame(master, padx=10, pady=5)
        anim_control_frame.pack(fill="x")
        tk.Button(anim_control_frame, text="Play", command=self.play_animation).pack(side="left", padx=5)
        tk.Button(anim_control_frame, text="Stop", command=self.stop_animation).pack(side="left", padx=5)
        tk.Button(anim_control_frame, text="Save ASCII Frames (TXT)", command=self.save_ascii_frames_txt).pack(side="right", padx=5)
        # Nút mới để xuất thành mã Python
        tk.Button(anim_control_frame, text="Export as Python Code", command=self.export_ascii_frames_as_python).pack(side="right", padx=5)

    def update_ascii_width(self, val):
        self.ascii_width_label.config(text=f"{int(float(val))}")

    def browse_gif(self):
        file_path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif")])
        if file_path:
            self.gif_path_entry.delete(0, tk.END)
            self.gif_path_entry.insert(0, file_path)

    def get_char(self, pixel_value):
        """Chuyển đổi giá trị pixel (0-255) sang ký tự ASCII."""
        if pixel_value == 0:
            return ' '  # Ký tự cho màu đen
        return self.ascii_chars[pixel_value * len(self.ascii_chars) // 256]

    def convert_image_to_ascii_frame(self, image, new_width):
        """Chuyển đổi một ảnh PIL thành một khung hình ASCII art."""
        width, height = image.size
        aspect_ratio = height / width
        # Điều chỉnh hệ số 0.55 vì ký tự thường cao hơn rộng
        new_height = int(new_width * aspect_ratio * 0.55) 
        
        # Đảm bảo new_width và new_height không nhỏ hơn 1
        new_width = max(1, new_width)
        new_height = max(1, new_height)

        img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img = img.convert('L')  # Chuyển sang grayscale

        pixels = img.getdata()
        ascii_str = "".join([self.get_char(pixel) for pixel in pixels])

        ascii_art = ""
        for i in range(0, len(ascii_str), new_width):
            ascii_art += ascii_str[i:i + new_width] + "\n"
        return ascii_art

    def start_conversion(self):
        gif_path = self.gif_path_entry.get()
        if not gif_path or not os.path.exists(gif_path):
            messagebox.showerror("Error", "Please select a valid GIF file.")
            return

        ascii_width = int(self.ascii_width_scale.get())

        self.ascii_text_area.config(state=tk.NORMAL)
        self.ascii_text_area.delete(1.0, tk.END)
        self.ascii_text_area.insert(tk.END, "Converting GIF to ASCII frames...\n")
        self.ascii_text_area.config(state=tk.DISABLED)

        # Run conversion in a separate thread to keep GUI responsive
        conversion_thread = threading.Thread(target=self._run_conversion_thread, args=(gif_path, ascii_width))
        conversion_thread.start()

    def _run_conversion_thread(self, gif_path, ascii_width):
        self.ascii_frames = []
        try:
            img = Image.open(gif_path)
            for frame_num in range(img.n_frames):
                img.seek(frame_num)
                # Ensure we copy the image to prevent issues with future seek operations
                frame_image = img.copy() 
                ascii_frame = self.convert_image_to_ascii_frame(frame_image, new_width=ascii_width)
                self.ascii_frames.append(ascii_frame)
                
                # Update progress
                self.master.after(0, self.update_conversion_progress, frame_num + 1, img.n_frames)

            self.master.after(0, self.conversion_complete)
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Conversion Error", f"Error processing GIF: {e}"))
            self.master.after(0, self.conversion_complete) # Still call complete to re-enable buttons
            self.ascii_frames = [] # Clear frames on error

    def update_conversion_progress(self, current_frame, total_frames):
        self.ascii_text_area.config(state=tk.NORMAL)
        self.ascii_text_area.delete(1.0, tk.END)
        self.ascii_text_area.insert(tk.END, f"Converting frame {current_frame}/{total_frames}...\n")
        self.ascii_text_area.config(state=tk.DISABLED)

    def conversion_complete(self):
        if self.ascii_frames:
            self.ascii_text_area.config(state=tk.NORMAL)
            self.ascii_text_area.delete(1.0, tk.END)
            self.ascii_text_area.insert(tk.END, f"Conversion complete! {len(self.ascii_frames)} frames extracted.\n")
            self.ascii_text_area.config(state=tk.DISABLED)
            self.play_animation() # Auto-play after conversion
        else:
            self.ascii_text_area.config(state=tk.NORMAL)
            self.ascii_text_area.delete(1.0, tk.END)
            self.ascii_text_area.insert(tk.END, "Conversion failed or no frames found.\n")
            self.ascii_text_area.config(state=tk.DISABLED)

    def play_animation(self):
        self.stop_animation() # Stop any existing animation
        if not self.ascii_frames:
            messagebox.showinfo("Info", "No ASCII frames to play. Convert a GIF first.")
            return

        self.stop_animation_event.clear()
        self.current_frame_index = 0
        self.animation_thread = threading.Thread(target=self._run_animation_thread)
        self.animation_thread.start()

    def _run_animation_thread(self):
        while not self.stop_animation_event.is_set():
            if not self.ascii_frames: # Handle case where frames might be cleared during animation
                break 

            frame = self.ascii_frames[self.current_frame_index]
            
            self.ascii_text_area.config(state=tk.NORMAL)
            self.ascii_text_area.delete(1.0, tk.END) # Clear previous frame
            self.ascii_text_area.insert(tk.END, frame)
            self.ascii_text_area.see(tk.END)
            self.ascii_text_area.config(state=tk.DISABLED)
            self.master.update_idletasks() # Update GUI immediately

            self.current_frame_index = (self.current_frame_index + 1) % len(self.ascii_frames)
            time.sleep(0.1) # Control animation speed (adjust as needed)

    def stop_animation(self):
        self.stop_animation_event.set()
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=0.5) # Give it a little time to stop

    def save_ascii_frames_txt(self):
        if not self.ascii_frames:
            messagebox.showinfo("Info", "No ASCII frames to save. Convert a GIF first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    for i, frame in enumerate(self.ascii_frames):
                        f.write(f"--- FRAME {i+1} ---\n")
                        f.write(frame)
                        f.write("\n\n")
                messagebox.showinfo("Success", f"ASCII frames saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save frames: {e}")

    def export_ascii_frames_as_python(self):
        if not self.ascii_frames:
            messagebox.showinfo("Info", "No ASCII frames to export. Convert a GIF first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("# This file contains ASCII art frames generated from a GIF.\n")
                    f.write("# You can copy and paste the content of 'YOUR_ASCII_ANIMATION_FRAMES' \n")
                    f.write("# directly into your main Python script.\n\n")
                    f.write("YOUR_ASCII_ANIMATION_FRAMES = [\n")
                    for frame in self.ascii_frames:
                        # Sử dụng triple quotes để xử lý các khung hình nhiều dòng dễ dàng
                        f.write(f'    """\n{frame.strip()}\n    """,\n')
                    f.write("]\n")
                messagebox.showinfo("Success", f"ASCII frames exported as Python code to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export frames as Python code: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GifToAsciiConverterGUI(root)
    root.mainloop()