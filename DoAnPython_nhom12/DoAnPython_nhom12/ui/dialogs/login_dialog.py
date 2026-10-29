import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk


class LoginDialog(tk.Frame):

    def __init__(self, parent, auth_service, on_login_success):
        # 1. Nền tối sang trọng, tạo độ tương phản cao với Card chính
        super().__init__(parent, bg="#1e272e")
        self.auth_service = auth_service
        self.on_login_success = on_login_success

        # 2. Khung chứa form (Card UI) bo lề rộng rãi, bỏ viền đen thô
        center_card = tk.Frame(
            self, bg="#ffffff", padx=50, pady=40, width=420, height=570
        )
        center_card.place(relx=0.5, rely=0.5, anchor="center")
        center_card.pack_propagate(False)

        # 3. Nạp và hiển thị Logo nhà hàng
        self.load_logo(center_card)

        # 4. Tiêu đề Form
        tk.Label(
            center_card,
            text="HỆ THỐNG QUẢN LÝ",
            font=("Segoe UI", 9, "bold"),
            fg="#808e9b",
            bg="#ffffff",
        ).pack()

        tk.Label(
            center_card,
            text="ĐĂNG NHẬP",
            font=("Segoe UI", 18, "bold"),
            fg="#2c3e50",
            bg="#ffffff",
        ).pack(pady=(2, 20))

        # 5. Khung nhập liệu (Xếp dọc hiện đại)
        form_frame = tk.Frame(center_card, bg="#ffffff")
        form_frame.pack(fill="x")

        # Username
        tk.Label(
            form_frame,
            text="Tài khoản",
            font=("Segoe UI", 9, "bold"),
            fg="#34495e",
            bg="#ffffff",
        ).pack(anchor="w", pady=(0, 2))

        self.txt_username = ttk.Entry(
            form_frame, font=("Segoe UI", 10), width=28
        )
        self.txt_username.pack(fill="x", ipady=4, pady=(0, 12))
        self.txt_username.focus()

        # Password
        tk.Label(
            form_frame,
            text="Mật khẩu",
            font=("Segoe UI", 9, "bold"),
            fg="#34495e",
            bg="#ffffff",
        ).pack(anchor="w", pady=(0, 2))

        self.txt_password = ttk.Entry(
            form_frame, font=("Segoe UI", 10), width=28, show="•"
        )
        self.txt_password.pack(fill="x", ipady=4, pady=(0, 15))

        # Phím tắt: Nhấn Enter ở bất kỳ ô nào cũng sẽ tự bấm Đăng nhập
        self.txt_username.bind("<Return>", lambda event: self.handle_login())
        self.txt_password.bind("<Return>", lambda event: self.handle_login())

        # 6. Nút Đăng nhập tràn viền, có hiệu ứng đổi màu khi rê chuột
        self.btn_login = tk.Button(
            center_card,
            text="ĐĂNG NHẬP",
            font=("Segoe UI", 10, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#219150",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_login,
        )
        self.btn_login.pack(fill="x", ipady=6, pady=(10, 0))

    def load_logo(self, parent):
        """Hàm nạp file logo TTB(1).ico / png ở góc trên form"""
        logo_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "TTB(1).ico"
        )
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(__file__), "TTB(1).ico")

        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img = img.resize((65, 65), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(parent, image=self.logo_img, bg="#ffffff")
                lbl_logo.pack(pady=(0, 10))
            except Exception:
                pass

    def handle_login(self):
        username = self.txt_username.get().strip()
        password = self.txt_password.get().strip()

        if not username or not password:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng nhập đầy đủ tài khoản và mật khẩu!"
            )
            return

        success, user_data_or_error = self.auth_service.login(
            username, password
        )

        if success:
            user = user_data_or_error
            full_name = (
                user.get("full_name")
                if isinstance(user, dict)
                else "Người dùng"
            )

            messagebox.showinfo(
                "Thành công", f"Đăng nhập thành công! Chào mừng {full_name}."
            )

            # Truyền object user đã đăng nhập sang hàm callback tiếp theo
            if callable(self.on_login_success):
                self.on_login_success(user)
        else:
            messagebox.showerror(
                "Thất bại", user_data_or_error or "Đăng nhập thất bại!"
            )