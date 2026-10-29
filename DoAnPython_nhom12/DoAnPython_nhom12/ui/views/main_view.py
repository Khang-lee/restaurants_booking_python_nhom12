import tkinter as tk
from tkinter import messagebox

# Import FloorplanView từ đường dẫn dự án
from ui.views.floorplan_view import FloorplanView

# Tải hoặc tự tạo class giả lập nếu chưa có file booking_list_view
try:
    from ui.views.booking_list_view import BookingListView
except (ImportError, ModuleNotFoundError):
    class BookingListView(tk.Frame):
        def __init__(self, parent=None, role="Lễ tân", booking_service=None):
            super().__init__(parent, bg="white")
            self.role = role
            self.booking_service = booking_service
            tk.Label(
                self,
                text="📋 DANH SÁCH ĐẶT BÀN (TÍNH NĂNG ĐANG PHÁT TRIỂN)",
                font=("Segoe UI", 12, "bold"),
                bg="white",
                fg="#7f8c8d",
            ).pack(expand=True, pady=50)

# ==============================================================
# SỬA LẠI IMPORT CHUẨN XÁC TÊN FILE: billlistview
# ==============================================================
try:
    from ui.views.billlistview import BillListView
except (ImportError, ModuleNotFoundError):
    class BillListView(tk.Frame):
        def __init__(self, parent=None, role="Lễ tân"):
            super().__init__(parent, bg="white")
            self.role = role
            tk.Label(
                self,
                text="🧾 QUẢN LÝ HÓA ĐƠN / BILL (TÍNH NĂNG ĐANG PHÁT TRIỂN)",
                font=("Segoe UI", 12, "bold"),
                bg="white",
                fg="#7f8c8d",
            ).pack(expand=True, pady=50)


# Tải hoặc tự tạo class giả lập nếu chưa có file report_view
try:
    from ui.views.report_view import ReportView
except (ImportError, ModuleNotFoundError):
    class ReportView(tk.Frame):
        def __init__(self, parent=None):
            super().__init__(parent, bg="white")
            tk.Label(
                self,
                text="📊 THỐNG KÊ & BÁO CÁO (TÍNH NĂNG ĐANG PHÁT TRIỂN)",
                font=("Segoe UI", 12, "bold"),
                bg="white",
                fg="#7f8c8d",
            ).pack(expand=True, pady=50)


class MainView(tk.Frame):

    def __init__(self, parent, current_user=None):
        super().__init__(parent)

        # 1. Khởi tạo đối tượng user
        if isinstance(current_user, dict):
            self.current_user = current_user
        else:
            # Nếu truyền vào là string hoặc None
            user_str = str(current_user or "").strip()

            # Lấy danh sách users từ DataManager của ứng dụng chính (nếu có)
            data_mgr = getattr(self.master, "data_manager", None)
            matched_user = None

            if data_mgr and hasattr(data_mgr, "load_users"):
                users = data_mgr.load_users()
                for u in users:
                    if u.get("username") == user_str or u.get("full_name") == user_str:
                        matched_user = u
                        break

            if matched_user:
                self.current_user = matched_user
            else:
                # Kiểm tra tương đối nếu không tìm thấy trong DB
                is_admin = "quanly" in user_str.lower() or "quản lý" in user_str.lower()
                self.current_user = {
                    "username": user_str if user_str else "guest",
                    "full_name": user_str if user_str else "Khách",
                    "role": "Quản lý" if is_admin else "Lễ tân",
                }

        # 2. Lấy role từ thông tin tài khoản đã chuẩn hóa
        self.role = self.current_user.get("role", "Lễ tân")

        # --- SIDEBAR NAV ---
        sidebar = tk.Frame(self, bg="#34495e", width=200)
        sidebar.pack(side="left", fill="y")

        display_name = self.current_user.get(
            "full_name", self.current_user.get("username", "")
        )

        tk.Label(
            sidebar,
            text=f"👤 {display_name}\n({str(self.role).upper()})",
            font=("Segoe UI", 9, "bold"),
            fg="#2ecc71" if self.role == "Quản lý" else "#f1c40f",
            bg="#34495e",
            justify="left",
            padx=15,
        ).pack(fill="x", pady=(15, 10))

        # Thanh Menu
        self.btn_floorplan = tk.Button(
            sidebar,
            text="📌  Sơ đồ bàn",
            anchor="w",
            padx=15,
            command=lambda: self.show_view("floorplan"),
            bg="#16a085",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
        )
        self.btn_floorplan.pack(fill="x", padx=10, pady=4, ipady=5)

        self.btn_booking = tk.Button(
            sidebar,
            text="📋  Danh sách đặt",
            anchor="w",
            padx=15,
            command=lambda: self.show_view("booking"),
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            cursor="hand2",
        )
        self.btn_booking.pack(fill="x", padx=10, pady=4, ipady=5)

        # NÚT MỚI: QUẢN LÝ BILL BÀN
        self.btn_bill = tk.Button(
            sidebar,
            text="🧾  Bill bàn / Hóa đơn",
            anchor="w",
            padx=15,
            command=lambda: self.show_view("bill"),
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            cursor="hand2",
        )
        self.btn_bill.pack(fill="x", padx=10, pady=4, ipady=5)

        # PHÂN QUYỀN GIAO DIỆN: Kiểm tra trực tiếp "Quản lý"
        if self.role == "Quản lý":
            self.btn_report = tk.Button(
                sidebar,
                text="📊  Thống kê & Báo cáo",
                anchor="w",
                padx=15,
                command=lambda: self.show_view("report"),
                bg="#34495e",
                fg="white",
                font=("Segoe UI", 10),
                relief="flat",
                cursor="hand2",
            )
            self.btn_report.pack(fill="x", padx=10, pady=4, ipady=5)

        btn_logout = tk.Button(
            sidebar,
            text="🚪  Đăng xuất",
            anchor="w",
            padx=15,
            command=self.handle_logout,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
        )
        btn_logout.pack(side="bottom", fill="x", padx=10, pady=15, ipady=5)

        # Khung chứa màn hình chính
        self.container = tk.Frame(self, bg="white")
        self.container.pack(side="right", fill="both", expand=True)

        booking_svc = getattr(self.master, "booking_service", None)

        self.views = {
            "floorplan": FloorplanView(self.container, role=self.role),
            "booking": BookingListView(
                parent=self.container,
                role=self.role,
                booking_service=booking_svc,
            ),
            "bill": BillListView(parent=self.container, role=self.role),
        }

        if self.role == "Quản lý":
            self.views["report"] = ReportView(self.container)

        self.show_view("floorplan")

    def show_view(self, view_name):
        # Reset màu tất cả các nút
        self.btn_floorplan.config(bg="#34495e", font=("Segoe UI", 10))
        self.btn_booking.config(bg="#34495e", font=("Segoe UI", 10))
        self.btn_bill.config(bg="#34495e", font=("Segoe UI", 10))
        if hasattr(self, "btn_report"):
            self.btn_report.config(bg="#34495e", font=("Segoe UI", 10))

        # Highlight nút đang được chọn
        if view_name == "floorplan":
            self.btn_floorplan.config(bg="#16a085", font=("Segoe UI", 10, "bold"))
        elif view_name == "booking":
            self.btn_booking.config(bg="#16a085", font=("Segoe UI", 10, "bold"))
        elif view_name == "bill":
            self.btn_bill.config(bg="#16a085", font=("Segoe UI", 10, "bold"))
        elif view_name == "report" and hasattr(self, "btn_report"):
            self.btn_report.config(bg="#16a085", font=("Segoe UI", 10, "bold"))

        # Hiển thị View tương ứng
        for key, view in self.views.items():
            if key == view_name:
                view.pack(fill="both", expand=True)
                if hasattr(view, "load_data"):
                    view.load_data()
            else:
                view.pack_forget()

    def handle_logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?"):
            self.pack_forget()

            login_widget = getattr(
                self.master,
                "login_frame",
                getattr(self.master, "login_dialog", None),
            )

            if login_widget:
                login_widget.pack(fill="both", expand=True)
                if hasattr(login_widget, "txt_username"):
                    login_widget.txt_username.delete(0, tk.END)
                if hasattr(login_widget, "txt_password"):
                    login_widget.txt_password.delete(0, tk.END)
                    login_widget.txt_username.focus()

            self.destroy()