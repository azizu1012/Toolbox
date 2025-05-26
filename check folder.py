import os
import tkinter as tk
from tkinter import filedialog

def list_files_and_folders(startpath):
    """
    Liệt kê tất cả các file và thư mục con bắt đầu từ startpath.
    Mỗi dòng output sẽ có dạng: [Độ sâu] [D/F] Tên (trong đó D là thư mục, F là file)
    """
    # Sử dụng một list để lưu trữ kết quả, dễ dàng hơn cho việc hiển thị hoặc ghi file sau này
    output_lines = []

    for root, dirs, files in os.walk(startpath):
        # Tính toán độ sâu của thư mục hiện tại để thụt đầu dòng cho dễ nhìn
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)

        # Hiển thị thư mục hiện tại
        output_lines.append(f"{indent}[D] {os.path.basename(root)}/")
        # print(f"{indent}[D] {os.path.basename(root)}/") # Bỏ comment nếu muốn in trực tiếp ra console

        sub_indent = ' ' * 4 * (level + 1)
        # Hiển thị các file trong thư mục hiện tại
        for f in files:
            output_lines.append(f"{sub_indent}[F] {f}")
            # print(f"{sub_indent}[F] {f}") # Bỏ comment nếu muốn in trực tiếp ra console
    
    return "\n".join(output_lines)

def select_folder_and_scan():
    """
    Mở hộp thoại để người dùng chọn thư mục, sau đó quét và hiển thị cấu trúc.
    """
    root_tk = tk.Tk()
    root_tk.withdraw()  # Ẩn cửa sổ chính của tkinter

    folder_path = filedialog.askdirectory(title="Chọn thư mục mod để quét")

    if folder_path:
        print(f"Đang quét thư mục: {folder_path}\n")
        structure_output = list_files_and_folders(folder_path)
        
        # Hiển thị kết quả trong console
        print("Cấu trúc thư mục và file:")
        print(structure_output)
        
        # (Tùy chọn) Lưu kết quả vào một file text
        try:
            output_filename = "folder_structure.txt"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(f"Cấu trúc thư mục và file của: {folder_path}\n\n")
                f.write(structure_output)
            print(f"\nKết quả đã được lưu vào file: {os.path.abspath(output_filename)}")
        except Exception as e:
            print(f"\nLỗi khi lưu file: {e}")
            
    else:
        print("Không có thư mục nào được chọn.")

if __name__ == "__main__":
    select_folder_and_scan()