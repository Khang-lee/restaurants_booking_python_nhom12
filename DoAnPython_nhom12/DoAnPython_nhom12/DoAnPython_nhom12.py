import ctypes
import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import AuthService
from services.data_manager import DataManager
from ui.dialogs.login_dialog import LoginDialog
from ui.views.main_view import MainView


class RestaurantApp(tk.Tk):

    def __init__(self):
        super().__init__()

        # 1. Đăng ký App ID để Windows nhận diện Icon riêng dưới Taskbar
        try:
            myappid = "nhom12.restaurant.management.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                myappid
            )
        except Exception:
            pass

        # 2. Cấu hình cửa sổ
        self.title("HỆ THỐNG QUẢN LÝ ĐẶT BÀN NHÀ HÀNG")
        self.geometry("1100x650")
        self.minsize(900, 550)

        # 3. Nạp và chỉnh kích thước Icon (Dài x Rộng)
        self.set_custom_icon_size(width=64, height=64)

        # 4. Khởi tạo các dịch vụ
        self.data_manager = DataManager()
        self.auth_service = AuthService(self.data_manager)

        # 5. Sự kiện đóng ứng dụng
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 6. Mở màn hình Login
        self.login_frame = LoginDialog(
            self, self.auth_service, self.show_main_app
        )
        self.login_frame.pack(fill="both", expand=True)

    def set_custom_icon_size(self, width=48, height=48):
        """Hàm chỉnh chiều dài và chiều rộng của Icon"""
        icon_path = os.path.join(os.path.dirname(__file__), "TTB(1).ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(
                os.path.dirname(__file__), "assets", "TTB(1).ico"
            )

        if os.path.exists(icon_path):
            try:
                # Nạp icon gốc qua iconbitmap cho thanh tiêu đề
                self.iconbitmap(icon_path)

                # Dùng Pillow để mở và chỉnh kích thước Dài x Rộng mong muốn
                img = Image.open(icon_path)
                img_resized = img.resize(
                    (width, height), Image.Resampling.LANCZOS
                )

                # Lưu giữ tham chiếu ảnh icon đã resize
                self.app_icon = ImageTk.PhotoImage(img_resized)
                self.wm_iconphoto(True, self.app_icon)
            except Exception as e:
                print(f"Lỗi nạp icon: {e}")

    def show_main_app(self, user=None):
        # 1. Ẩn/xóa màn hình đăng nhập (Dùng đúng biến self.login_frame)
        if hasattr(self, "login_frame") and self.login_frame:
            self.login_frame.pack_forget()

        # 2. Xóa MainView cũ nếu đã tồn tại
        if hasattr(self, "main_view") and self.main_view:
            self.main_view.destroy()

        # 3. Khởi tạo MainView mới và truyền user vừa đăng nhập vào
        self.main_view = MainView(self, current_user=user)
        self.main_view.pack(fill="both", expand=True)

    def on_closing(self):
        try:
            self.destroy()
        except Exception:
            pass
        finally:
            os._exit(0)


if __name__ == "__main__":
    app = RestaurantApp()
    app.mainloop()