import os
import tkinter as tk
from PIL import Image
from tkinter import Tk, filedialog, messagebox, Label, Button, Entry, StringVar, ttk
import threading
import ctypes # Thêm import ctypes cho SetProcessDpiAwareness

class ImageToICOConverter:
    def __init__(self, master):
        self.master = master
        master.title("Chuyển đổi ảnh sang ICO")
        master.geometry("550x380") # Tăng kích thước cửa sổ để chứa thêm nút
        master.resizable(False, False)

        # Cấu hình phong cách
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=5)
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 10))

        # Nhãn và nút chọn file ảnh đầu vào
        self.input_label = ttk.Label(master, text="Chọn file ảnh (.jpg, .png, .bmp, ...):")
        self.input_label.pack(pady=(10,0)) # Giảm khoảng cách trên

        self.input_path_var = StringVar()
        self.input_entry = ttk.Entry(master, textvariable=self.input_path_var, width=60)
        self.input_entry.pack(pady=5)

        self.browse_input_button = ttk.Button(master, text="Duyệt ảnh...", command=self.browse_input_file)
        self.browse_input_button.pack(pady=5)

        # Nhãn và trường nhập tên file ICO đầu ra
        self.output_name_label = ttk.Label(master, text="Nhập tên file ICO đầu ra (ví dụ: icon_moi.ico):")
        self.output_name_label.pack(pady=(10,0))

        self.output_name_var = StringVar()
        self.output_name_entry = ttk.Entry(master, textvariable=self.output_name_var, width=60)
        self.output_name_entry.pack(pady=5)
        self.output_name_var.set("output.ico") # Giá trị mặc định

        # === THÊM MỚI: Nhãn và nút chọn thư mục đầu ra ===
        self.output_dir_label = ttk.Label(master, text="Chọn thư mục lưu file ICO:")
        self.output_dir_label.pack(pady=(10,0))

        self.output_dir_var = StringVar()
        self.output_dir_entry = ttk.Entry(master, textvariable=self.output_dir_var, width=60)
        self.output_dir_entry.pack(pady=5)
        self.output_dir_var.set(os.getcwd()) # Mặc định là thư mục hiện tại

        self.browse_output_dir_button = ttk.Button(master, text="Duyệt thư mục...", command=self.browse_output_directory)
        self.browse_output_dir_button.pack(pady=5)
        # =================================================

        # Nút chuyển đổi
        self.convert_button = ttk.Button(master, text="Chuyển đổi sang ICO", command=self.start_conversion_thread)
        self.convert_button.pack(pady=15)

        # Nhãn trạng thái
        self.status_label = tk.Label(master, text="", font=("Arial", 10, "italic"))
        self.status_label.pack(pady=5)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file ảnh",
            filetypes=[("Tất cả các loại ảnh", "*.jpg *.jpeg *.png *.bmp *.gif"),
                       ("JPEG files", "*.jpg"),
                       ("PNG files", "*.png"),
                       ("BMP files", "*.bmp"),
                       ("GIF files", "*.gif")]
        )
        if file_path:
            self.input_path_var.set(file_path)
            # Gợi ý tên file đầu ra dựa trên tên file đầu vào
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            self.output_name_var.set(name_without_ext + ".ico")

    # === THÊM MỚI: Hàm để duyệt thư mục đầu ra ===
    def browse_output_directory(self):
        dir_path = filedialog.askdirectory(
            title="Chọn thư mục lưu icon"
        )
        if dir_path:
            self.output_dir_var.set(dir_path)
    # ============================================

    def convert_image_to_ico(self):
        input_file = self.input_path_var.get()
        output_name = self.output_name_var.get() # Lấy chỉ tên file
        output_directory = self.output_dir_var.get() # Lấy thư mục đầu ra

        if not input_file:
            self.update_status("Vui lòng chọn file ảnh đầu vào.", "red")
            return

        if not output_name:
            self.update_status("Vui lòng nhập tên file ICO đầu ra.", "red")
            return
        
        if not output_directory:
            self.update_status("Vui lòng chọn thư mục lưu file ICO.", "red")
            return

        # Đảm bảo phần mở rộng là .ico cho tên file
        if not output_name.lower().endswith(".ico"):
            output_name += ".ico"
            
        # Tạo đường dẫn đầy đủ cho file đầu ra
        full_output_path = os.path.join(output_directory, output_name)

        try:
            img = Image.open(input_file)
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Các kích thước phổ biến cho icon
            sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # Lưu ảnh vào đường dẫn đầy đủ
            img.save(full_output_path, format='ICO', sizes=sizes)
            
            self.update_status(f"Chuyển đổi thành công! Icon đã lưu tại: {os.path.abspath(full_output_path)}", "green")

        except FileNotFoundError:
            self.update_status(f"Lỗi: Không tìm thấy file '{input_file}'.", "red")
        except Exception as e:
            self.update_status(f"Lỗi khi chuyển đổi: {e}", "red")

    def update_status(self, message, color="black"):
        self.master.after(0, lambda: self.status_label.config(text=message, fg=color))

    def start_conversion_thread(self):
        self.convert_button.config(state=tk.DISABLED)
        self.update_status("Đang chuyển đổi...", "blue")
        
        conversion_thread = threading.Thread(target=self._run_conversion_task)
        conversion_thread.daemon = True 
        conversion_thread.start()

    def _run_conversion_task(self):
        self.convert_image_to_ico()
        self.master.after(0, lambda: self.convert_button.config(state=tk.NORMAL))


if __name__ == "__main__":
    root = tk.Tk()
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
        
    app = ImageToICOConverter(root)
    root.mainloop()