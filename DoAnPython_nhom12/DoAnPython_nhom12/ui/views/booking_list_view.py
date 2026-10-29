import json
import os
import uuid
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

class BookingListView(tk.Frame):
    def __init__(self, parent=None, role="Lễ tân", booking_service=None):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.booking_service = booking_service
        
        # --- TÌM ĐƯỜNG DẪN CÁC FILE JSON ---
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # 1. Đường dẫn file bookings.json
        booking_paths = [
            os.path.join(CURRENT_DIR, "..", "..", "data", "bookings.json"),
            os.path.join(CURRENT_DIR, "..", "data", "bookings.json"),
            os.path.join("data", "bookings.json")
        ]
        self.BOOKING_FILE = booking_paths[0]
        for path in booking_paths:
            if os.path.exists(path):
                self.BOOKING_FILE = path
                break
                
        # 2. Đường dẫn file tables.json (để cập nhật trạng thái bàn)
        table_paths = [
            os.path.join(CURRENT_DIR, "..", "..", "data", "tables.json"),
            os.path.join(CURRENT_DIR, "..", "data", "tables.json"),
            os.path.join("data", "tables.json")
        ]
        self.TABLE_FILE = table_paths[0]
        for path in table_paths:
            if os.path.exists(path):
                self.TABLE_FILE = path
                break

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- HEADER & TOOLBAR ---
        header_frame = tk.Frame(self, bg="white", padx=20, pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame, 
            text="📋 DANH SÁCH ĐẶT BÀN", 
            font=("Segoe UI", 14, "bold"), 
            bg="white", 
            fg="#2c3e50"
        ).pack(side="left")
        
        toolbar = tk.Frame(header_frame, bg="white")
        toolbar.pack(side="right")

        # Nút Thêm (Cho tất cả)
        tk.Button(
            toolbar, text="➕ Thêm mới", bg="#2ecc71", fg="white", 
            font=("Segoe UI", 9, "bold"), command=lambda: self.open_booking_form(is_edit=False), 
            relief="flat", cursor="hand2", padx=10
        ).pack(side="left", padx=5)

        # Nút Sửa (Cho tất cả)
        tk.Button(
            toolbar, text="✏️ Sửa", bg="#f39c12", fg="white", 
            font=("Segoe UI", 9, "bold"), command=lambda: self.open_booking_form(is_edit=True), 
            relief="flat", cursor="hand2", padx=10
        ).pack(side="left", padx=5)

        # Nút Xóa (CHỈ CHO QUẢN LÝ)
        if self.role == "Quản lý":
            tk.Button(
                toolbar, text="❌ Xóa", bg="#e74c3c", fg="white", 
                font=("Segoe UI", 9, "bold"), command=self.delete_booking, 
                relief="flat", cursor="hand2", padx=10
            ).pack(side="left", padx=5)

        # Nút Làm mới
        tk.Button(
            toolbar, text="🔄 Làm mới", bg="#3498db", fg="white", 
            font=("Segoe UI", 9, "bold"), command=self.load_data, 
            relief="flat", cursor="hand2", padx=10
        ).pack(side="left", padx=5)

        # --- BẢNG DỮ LIỆU (TREEVIEW) ---
        table_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("id", "table", "customer", "phone", "guests", "deposit", "date", "time", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        
        self.tree.heading("id", text="Mã Đặt")
        self.tree.heading("table", text="Bàn (ID)")
        self.tree.heading("customer", text="Khách hàng")
        self.tree.heading("phone", text="Số ĐT")
        self.tree.heading("guests", text="Khách")
        self.tree.heading("deposit", text="Tiền cọc (VNĐ)")
        self.tree.heading("date", text="Ngày đặt")
        self.tree.heading("time", text="Giờ đặt")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("table", width=100, anchor="center")
        self.tree.column("customer", width=150)
        self.tree.column("phone", width=110, anchor="center")
        self.tree.column("guests", width=60, anchor="center")
        self.tree.column("deposit", width=110, anchor="e")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("time", width=80, anchor="center")
        self.tree.column("status", width=110, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        if os.path.exists(self.BOOKING_FILE):
            try:
                with open(self.BOOKING_FILE, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                    for b in reversed(bookings):
                        self.tree.insert("", "end", values=(
                            b.get("booking_id", ""),
                            b.get("table_id", ""),
                            b.get("customer_name", ""),
                            b.get("customer_phone", ""),
                            b.get("guest_count", 0),
                            f"{int(b.get('deposit_amount', 0)):,}",
                            b.get("booking_date", ""),
                            b.get("booking_time", ""),
                            b.get("status", "")
                        ))
            except Exception as e:
                print(f"Lỗi đọc file bookings.json: {e}")

    # ===============================================
    # CÁC HÀM XỬ LÝ (THÊM, SỬA, XÓA)
    # ===============================================
    def delete_booking(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một đơn để xóa!")
            return
            
        item = self.tree.item(selected[0])
        booking_id = item['values'][0]
        table_name = item['values'][1]

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa đơn đặt bàn {booking_id} của {table_name}?"):
            # 1. Xóa trong bookings.json
            try:
                with open(self.BOOKING_FILE, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                bookings = [b for b in bookings if b.get("booking_id") != booking_id]
                
                with open(self.BOOKING_FILE, "w", encoding="utf-8") as f:
                    json.dump(bookings, f, ensure_ascii=False, indent=2)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa JSON Đặt bàn: {e}")
                return

            # 2. Cập nhật lại bàn thành "Trống" trong tables.json (để sơ đồ xanh lại)
            self._update_table_status(table_name, "Trống")
            
            messagebox.showinfo("Thành công", "Đã xóa đơn đặt bàn!")
            self.load_data()

    def open_booking_form(self, is_edit=False):
        selected = self.tree.selection()
        if is_edit and not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một đơn đặt bàn để sửa!")
            return

        dialog = tk.Toplevel(self)
        dialog.title("SỬA ĐẶT BÀN" if is_edit else "THÊM ĐẶT BÀN MỚI")
        dialog.geometry("380x420")
        dialog.configure(bg="white")
        dialog.transient(self)
        dialog.grab_set()

        # Lấy danh sách bàn từ tables.json để đưa vào Combobox
        table_names = []
        if os.path.exists(self.TABLE_FILE):
            try:
                with open(self.TABLE_FILE, "r", encoding="utf-8") as f:
                    tables = json.load(f)
                    table_names = [t["name"] for t in tables]
            except:
                pass
        if not table_names:
            table_names = ["Bàn 01", "Bàn 02", "Bàn VIP"] # Backup data

        # Form Fields
        tk.Label(dialog, text="Chọn Bàn:", bg="white").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        cbo_table = ttk.Combobox(dialog, values=table_names, state="readonly", width=22)
        cbo_table.grid(row=0, column=1)
        if table_names: cbo_table.current(0)

        tk.Label(dialog, text="Tên KH:", bg="white").grid(row=1, column=0, sticky="w", padx=20, pady=10)
        txt_cust = tk.Entry(dialog, width=25)
        txt_cust.grid(row=1, column=1)

        tk.Label(dialog, text="Số ĐT:", bg="white").grid(row=2, column=0, sticky="w", padx=20, pady=10)
        txt_phone = tk.Entry(dialog, width=25)
        txt_phone.grid(row=2, column=1)

        tk.Label(dialog, text="Số khách:", bg="white").grid(row=3, column=0, sticky="w", padx=20, pady=10)
        spn_guests = tk.Spinbox(dialog, from_=1, to=50, width=23)
        spn_guests.grid(row=3, column=1)

        tk.Label(dialog, text="Tiền cọc:", bg="white").grid(row=4, column=0, sticky="w", padx=20, pady=10)
        txt_deposit = tk.Entry(dialog, width=25)
        txt_deposit.insert(0, "0")
        txt_deposit.grid(row=4, column=1)
        
        def auto_calc(*args):
            try:
                val = int(spn_guests.get()) * 120000
                txt_deposit.delete(0, tk.END)
                txt_deposit.insert(0, f"{val}")
            except: pass
        spn_guests.config(command=auto_calc)

        tk.Label(dialog, text="Ngày đặt:", bg="white").grid(row=5, column=0, sticky="w", padx=20, pady=10)
        if DateEntry:
            dt_entry = DateEntry(dialog, width=22, background="darkblue", date_pattern="yyyy-mm-dd")
        else:
            dt_entry = tk.Entry(dialog, width=25)
            dt_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        dt_entry.grid(row=5, column=1)

        tk.Label(dialog, text="Giờ đặt:", bg="white").grid(row=6, column=0, sticky="w", padx=20, pady=10)
        time_slots = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in (0, 30)]
        cbo_time = ttk.Combobox(dialog, values=time_slots, state="readonly", width=22)
        cbo_time.set("18:00")
        cbo_time.grid(row=6, column=1)

        # Trạng thái ban đầu (Biến id để lưu nếu đang Sửa)
        booking_id_to_edit = None
        old_table_name = None

        if is_edit:
            item = self.tree.item(selected[0])['values']
            booking_id_to_edit = item[0]
            old_table_name = item[1]
            
            cbo_table.set(item[1])
            txt_cust.insert(0, item[2])
            txt_phone.insert(0, f"0{item[3]}" if not str(item[3]).startswith('0') else item[3]) # fix zero drop
            spn_guests.delete(0, tk.END)
            spn_guests.insert(0, item[4])
            txt_deposit.delete(0, tk.END)
            txt_deposit.insert(0, str(item[5]).replace(',', ''))
            
            if DateEntry:
                dt_entry.set_date(datetime.strptime(item[6], "%Y-%m-%d"))
            else:
                dt_entry.delete(0, tk.END)
                dt_entry.insert(0, item[6])
                
            cbo_time.set(item[7])

        def save_form():
            t_name = cbo_table.get()
            cust = txt_cust.get().strip()
            phone = txt_phone.get().strip()
            deposit = txt_deposit.get().replace(",", "").strip()
            date = dt_entry.get_date().strftime("%Y-%m-%d") if DateEntry and hasattr(dt_entry, "get_date") else dt_entry.get()
            time = cbo_time.get()

            if not cust or not phone.isdigit() or not deposit.isdigit():
                messagebox.showerror("Lỗi", "Vui lòng nhập đúng Tên, SĐT (số), Tiền cọc (số)!")
                return

            # Đọc file hiện tại
            bookings = []
            if os.path.exists(self.BOOKING_FILE):
                with open(self.BOOKING_FILE, "r", encoding="utf-8") as f:
                    bookings = json.load(f)

            if is_edit:
                # Cập nhật đơn cũ
                for b in bookings:
                    if b.get("booking_id") == booking_id_to_edit:
                        b["table_id"] = t_name
                        b["customer_name"] = cust
                        b["customer_phone"] = phone
                        b["guest_count"] = int(spn_guests.get())
                        b["deposit_amount"] = int(deposit)
                        b["booking_date"] = date
                        b["booking_time"] = time
                        break
            else:
                # Thêm đơn mới
                b_id = "B" + str(uuid.uuid4().hex)[:5].upper()
                bookings.append({
                    "booking_id": b_id,
                    "table_id": t_name,
                    "customer_name": cust,
                    "customer_phone": phone,
                    "booking_date": date,
                    "booking_time": time,
                    "guest_count": int(spn_guests.get()),
                    "status": "Đã xác nhận",
                    "pre_orders": [],
                    "deposit_amount": int(deposit)
                })

            # 1. Lưu lại bookings.json
            with open(self.BOOKING_FILE, "w", encoding="utf-8") as f:
                json.dump(bookings, f, ensure_ascii=False, indent=2)

            # 2. Cập nhật tables.json
            if is_edit and old_table_name != t_name:
                self._update_table_status(old_table_name, "Trống")
            self._update_table_status(t_name, "Đã đặt")

            messagebox.showinfo("Thành công", "Đã lưu Đơn đặt bàn!")
            self.load_data()
            dialog.destroy()

        tk.Button(
            dialog, text="✅ Lưu Thông Tin", bg="#2ecc71", fg="white", 
            font=("Segoe UI", 10, "bold"), command=save_form, pady=5
        ).grid(row=7, column=0, columnspan=2, sticky="we", padx=20, pady=20)

    # --- Hàm hỗ trợ cập nhật màu/trạng thái bàn trong file tables.json ---
    def _update_table_status(self, table_name, new_status):
        if not os.path.exists(self.TABLE_FILE):
            return
            
        try:
            with open(self.TABLE_FILE, "r", encoding="utf-8") as f:
                tables = json.load(f)
                
            for t in tables:
                if t.get("name") == table_name:
                    t["status"] = new_status
                    break
                    
            with open(self.TABLE_FILE, "w", encoding="utf-8") as f:
                json.dump(tables, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi cập nhật tables.json: {e}")