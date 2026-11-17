import tkinter as tk
from tkinter import ttk, messagebox
from controllers.booking_controller import BookingController

class BookingListView(tk.Frame):
    def __init__(self, parent=None, role="Lễ tân", booking_service=None):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.controller = BookingController(self)
        self.bookings = []
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 1. Header Top Bar
        top_bar = tk.Frame(self, bg="white", padx=20, pady=15, bd=1, relief="solid")
        top_bar.pack(fill="x", padx=15, pady=15)
        top_bar.configure(highlightbackground="#dcdde1")

        tk.Label(
            top_bar, text="📋 DANH SÁCH ĐẶT BÀN", 
            font=("Segoe UI", 16, "bold"), bg="white", fg="#2c3e50"
        ).pack(side="left")

        btn_action_frame = tk.Frame(top_bar, bg="white")
        btn_action_frame.pack(side="right")

        tk.Button(
            btn_action_frame, text="🔄 Làm mới", bg="#3498db", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=12, pady=6,
            command=self.load_data
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            btn_action_frame, text="➕ Thêm mới", bg="#2ecc71", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=12, pady=6,
            command=self.add_booking
        ).pack(side="right", padx=(8, 0))

        # 2. Main Content Container (Bố cục Trái: Bảng, Phải: Thao tác nhanh)
        main_content = tk.Frame(self, bg="#f5f6fa")
        main_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Khung bên trái chứa Bảng Treeview
        left_frame = tk.Frame(main_content, bg="white", padx=10, pady=10, bd=1, relief="solid")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        left_frame.configure(highlightbackground="#dcdde1")

        columns = ("id", "table", "customer", "phone", "guests", "date", "time", "status", "deposit")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="Mã Đặt")
        self.tree.heading("table", text="Bàn")
        self.tree.heading("customer", text="Tên Khách")
        self.tree.heading("phone", text="SĐT")
        self.tree.heading("guests", text="Khách")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("time", text="Giờ")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("deposit", text="Cọc (VNĐ)")

        self.tree.column("id", width=75, anchor="center")
        self.tree.column("table", width=90, anchor="center")
        self.tree.column("customer", width=120, anchor="w")
        self.tree.column("phone", width=100, anchor="center")
        self.tree.column("guests", width=55, anchor="center")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("time", width=65, anchor="center")
        self.tree.column("status", width=95, anchor="center")
        self.tree.column("deposit", width=80, anchor="e")

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # 3. Khung bên phải: Thao tác nhanh (Sửa / Xóa gắn trực tiếp)
        right_frame = tk.Frame(main_content, bg="white", padx=15, pady=15, bd=1, relief="solid", width=280)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        right_frame.configure(highlightbackground="#dcdde1")

        tk.Label(
            right_frame, text="⚙️ THAO TÁC BÀN ĐẶT", 
            font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 15))

        self.lbl_selected_info = tk.Label(
            right_frame, text="Chưa chọn lịch đặt nào.\n(Chọn một dòng bên trái để thao tác)", 
            font=("Segoe UI", 9), bg="white", fg="#7f8c8d", justify="left"
        )
        self.lbl_selected_info.pack(anchor="w", pady=(0, 20))

        tk.Button(
            right_frame, text="✏️ Sửa Thông Tin", bg="#f39c12", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=10, pady=8,
            command=self.edit_selected_booking
        ).pack(fill="x", pady=5)

        tk.Button(
            right_frame, text="🗑️ Xóa Lịch Đặt", bg="#e74c3c", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=10, pady=8,
            command=self.delete_selected_booking
        ).pack(fill="x", pady=5)

    def load_data(self):
        """Tải dữ liệu thông qua controller"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.bookings = self.controller.get_bookings()
        for b in self.bookings:
            b_id = b.get("booking_id", "")
            table_id = b.get("table_id", "")
            cust_name = b.get("customer_name", "Khách")
            phone = b.get("customer_phone", "")
            guests = b.get("guest_count", 1)
            b_date = b.get("booking_date", "")
            b_time = b.get("booking_time", "")
            status = b.get("status", "Đã xác nhận")
            deposit = b.get("deposit_amount", 0)
            try:
                deposit_str = f"{int(deposit):,}"
            except Exception:
                deposit_str = str(deposit)

            self.tree.insert("", "end", values=(
                b_id, table_id, cust_name, phone, guests, b_date, b_time, status, deposit_str
            ))

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], "values")
        b_id, table_id, cust_name, phone, guests, b_date, b_time, status, deposit = item_values
        
        info_text = (
            f"• Mã đặt: {b_id}\n"
            f"• Bàn: {table_id}\n"
            f"• Khách: {cust_name}\n"
            f"• SĐT: {phone}\n"
            f"• Số khách: {guests} người\n"
            f"• Ngày: {b_date}\n"
            f"• Giờ: {b_time}\n"
            f"• Trạng thái: {status}"
        )
        self.lbl_selected_info.config(text=info_text, fg="#2c3e50")

    def add_booking(self):
        self.open_booking_form_dialog(is_edit=False)

    def edit_selected_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch đặt bàn cần sửa từ bảng bên trái!")
            return
        
        item_values = self.tree.item(selected[0], "values")
        b_id = item_values[0]
        
        target = next((b for b in self.bookings if b.get("booking_id") == b_id), None)
        if target:
            self.open_booking_form_dialog(is_edit=True, booking_data=target)

    def delete_selected_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch đặt bàn cần xóa từ bảng bên trái!")
            return
        
        item_values = self.tree.item(selected[0], "values")
        b_id = item_values[0]
        
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa lịch đặt bàn mã [{b_id}] không?"):
            if self.controller.delete_booking(b_id):
                messagebox.showinfo("Thành công", "Đã xóa lịch đặt bàn thành công!")
                self.lbl_selected_info.config(text="Chưa chọn lịch đặt nào.\n(Chọn một dòng bên trái để thao tác)", fg="#7f8c8d")
                self.load_data()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa dữ liệu đặt bàn.")

    def open_booking_form_dialog(self, is_edit=False, booking_data=None):
        dialog = tk.Toplevel(self)
        dialog.title("Sửa Đặt Bàn" if is_edit else "Thêm Mới Đặt Bàn")
        dialog.geometry("420x480")
        dialog.config(bg="white")
        dialog.grab_set()

        tk.Label(
            dialog, text="THÔNG TIN ĐẶT BÀN", 
            font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50"
        ).pack(pady=15)

        form_frame = tk.Frame(dialog, bg="white", padx=20)
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="Chọn Bàn:", bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
        table_list = self.controller.get_table_options()
        combo_table = ttk.Combobox(form_frame, values=table_list, font=("Segoe UI", 10), state="readonly")
        combo_table.pack(fill="x", pady=(0, 10), ipady=3)
        if table_list:
            combo_table.current(0)

        tk.Label(form_frame, text="Tên Khách Hàng:", bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
        txt_name = tk.Entry(form_frame, font=("Segoe UI", 10), bd=1, relief="solid")
        txt_name.pack(fill="x", pady=(0, 10), ipady=3)

        tk.Label(form_frame, text="Số Điện Thoại:", bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
        txt_phone = tk.Entry(form_frame, font=("Segoe UI", 10), bd=1, relief="solid")
        txt_phone.pack(fill="x", pady=(0, 10), ipady=3)

        tk.Label(form_frame, text="Số Lượng Khách:", bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
        txt_guests = tk.Entry(form_frame, font=("Segoe UI", 10), bd=1, relief="solid")
        txt_guests.pack(fill="x", pady=(0, 10), ipady=3)

        tk.Label(form_frame, text="Giờ Hẹn:", bg="white", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
        time_frame = tk.Frame(form_frame, bg="white")
        time_frame.pack(fill="x", pady=(0, 10))

        hours = [f"{h:02d}" for h in range(8, 23)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]

        combo_hour = ttk.Combobox(time_frame, values=hours, font=("Segoe UI", 10), width=8, state="readonly")
        combo_hour.pack(side="left")
        combo_hour.set("18")

        tk.Label(time_frame, text=" : ", bg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        combo_minute = ttk.Combobox(time_frame, values=minutes, font=("Segoe UI", 10), width=8, state="readonly")
        combo_minute.pack(side="left")
        combo_minute.set("00")

        if is_edit and booking_data:
            current_table = booking_data.get("table_id", "")
            if current_table in table_list:
                combo_table.set(current_table)
            txt_name.insert(0, booking_data.get("customer_name", ""))
            txt_phone.insert(0, booking_data.get("customer_phone", ""))
            txt_guests.insert(0, str(booking_data.get("guest_count", 1)))
            
            old_time = booking_data.get("booking_time", "18:00")
            if ":" in old_time:
                h_part, m_part = old_time.split(":")[:2]
                combo_hour.set(h_part)
                combo_minute.set(m_part)
        else:
            txt_guests.insert(0, "2")

        def save_data():
            t_id = combo_table.get().strip()
            c_name = txt_name.get().strip()
            c_phone = txt_phone.get().strip()
            g_count = txt_guests.get().strip()
            b_time = f"{combo_hour.get()}:{combo_minute.get()}"

            if not t_id or not c_name or not c_phone:
                messagebox.showerror("Lỗi", "Vui lòng chọn bàn và nhập đầy đủ tên, số điện thoại!", parent=dialog)
                return

            try:
                guests_int = int(g_count)
            except ValueError:
                guests_int = 1

            data = {
                "table_id": t_id,
                "customer_name": c_name,
                "customer_phone": c_phone,
                "guest_count": guests_int,
                "booking_time": b_time
            }

            if is_edit and booking_data:
                success = self.controller.update_booking(booking_data.get("booking_id"), data)
            else:
                success = self.controller.add_booking(data)

            if success:
                messagebox.showinfo("Thành công", "Đã lưu thông tin đặt bàn thành công!", parent=dialog)
                dialog.destroy()
                self.load_data()
            else:
                messagebox.showerror("Lỗi", "Không thể lưu dữ liệu đặt bàn.", parent=dialog)

        tk.Button(
            form_frame, text="💾 Lưu Thông Tin", bg="#2ecc71", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=8,
            command=save_data
        ).pack(fill="x", pady=(15, 0))