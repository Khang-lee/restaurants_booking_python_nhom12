import json
import os
import uuid
import tkinter as tk
from tkinter import messagebox, ttk

from ui.views.order_menu_view import OrderMenuView


class Table:
    def __init__(
        self,
        id,
        name,
        area,
        capacity=4,
        status="Trống",
        x=50,
        y=50,
        bookings=None,
        orders=None,
    ):
        self.id = id
        self.name = name
        self.area = area
        self.capacity = capacity
        self.status = status
        self.x = x
        self.y = y
        self.bookings = bookings if bookings is not None else []
        self.orders = orders if orders is not None else []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "area": self.area,
            "capacity": self.capacity,
            "status": self.status,
            "x": self.x,
            "y": self.y,
            "bookings": self.bookings,
            "orders": self.orders,
        }


class FloorplanView(tk.Frame):

    COLOR_MAP = {
        "Trống": "#95a5a6",
        "Đã đặt": "#e67e22",
        "Đang phục vụ": "#2ecc71",
    }
    GRID_SIZE = 20

    def __init__(self, parent, role="Lễ tân", open_booking_callback=None):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.open_booking_callback = open_booking_callback
        self.is_edit_mode = False

        self.drag_data = {"x": 0, "y": 0, "item": None, "table": None}
        self.tables = []

        # TỰ ĐỘNG TÌM ĐƯỜNG DẪN DỮ LIỆU BÀN TRONG DATA/TABLES.JSON
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(CURRENT_DIR, "data", "tables.json"),
            os.path.join(os.path.dirname(CURRENT_DIR), "data", "tables.json"),
            os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), "data", "tables.json"),
            os.path.join("data", "tables.json")
        ]
        
        self.DATA_FILE = possible_paths[0]
        for path in possible_paths:
            if os.path.exists(path):
                self.DATA_FILE = path
                break

        self.load_data_from_file()
        self.setup_ui()
        self.draw_tables()

    def load_data(self):
        self.load_data_from_file()
        self.draw_tables()

    def load_data_from_file(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tables = [Table(**item) for item in data]
                    return
            except Exception as e:
                print(f"Lỗi đọc file JSON bàn ăn: {e}")
        self.tables = []

    def save_data_to_file(self, show_toast=True):
        try:
            data = [t.to_dict() for t in self.tables]
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            if show_toast:
                messagebox.showinfo(
                    "Thành công", "Đã lưu thông tin và vị trí sơ đồ bàn!"
                )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    def setup_ui(self):
        top_frame = tk.Frame(self, bg="white", padx=15, pady=10)
        top_frame.pack(fill="x")

        tk.Label(
            top_frame,
            text="📌 SƠ ĐỒ MẶT BẰNG BÀN",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(side="left")

        tk.Label(
            top_frame, text=" | Khu vực:", bg="white", font=("Segoe UI", 10)
        ).pack(side="left", padx=(10, 2))

        areas = ["Tất cả"] + sorted(list(set(t.area for t in self.tables)))
        self.cbo_area = ttk.Combobox(
            top_frame, values=areas, state="readonly", width=12
        )
        self.cbo_area.set("Tất cả")
        self.cbo_area.pack(side="left", padx=5)
        self.cbo_area.bind(
            "<<ComboboxSelected>>", lambda e: self.on_area_changed()
        )

        # CÁC NÚT DÀNH RIÊNG CHO QUẢN LÝ (Mặc định ẩn)
        self.btn_add_table = tk.Button(
            top_frame, text="➕ Thêm Bàn", bg="#27ae60", fg="white",
            font=("Segoe UI", 9, "bold"), command=self.add_new_table
        )
        
        self.btn_save_layout = tk.Button(
            top_frame, text="💾 Lưu Sơ Đồ", bg="#2980b9", fg="white",
            font=("Segoe UI", 9, "bold"), command=self.save_data_to_file
        )

        legend_frame = tk.Frame(top_frame, bg="white")
        legend_frame.pack(side="right")
        for status, color in self.COLOR_MAP.items():
            box = tk.Label(
                legend_frame, bg=color, width=2, height=1, relief="solid", bd=1
            )
            box.pack(side="left", padx=(8, 2))
            lbl = tk.Label(
                legend_frame, text=status, bg="white", font=("Segoe UI", 8, "bold"),
            )
            lbl.pack(side="left")

        canvas_container = tk.Frame(self, bg="#dcdde1", padx=2, pady=2)
        canvas_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_container, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def on_area_changed(self):
        selected_area = self.cbo_area.get()
        
        # PHÂN QUYỀN: Chỉ có Quản lý mới bật được Edit Mode
        if selected_area == "Tất cả" or self.role != "Quản lý":
            self.is_edit_mode = False
            self.btn_save_layout.pack_forget()
            self.btn_add_table.pack_forget()
        else:
            # Là Quản lý và chọn 1 khu vực cụ thể
            self.is_edit_mode = True
            self.btn_save_layout.pack(side="left", padx=5)
            self.btn_add_table.pack(side="left", padx=5)

        self.draw_tables()

    def add_new_table(self):
        """Tạo bàn mới trong khu vực đang chọn (Chỉ Quản lý)"""
        current_area = self.cbo_area.get()
        if current_area == "Tất cả":
            return
            
        new_id = f"T-{str(uuid.uuid4().hex)[:6].upper()}"
        new_name = f"Bàn mới {len(self.tables) + 1}"
        
        new_table = Table(id=new_id, name=new_name, area=current_area, capacity=4, x=50, y=50)
        self.tables.append(new_table)
        self.save_data_to_file(show_toast=False)
        self.draw_tables()
        messagebox.showinfo("Thêm bàn", f"Đã thêm '{new_name}' vào {current_area}.\nKéo thả để di chuyển, nhấp đúp để đổi tên!")

    def draw_tables(self):
        self.canvas.delete("all")
        selected_area = self.cbo_area.get()
        w_table, h_table = 120, 90

        if selected_area == "Tất cả":
            areas = sorted(list(set(t.area for t in self.tables)))
            current_y = 30
            padding_x = 40
            spacing_x = 140

            for area in areas:
                self.canvas.create_text(
                    40, current_y, text=f"📍 {area.upper()}", anchor="w",
                    font=("Segoe UI", 12, "bold"), fill="#2c3e50"
                )
                self.canvas.create_line(40, current_y + 15, 750, current_y + 15, fill="#bdc3c7", width=1)

                area_tables = [t for t in self.tables if t.area == area]
                start_x = padding_x
                start_y = current_y + 35

                for idx, table in enumerate(area_tables):
                    x = start_x + (idx % 5) * spacing_x
                    y = start_y + (idx // 5) * 110
                    self.render_single_table(table, x, y, w_table, h_table)

                rows = ((len(area_tables) - 1) // 5) + 1 if area_tables else 1
                current_y = start_y + rows * 110 + 20
        else:
            if self.is_edit_mode:
                w_canv = self.canvas.winfo_width() or 1000
                h_canv = self.canvas.winfo_height() or 700
                for x in range(0, w_canv, self.GRID_SIZE):
                    self.canvas.create_line(x, 0, x, h_canv, fill="#f1f2f6", tags="grid")
                for y in range(0, h_canv, self.GRID_SIZE):
                    self.canvas.create_line(0, y, w_canv, y, fill="#f1f2f6", tags="grid")

            filtered_tables = [t for t in self.tables if t.area == selected_area]
            for table in filtered_tables:
                self.render_single_table(table, table.x, table.y, w_table, h_table)

    def render_single_table(self, table, x, y, w, h):
        bg_color = self.COLOR_MAP.get(table.status, "#95a5a6")
        tag_name = f"table_{table.id}"

        outline_color = "#e74c3c" if self.is_edit_mode else "#2c3e50"
        dash_pattern = (4, 4) if self.is_edit_mode else None

        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg_color, outline=outline_color, width=2,
            dash=dash_pattern, tags=(tag_name, "table_group")
        )
        self.canvas.create_text(
            x + w / 2, y + 25, text=table.name, fill="white",
            font=("Segoe UI", 10, "bold"), tags=(tag_name, "table_group")
        )
        self.canvas.create_text(
            x + w / 2, y + 48, text=f"👥 {table.capacity} chỗ", fill="white",
            font=("Segoe UI", 8), tags=(tag_name, "table_group")
        )

        status_text = (
            "↔️ Kéo / Nhấp đúp để Sửa" if self.is_edit_mode else f"[{table.status}]"
        )
        
        self.canvas.create_text(
            x + w / 2, y + 68, text=status_text, fill="white",
            font=("Segoe UI", 8, "italic"), tags=(tag_name, "table_group")
        )

        self.canvas.tag_bind(tag_name, "<Double-Button-1>", lambda e, t=table: self.on_table_double_click(t))
        self.canvas.tag_bind(tag_name, "<ButtonPress-1>", lambda e, tag=tag_name, t=table: self.on_drag_start(e, tag, t))
        self.canvas.tag_bind(tag_name, "<B1-Motion>", self.on_drag_motion)
        self.canvas.tag_bind(tag_name, "<ButtonRelease-1>", self.on_drag_stop)

    def on_drag_start(self, event, tag_name, table):
        if not self.is_edit_mode: return
        self.drag_data["item"] = tag_name
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["table"] = table
        self.drag_data["original_x"] = table.x
        self.drag_data["original_y"] = table.y

    def is_overlapping(self, current_table, target_x, target_y, w=120, h=90):
        for other in self.tables:
            if other.id == current_table.id or other.area != current_table.area:
                continue
            if not (target_x + w <= other.x or target_x >= other.x + w or target_y + h <= other.y or target_y >= other.y + h):
                return True
        return False

    def on_drag_motion(self, event):
        if not self.is_edit_mode or not self.drag_data["item"]: return
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.drag_data["item"], dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_stop(self, event):
        if not self.is_edit_mode or not self.drag_data["table"]: return

        current_table = self.drag_data["table"]
        bbox = self.canvas.bbox(self.drag_data["item"])

        if bbox:
            raw_x, raw_y = bbox[0], bbox[1]
            snapped_x = max(0, round(raw_x / self.GRID_SIZE) * self.GRID_SIZE)
            snapped_y = max(0, round(raw_y / self.GRID_SIZE) * self.GRID_SIZE)

            if self.is_overlapping(current_table, snapped_x, snapped_y):
                messagebox.showwarning("Cảnh báo", "Vị trí bị đè lên bàn khác! Bàn sẽ quay về vị trí ban đầu.")
                current_table.x = self.drag_data["original_x"]
                current_table.y = self.drag_data["original_y"]
            else:
                current_table.x = snapped_x
                current_table.y = snapped_y

            self.draw_tables()
        self.drag_data["item"] = None
        self.drag_data["table"] = None

    def on_table_double_click(self, table):
        # PHÂN QUYỀN CHỨC NĂNG KHI NHẤP ĐÚP
        if self.is_edit_mode:
            # Quản lý ở khu vực cụ thể -> Mở hộp thoại cấu hình / sửa / xóa bàn
            self.open_edit_table_dialog(table)
        else:
            # Lễ tân hoặc chế độ xem Tất cả -> Mở hộp thoại đặt món / thanh toán
            if self.open_booking_callback:
                self.open_booking_callback(table, self.tables, self.draw_tables, self)
            elif OrderMenuView:
                OrderMenuView.open_booking_dialog(table, self.tables, self.draw_tables, self)

    def open_edit_table_dialog(self, table):
        dialog = tk.Toplevel(self)
        dialog.title(f"⚙️ CẤU HÌNH BÀN - {table.name}")
        dialog.geometry("360x300")
        dialog.configure(bg="white")
        dialog.transient(self)
        dialog.grab_set()

        # Tiêu đề
        tk.Label(dialog, text="THÔNG TIN BÀN", font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10))

        frame_inputs = tk.Frame(dialog, bg="white")
        frame_inputs.pack(fill="both", expand=True, padx=20)

        # Tên bàn
        tk.Label(frame_inputs, text="Tên bàn (*):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        txt_name = tk.Entry(frame_inputs, width=25, font=("Segoe UI", 10))
        txt_name.insert(0, table.name)
        txt_name.grid(row=0, column=1, pady=8, padx=5)

        # Khu vực
        tk.Label(frame_inputs, text="Khu vực (*):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        txt_area = tk.Entry(frame_inputs, width=25, font=("Segoe UI", 10))
        txt_area.insert(0, table.area)
        txt_area.grid(row=1, column=1, pady=8, padx=5)

        # Sức chứa
        tk.Label(frame_inputs, text="Sức chứa:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        spn_cap = tk.Spinbox(frame_inputs, from_=1, to=100, width=23, font=("Segoe UI", 10))
        spn_cap.delete(0, "end")
        spn_cap.insert(0, table.capacity)
        spn_cap.grid(row=2, column=1, pady=8, padx=5)

        def save_changes():
            new_name = txt_name.get().strip()
            new_area = txt_area.get().strip()
            
            # 1. Bắt lỗi đầu vào
            if not new_name or not new_area:
                messagebox.showerror("Lỗi", "Tên bàn và Khu vực không được để trống!", parent=dialog)
                return
                
            try:
                new_cap = int(spn_cap.get())
                if new_cap <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Sức chứa phải là số nguyên dương lớn hơn 0!", parent=dialog)
                return

            # 2. Kiểm tra trùng tên bàn (trừ chính cái bàn đang sửa)
            for t in self.tables:
                if t.id != table.id and t.name.lower() == new_name.lower():
                    messagebox.showwarning("Cảnh báo", f"Tên bàn '{new_name}' đã tồn tại!\nVui lòng chọn tên khác.", parent=dialog)
                    return

            # 3. Cập nhật dữ liệu
            table.name = new_name
            table.area = new_area
            table.capacity = new_cap

            # 4. Làm mới danh sách dropdown Khu vực
            areas = ["Tất cả"] + sorted(list(set(t.area for t in self.tables)))
            self.cbo_area["values"] = areas
            
            # Nếu khu vực thay đổi, tự động chuyển UI về khu vực mới đó
            self.cbo_area.set(new_area)
            self.on_area_changed()
            
            # Lưu file và đóng
            self.save_data_to_file(show_toast=False)
            messagebox.showinfo("Thành công", f"Đã cập nhật thông tin cho {new_name}!", parent=dialog)
            dialog.destroy()
            
        def delete_table():
            if table.status != "Trống":
                messagebox.showerror("Lỗi", "Bàn đang có khách hoặc đã được đặt, không thể xóa!", parent=dialog)
                return
                
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa vĩnh viễn '{table.name}' không?", parent=dialog):
                self.tables.remove(table)
                self.save_data_to_file(show_toast=False)
                
                # Cập nhật lại dropdown khu vực
                areas = ["Tất cả"] + sorted(list(set(t.area for t in self.tables)))
                self.cbo_area["values"] = areas
                
                # Nếu xóa xong mà khu vực đó hết bàn thì quay về màn hình 'Tất cả'
                if not any(t.area == self.cbo_area.get() for t in self.tables):
                    self.cbo_area.set("Tất cả")
                    self.on_area_changed()
                else:
                    self.draw_tables()
                    
                messagebox.showinfo("Thành công", "Đã xóa bàn thành công!", parent=dialog)
                dialog.destroy()

        # Nút bấm dưới cùng
        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        tk.Button(
            btn_frame, text="💾 Lưu Thay Đổi", bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"), command=save_changes, pady=5
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        tk.Button(
            btn_frame, text="🗑️ Xóa Bàn", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), command=delete_table, pady=5
        ).pack(side="right", expand=True, fill="x", padx=(5, 0))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("HỆ THỐNG QUẢN LÝ BÀN NHÀ HÀNG")
    root.geometry("1000x700")
    # Chạy thử với quyền Quản lý
    app = FloorplanView(root, role="Quản lý")
    app.pack(fill="both", expand=True)
    root.mainloop()