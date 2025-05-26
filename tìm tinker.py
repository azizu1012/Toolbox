import os
import sys
import re

def find_tkinter_tcl_base_dir():
    """
    Tìm thư mục gốc của Tkinter tcl/tk trong các đường dẫn Python phổ biến.
    """
    print(f"Đang tìm kiếm thư mục Tkinter tcl/tk trong môi trường Python hiện tại...")

    # Các đường dẫn Python cơ bản mà PyInstaller thường sử dụng
    # sys.base_prefix: Đường dẫn gốc của môi trường Python (đặc biệt hữu ích cho venv)
    # sys.prefix: Đường dẫn cài đặt Python hiện tại
    potential_python_roots = [
        sys.base_prefix,
        sys.prefix
    ]

    # Loại bỏ các đường dẫn trùng lặp và đảm bảo chúng là duy nhất
    potential_python_roots = list(set(potential_python_roots))

    tcl_base_dir_found = None

    for python_root_path in potential_python_roots:
        if not python_root_path or not os.path.isdir(python_root_path):
            print(f"  Bỏ qua đường dẫn không hợp lệ hoặc không tồn tại: {python_root_path}")
            continue

        print(f"  Đang kiểm tra trong thư mục gốc Python: {python_root_path}")

        # Các vị trí phổ biến của thư mục tcl/tk trong cài đặt Python
        # Ví dụ: C:\Python39\tcl
        # Hoặc: C:\Users\YourUser\AppData\Local\Programs\Python\Python311\tcl
        # Hoặc (ít phổ biến hơn cho tcl/tk trực tiếp ở đây, nhưng có thể có): C:\Python39\Lib\tcltk
        potential_tcl_paths = [
            os.path.join(python_root_path, 'tcl'),
            os.path.join(python_root_path, 'Lib', 'tcltk'), # Đối với các trường hợp đặc biệt như venv
        ]

        for path_attempt in potential_tcl_paths:
            if os.path.isdir(path_attempt):
                print(f"    Tìm thấy một thư mục có tên 'tcl' hoặc 'tcltk': {path_attempt}")
                # Kiểm tra xem có ít nhất một thư mục con tkX.Y và tclX.Y không
                tk_sub_dir_found = False
                tcl_sub_dir_found = False
                
                try: 
                    for d in os.listdir(path_attempt):
                        full_d_path = os.path.join(path_attempt, d)
                        if os.path.isdir(full_d_path):
                            if d.startswith('tk') and re.match(r'tk\d+\.\d+$', d): 
                                tk_sub_dir_found = True
                            if d.startswith('tcl') and re.match(r'tcl\d+\.\d+$', d): 
                                tcl_sub_dir_found = True
                        if tk_sub_dir_found and tcl_sub_dir_found:
                            print(f"\n✅ Đã tìm thấy thư mục gốc của Tkinter tcl/tk tại: {path_attempt}")
                            tcl_base_dir_found = path_attempt
                            return tcl_base_dir_found # Tìm thấy, trả về đường dẫn ngay
                except PermissionError:
                    print(f"    Không có quyền truy cập thư mục: {path_attempt}")
                except Exception as e:
                    print(f"    Lỗi khi kiểm tra thư mục {path_attempt}: {e}")
            else:
                print(f"    Thư mục không tồn tại: {path_attempt}")

    if not tcl_base_dir_found:
        print("\n❌ Không tìm thấy thư mục Tkinter tcl/tk chuẩn trong các đường dẫn đã kiểm tra.")
        print("   Có thể bạn cần tìm thủ công hoặc đảm bảo Tkinter được cài đặt đúng cách.")
    return tcl_base_dir_found

if __name__ == "__main__":
    found_path = find_tkinter_tcl_base_dir()
    if found_path:
        print("\nBạn có thể sử dụng đường dẫn này với PyInstaller như sau:")
        print(f"pyinstaller your_script.py --onefile --windowed --add-data \"{found_path};tcl\"")
        print("\nLưu ý: Thay 'your_script.py' bằng tên file Python của bạn.")
    else:
        print("\nKhông tìm thấy đường dẫn Tkinter. Vui lòng kiểm tra lại cài đặt Python/Tkinter của bạn.")