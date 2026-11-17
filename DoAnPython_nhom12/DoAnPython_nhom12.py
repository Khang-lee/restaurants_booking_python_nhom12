import ctypes
import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

# Đảm bảo nhận diện đường dẫn gốc của dự án
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
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        # 2. Cấu hình cửa sổ
        self.title("HỆ THỐNG QUẢN LÝ ĐẶT BÀN NHÀ HÀNG")
        self.geometry("1100x650")
        self.minsize(900, 550)

        # 3. Nạp và chỉnh kích thước Icon
        self.set_custom_icon_size(width=64, height=64)

        # 4. Khởi tạo các dịch vụ cốt lõi
        self.data_manager = DataManager()
        self.auth_service = AuthService(self.data_manager)
        
        # (Tùy chọn) Khởi tạo booking_service nếu dự án của bạn có quản lý service này
        self.booking_service = None 

        # 5. Sự kiện đóng ứng dụng
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 6. Mở màn hình Login
        try:
            self.login_frame = LoginDialog(self, self.auth_service, self.show_main_app)
            self.login_frame.pack(fill="both", expand=True)
        except Exception as e:
            print(f"Lỗi khởi tạo màn hình đăng nhập: {e}")

    def set_custom_icon_size(self, width=48, height=48):
        icon_path = os.path.join(os.path.dirname(__file__), "TTB(1).ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "TTB(1).ico")

        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
                img = Image.open(icon_path)
                img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
                self.app_icon = ImageTk.PhotoImage(img_resized)
                self.wm_iconphoto(True, self.app_icon)
            except Exception as e:
                print(f"Lỗi nạp icon: {e}")

    def show_main_app(self, user=None):
        """Chuyển từ màn hình Đăng nhập sang Màn hình chính (MainView)"""
        if hasattr(self, "login_frame") and self.login_frame:
            self.login_frame.pack_forget()
            self.login_frame.destroy()
            self.login_frame = None

        if hasattr(self, "main_view") and self.main_view:
            self.main_view.destroy()

        # Khởi tạo và đưa MainView lên hiển thị
        self.main_view = MainView(self, current_user=user)
        self.main_view.pack(fill="both", expand=True)

    def on_closing(self):
        """Xử lý khi tắt hẳn ứng dụng"""
        try:
            self.destroy()
        except Exception:
            pass
        finally:
            os._exit(0)

if __name__ == "__main__":
    app = RestaurantApp()
    app.mainloop()