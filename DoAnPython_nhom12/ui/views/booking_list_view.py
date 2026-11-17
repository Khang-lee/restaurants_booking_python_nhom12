import os
import json
import uuid
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  # <-- Thêm DateEntry từ thư viện tkcalendar

class BookingListView(tk.Frame):
    def __init__(self, parent=None, role="Lễ tân", booking_service=None):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.booking_service = booking_service
        self.bookings = []
        self.selected_booking_id = None  # Lưu ID dòng đang chọn
        
        self.setup_ui()
        self.load_data()

    def _get_bookings_file_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "..", "..", "data", "bookings.json")
        if not os.path.exists(file_path):
            return "data/bookings.json"
        return file_path

    def _get_tables_file_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "..", "..", "data", "tables.json")
        if not os.path.exists(file_path):
            return "data/tables.json"
        return file_path

    def load_table_options(self):
        """Tải danh sách tên bàn trực tiếp từ file tables.json"""
        tables = []
        try:
            file_path = self._get_tables_file_path()
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for t in data:
                        t_name = t.get("name") or t.get("id")
                        if t_name and t_name not in tables:
                            tables.append(str(t_name))
        except Exception as e:
            print("Lỗi đọc danh sách bàn từ tables.json:", e)
        return tables

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

        # 2. Main Content Container
        main_content = tk.Frame(self, bg="#f5f6fa")
        main_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Khung bên trái chứa Bảng Treeview
        left_frame = tk.Frame(main_content, bg="white", padx=10, pady=10, bd=1, relief="solid")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        left_frame.configure(highlightbackground="#dcdde1")

        columns = ("id", "table", "customer", "phone", "guests", "date", "time", "status", "deposit")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        
        # Tiêu đề cột
        self.tree.heading("id", text="Mã Đặt")
        self.tree.heading("table", text="Bàn")
        self.tree.heading("customer", text="Tên Khách")
        self.tree.heading("phone", text="SĐT")
        self.tree.heading("guests", text="Khách")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("time", text="Giờ")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("deposit", text="Cọc (VNĐ)")

        # Kích thước cột
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

        # 3. Khung bên phải: Form chỉnh sửa và thao tác trực tiếp
        right_frame = tk.Frame(main_content, bg="white", padx=15, pady=15, bd=1, relief="solid", width=310)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)
        right_frame.configure(highlightbackground="#dcdde1")

        tk.Label(
            right_frame, text="⚙️ THÔNG TIN ĐẶT BÀN", 
            font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 10))

        # Form fields
        tk.Label(right_frame, text="Chọn Bàn:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        table_list = self.load_table_options()
        self.combo_table = ttk.Combobox(right_frame, values=table_list, font=("Segoe UI", 9), state="readonly")
        self.combo_table.pack(fill="x", pady=(0, 6), ipady=2)
        if table_list:
            self.combo_table.current(0)

        tk.Label(right_frame, text="Tên Khách Hàng:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.txt_name = tk.Entry(right_frame, font=("Segoe UI", 9), bd=1, relief="solid")
        self.txt_name.pack(fill="x", pady=(0, 6), ipady=2)

        tk.Label(right_frame, text="Số Điện Thoại:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.txt_phone = tk.Entry(right_frame, font=("Segoe UI", 9), bd=1, relief="solid")
        self.txt_phone.pack(fill="x", pady=(0, 6), ipady=2)

        tk.Label(right_frame, text="Số Lượng Khách:", bg="white", font=("Segoe UI, 9, bold")).pack(anchor="w", pady=(2, 0)) if False else tk.Label(right_frame, text="Số Lượng Khách:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.txt_guests = tk.Entry(right_frame, font=("Segoe UI", 9), bd=1, relief="solid")
        self.txt_guests.pack(fill="x", pady=(0, 6), ipady=2)
        self.txt_guests.insert(0, "2")
        self.txt_guests.bind("<KeyRelease>", self.on_guests_changed)

        tk.Label(right_frame, text="Tiền Cọc (VNĐ):", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.txt_deposit = tk.Entry(right_frame, font=("Segoe UI", 9), bd=1, relief="solid")
        self.txt_deposit.pack(fill="x", pady=(0, 6), ipady=2)
        self.txt_deposit.insert(0, "100000")

        # === ĐÃ THÊM: Ô CHỌN NGÀY (DateEntry) THAY CHO NHẬP VĂN BẢN THƯỜNG ===
        tk.Label(right_frame, text="Ngày Đến:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        self.date_entry = DateEntry(
            right_frame, width=22, font=("Segoe UI", 9),
            background='#2980b9', foreground='white', borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.pack(fill="x", pady=(0, 6), ipady=2)
        # ====================================================================

        tk.Label(right_frame, text="Giờ Hẹn:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 0))
        time_frame = tk.Frame(right_frame, bg="white")
        time_frame.pack(fill="x", pady=(0, 10))

        hours = [f"{h:02d}" for h in range(8, 23)]
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]

        self.combo_hour = ttk.Combobox(time_frame, values=hours, font=("Segoe UI", 9), width=7, state="readonly")
        self.combo_hour.pack(side="left")
        self.combo_hour.set("18")

        tk.Label(time_frame, text=" : ", bg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=3)

        self.combo_minute = ttk.Combobox(time_frame, values=minutes, font=("Segoe UI", 9), width=7, state="readonly")
        self.combo_minute.pack(side="left")
        self.combo_minute.set("00")

        # Nút Thêm Mới, Cập Nhật, Xóa
        tk.Button(
            right_frame, text="➕ Thêm Mới", bg="#2ecc71", fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", pady=6,
            command=self.save_new_booking
        ).pack(fill="x", pady=4)

        tk.Button(
            right_frame, text="✏️ Cập Nhật (Sửa)", bg="#f39c12", fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", pady=6,
            command=self.update_selected_booking
        ).pack(fill="x", pady=4)

        tk.Button(
            right_frame, text="🗑️ Xóa Lịch Đặt", bg="#e74c3c", fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", pady=6,
            command=self.delete_selected_booking
        ).pack(fill="x", pady=4)

    def on_guests_changed(self, event):
        """Tự động gợi ý tiền cọc tối thiểu (50K/người) khi thay đổi số lượng khách"""
        try:
            guests = int(self.txt_guests.get().strip())
            if guests > 0:
                min_deposit = guests * 50000
                self.txt_deposit.delete(0, tk.END)
                self.txt_deposit.insert(0, str(min_deposit))
        except ValueError:
            pass

    def _check_conflict(self, table_id, booking_date, booking_time, exclude_booking_id=None):
        """
        Kiểm tra trùng lịch đặt bàn:
        Mỗi bàn trong ngày phải cách nhau tối thiểu 30 phút (giả định 1 ca bàn tiêu chuẩn kéo dài 2 tiếng).
        Trả về True nếu bị trùng/vi phạm khoảng cách, False nếu hợp lệ.
        """
        file_path = self._get_bookings_file_path()
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bookings = json.load(f)

            target_date = str(booking_date).split(" ")[0].strip()
            new_dt_start = datetime.strptime(f"{target_date} {booking_time}", "%Y-%m-%d %H:%M")
            new_dt_end = new_dt_start + timedelta(hours=2)

            for b in bookings:
                b_id = b.get("booking_id")
                if exclude_booking_id and b_id == exclude_booking_id:
                    continue

                b_table = str(b.get("table_id", "")).strip()
                b_date_raw = str(b.get("booking_date", "")).strip()
                b_date = b_date_raw.split(" ")[0].strip()
                b_time = str(b.get("booking_time", "")).strip()
                b_status = str(b.get("status", "")).strip()

                # Chỉ xét cùng bàn, cùng ngày và không bị hủy
                if b_table == str(table_id).strip() and b_date == target_date and b_status != "Đã hủy":
                    existing_dt_start = datetime.strptime(f"{b_date} {b_time}", "%Y-%m-%d %H:%M")
                    existing_dt_end = existing_dt_start + timedelta(hours=2)

                    # Quy tắc: Các lịch đặt phải cách nhau tối thiểu 30 phút
                    buffer_td = timedelta(minutes=30)
                    buffered_new_start = new_dt_start - buffer_td
                    buffered_new_end = new_dt_end + buffer_td

                    if max(buffered_new_start, existing_dt_start) < min(buffered_new_end, existing_dt_end):
                        return True
        except Exception as e:
            print("Lỗi kiểm tra trùng lịch:", e)

        return False

    def load_data(self):
        """Tải dữ liệu từ bookings.json lên bảng"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.bookings = []
        try:
            file_path = self._get_bookings_file_path()
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self.bookings = json.load(f)

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
        except Exception as e:
            print("Lỗi tải danh sách đặt bàn:", e)
        self.clear_form()

    def on_row_select(self, event):
        """Đổ dữ liệu từ dòng được chọn lên form bên phải"""
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], "values")
        b_id, table_id, cust_name, phone, guests, b_date, b_time, status, deposit_str = item_values
        
        self.selected_booking_id = b_id

        if table_id in self.combo_table["values"]:
            self.combo_table.set(table_id)
        
        self.txt_name.delete(0, tk.END)
        self.txt_name.insert(0, cust_name)

        self.txt_phone.delete(0, tk.END)
        self.txt_phone.insert(0, phone)

        self.txt_guests.delete(0, tk.END)
        self.txt_guests.insert(0, guests)

        raw_deposit = deposit_str.replace(",", "").strip()
        self.txt_deposit.delete(0, tk.END)
        self.txt_deposit.insert(0, raw_deposit)

        # === ĐÃ THÊM: Đổ ngày từ bảng lên DateEntry khi click chọn dòng ===
        if b_date:
            try:
                self.date_entry.set_date(b_date)
            except Exception:
                pass
        # ================================================================

        if ":" in b_time:
            h_part, m_part = b_time.split(":")[:2]
            self.combo_hour.set(h_part)
            self.combo_minute.set(m_part)

    def clear_form(self):
        """Làm sạch form nhập liệu bên phải và hủy chọn dòng trên bảng"""
        self.selected_booking_id = None
        self.txt_name.delete(0, tk.END)
        self.txt_phone.delete(0, tk.END)
        self.txt_guests.delete(0, tk.END)
        self.txt_guests.insert(0, "2")
        self.txt_deposit.delete(0, tk.END)
        self.txt_deposit.insert(0, "100000")
        
        # === ĐÃ THÊM: Reset DateEntry về ngày hiện tại khi clear form ===
        try:
            self.date_entry.set_date(datetime.now().strftime("%Y-%m-%d"))
        except Exception:
            pass
        # ============================================================

        self.combo_hour.set("18")
        self.combo_minute.set("00")
        if self.combo_table["values"]:
            self.combo_table.current(0)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def save_new_booking(self):
        """Thêm mới lịch đặt bàn với kiểm tra tiền cọc tối thiểu và trùng lịch (cách nhau ít nhất 30p)"""
        t_id = self.combo_table.get().strip()
        c_name = self.txt_name.get().strip()
        c_phone = self.txt_phone.get().strip()
        g_count = self.txt_guests.get().strip()
        deposit_str = self.txt_deposit.get().strip()
        b_time = f"{self.combo_hour.get()}:{self.combo_minute.get()}"
        
        # === ĐÃ THÊM: Lấy ngày từ DateEntry thay vì mặc định ngày hiện tại ===
        booking_date = self.date_entry.get().strip()
        # ===================================================================

        if not t_id or not c_name or not c_phone:
            messagebox.showerror("Lỗi", "Vui lòng chọn bàn và nhập đầy đủ tên, số điện thoại!")
            return

        try:
            guests_int = int(g_count)
            if guests_int <= 0:
                guests_int = 1
        except ValueError:
            guests_int = 1

        try:
            deposit_val = float(deposit_str)
        except ValueError:
            deposit_val = 0.0

        # 1. Kiểm tra quy tắc cọc tối thiểu 50K/người
        min_required = guests_int * 50000
        if deposit_val < min_required:
            messagebox.showerror("Lỗi tiền cọc", f"Tiền cọc tối thiểu cho {guests_int} khách là {min_required:,.0f} VNĐ (50,000đ/người)!")
            return

        # 2. Kiểm tra trùng lịch và khoảng cách tối thiểu 30 phút
        if self._check_conflict(t_id, booking_date, b_time):
            messagebox.showerror("Lỗi trùng lịch", f"Bàn [{t_id}] đã có lịch đặt trùng hoặc không đủ khoảng cách tối thiểu 30 phút so với lịch hẹn này!")
            return

        file_path = self._get_bookings_file_path()
        bookings = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    bookings = json.load(f)
                except Exception:
                    bookings = []

        new_booking = {
            "booking_id": f"B{str(uuid.uuid4().hex)[:5].upper()}",
            "table_id": t_id,
            "customer_name": c_name,
            "customer_phone": c_phone,
            "booking_date": booking_date,  # Lưu ngày từ DateEntry
            "booking_time": b_time,
            "guest_count": guests_int,
            "status": "Đã xác nhận",
            "pre_orders": [],
            "deposit_amount": deposit_val
        }
        bookings.append(new_booking)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(bookings, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", "Đã thêm mới lịch đặt bàn thành công!")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu: {e}")

    def update_selected_booking(self):
        """Sửa thông tin lịch đặt bàn đang chọn với kiểm tra tiền cọc và trùng lịch (cách nhau ít nhất 30p)"""
        if not self.selected_booking_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch đặt bàn từ bảng bên trái cần sửa!")
            return
        
        t_id = self.combo_table.get().strip()
        c_name = self.txt_name.get().strip()
        c_phone = self.txt_phone.get().strip()
        g_count = self.txt_guests.get().strip()
        deposit_str = self.txt_deposit.get().strip()
        b_time = f"{self.combo_hour.get()}:{self.combo_minute.get()}"
        
        # === ĐÃ THÊM: Lấy ngày mới từ DateEntry khi cập nhật ===
        booking_date = self.date_entry.get().strip()
        # ====================================================

        if not t_id or not c_name or not c_phone:
            messagebox.showerror("Lỗi", "Vui lòng chọn bàn và nhập đầy đủ tên, số điện thoại!")
            return

        try:
            guests_int = int(g_count)
            if guests_int <= 0:
                guests_int = 1
        except ValueError:
            guests_int = 1

        try:
            deposit_val = float(deposit_str)
        except ValueError:
            deposit_val = 0.0

        # 1. Kiểm tra quy tắc cọc tối thiểu 50K/người
        min_required = guests_int * 50000
        if deposit_val < min_required:
            messagebox.showerror("Lỗi tiền cọc", f"Tiền cọc tối thiểu cho {guests_int} khách là {min_required:,.0f} VNĐ (50,000đ/người)!")
            return

        # 2. Kiểm tra trùng lịch và khoảng cách tối thiểu 30 phút (loại trừ chính booking đang sửa)
        if self._check_conflict(t_id, booking_date, b_time, exclude_booking_id=self.selected_booking_id):
            messagebox.showerror("Lỗi trùng lịch", f"Khung giờ chỉnh sửa bị trùng hoặc không đủ khoảng cách tối thiểu 30 phút với lịch đặt khác của bàn [{t_id}]!")
            return

        file_path = self._get_bookings_file_path()
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                updated = False
                for b in bookings:
                    if b.get("booking_id") == self.selected_booking_id:
                        b["table_id"] = t_id
                        b["customer_name"] = c_name
                        b["customer_phone"] = c_phone
                        b["guest_count"] = guests_int
                        b["booking_date"] = booking_date  # Cập nhật ngày mới từ DateEntry
                        b["booking_time"] = b_time
                        b["deposit_amount"] = deposit_val
                        updated = True
                        break
                
                if updated:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(bookings, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("Thành công", f"Đã cập nhật lịch đặt mã [{self.selected_booking_id}] thành công!")
                    self.load_data()
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy mã đặt bàn cần cập nhật.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật dữ liệu: {e}")

    def delete_selected_booking(self):
        """Xóa lịch đặt bàn đang chọn ngay tại form bên phải"""
        if not self.selected_booking_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn lịch đặt bàn từ bảng bên trái cần xóa!")
            return
        
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa lịch đặt bàn mã [{self.selected_booking_id}] không?"):
            try:
                file_path = self._get_bookings_file_path()
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        bookings = json.load(f)
                    
                    new_bookings = [b for b in bookings if b.get("booking_id") != self.selected_booking_id]
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(new_bookings, f, ensure_ascii=False, indent=2)
                        
                    messagebox.showinfo("Thành công", "Đã xóa lịch đặt bàn thành công!")
                    self.load_data()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa dữ liệu: {e}")