import json
import os
import uuid
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

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
        start_time=None,
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
        self.start_time = start_time

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
            "start_time": self.start_time,
        }


class FloorplanView(tk.Frame):

    THEME_MAP = {
        "Trống": {
            "bg": "#ffffff",
            "header": "#7f8c8d",
            "border": "#bdc3c7",
            "text_hdr": "#ffffff",
            "text_body": "#2c3e50",
            "badge_bg": "#ecf0f1",
            "badge_fg": "#7f8c8d",
        },
        "Đã đặt": {
            "bg": "#fffaf0",
            "header": "#e67e22",
            "border": "#f39c12",
            "text_hdr": "#ffffff",
            "text_body": "#d35400",
            "badge_bg": "#fdebd0",
            "badge_fg": "#e67e22",
        },
        "Đang phục vụ": {
            "bg": "#f0fff4",
            "header": "#2ecc71",
            "border": "#27ae60",
            "text_hdr": "#ffffff",
            "text_body": "#1e8449",
            "badge_bg": "#1e8449",
            "badge_fg": "#ffffff",
        },
    }
    GRID_SIZE = 20

    def __init__(self, parent, role="Lễ tân", open_booking_callback=None):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.open_booking_callback = open_booking_callback
        self.is_edit_mode = False

        self.drag_data = {"x": 0, "y": 0, "item": None, "table": None}
        self.tables = []
        self.notified_bookings = set()

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
        self.check_reminders()

        self.timer_job = None
        self.start_live_timer()

    # ==========================================
    # LOGIC ĐẾM GIỜ VÀ NHẮC LỊCH
    # ==========================================
    def start_live_timer(self):
        if not self.is_edit_mode and hasattr(self, 'floorplan_container') and self.floorplan_container.winfo_ismapped():
            self.draw_tables()
        self.timer_job = self.after(1000, self.start_live_timer)

    def destroy(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
        super().destroy()

    def calculate_elapsed_time(self, start_time_str):
        if not start_time_str: return ""
        try:
            start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            diff = datetime.now() - start_dt
            total_seconds = max(0, int(diff.total_seconds()))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except Exception:
            return ""

    def check_reminders(self):
        try:
            booking_file = os.path.join(os.path.dirname(self.DATA_FILE), "bookings.json")
            if not os.path.exists(booking_file): return
            
            with open(booking_file, "r", encoding="utf-8") as f:
                bookings = json.load(f)
                
            now = datetime.now()
            reminders = []
            
            for b in bookings:
                if b.get("status") == "Đã xác nhận":
                    dt_str = f"{b.get('booking_date')} {b.get('booking_time')}"
                    try:
                        b_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                        diff_mins = (b_time - now).total_seconds() / 60
                        
                        if 0 <= diff_mins <= 30:
                            b_id = b.get("booking_id")
                            if b_id not in self.notified_bookings:
                                reminders.append(f"📌 Bàn: {b.get('table_id')} | Khách: {b.get('customer_name')} | SĐT: {b.get('customer_phone')} | Giờ đến: {b.get('booking_time')}")
                                self.notified_bookings.add(b_id)
                    except: pass
                    
            if reminders:
                msg = "🔔 CÁC KHÁCH ĐẶT SẮP ĐẾN TRONG 30 PHÚT TỚI:\n\n" + "\n\n".join(reminders)
                messagebox.showinfo("Nhắc lịch hệ thống", msg)
        except Exception as e:
            print("Lỗi nhắc lịch:", e)

    def load_data(self):
        self.load_data_from_file()
        self.draw_tables()
        self.check_reminders()

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
                messagebox.showinfo("Thành công", "Đã lưu thông tin và vị trí sơ đồ bàn!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    # ==========================================
    # GIAO DIỆN CHÍNH (SETUP UI)
    # ==========================================
    def setup_ui(self):
        # 1. Khung chứa Sơ đồ mặt bằng
        self.floorplan_container = tk.Frame(self, bg="#f5f6fa")
        self.floorplan_container.pack(fill="both", expand=True)

        top_frame = tk.Frame(self.floorplan_container, bg="white", padx=15, pady=12)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="📌 SƠ ĐỒ MẶT BẰNG BÀN", font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50").pack(side="left")
        tk.Label(top_frame, text=" |  Khu vực:", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=(10, 2))

        areas = ["Tất cả"] + sorted(list(set(t.area for t in self.tables)))
        self.cbo_area = ttk.Combobox(top_frame, values=areas, state="readonly", width=12, font=("Segoe UI", 9))
        self.cbo_area.set("Tất cả")
        self.cbo_area.pack(side="left", padx=5)
        self.cbo_area.bind("<<ComboboxSelected>>", lambda e: self.on_area_changed())

        self.btn_add_table = tk.Button(top_frame, text="➕ Thêm Bàn", bg="#2ecc71", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10, command=self.add_new_table)
        self.btn_save_layout = tk.Button(top_frame, text="💾 Lưu Sơ Đồ", bg="#3498db", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10, command=self.save_data_to_file)

        legend_frame = tk.Frame(top_frame, bg="white")
        legend_frame.pack(side="right")
        
        status_colors = [("Trống", "#7f8c8d"), ("Đã đặt", "#e67e22"), ("Đang phục vụ", "#2ecc71")]
        for status, color in status_colors:
            dot = tk.Label(legend_frame, text="●", fg=color, bg="white", font=("Segoe UI", 12))
            dot.pack(side="left", padx=(10, 2))
            lbl = tk.Label(legend_frame, text=status, bg="white", font=("Segoe UI", 9, "bold"), fg="#34495e")
            lbl.pack(side="left")

        canvas_container = tk.Frame(self.floorplan_container, bg="#eaeded", padx=2, pady=2)
        canvas_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_container, bg="#f8f9fa", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 2. Khung Oder trực tiếp ngay trong giao diện này (Mặc định ẩn)
        self.order_container = tk.Frame(self, bg="#f5f6fa")

    def open_embedded_order_view(self, table):
        """Hiển thị bảng Order trực tiếp ngay trong khung giao diện Sơ đồ bàn"""
        self.floorplan_container.pack_forget() # Ẩn sơ đồ bàn
        
        # Xóa các widget Oder cũ nếu có
        for widget in self.order_container.winfo_children():
            widget.destroy()

        self.order_container.pack(fill="both", expand=True)

        # Thanh Header điều hướng quay lại
        nav_bar = tk.Frame(self.order_container, bg="#2c3e50", padx=15, pady=8)
        nav_bar.pack(fill="x")

        tk.Button(
            nav_bar, text="⬅️ Quay lại Sơ đồ bàn", bg="#e74c3c", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            command=self.close_embedded_order_view
        ).pack(side="left")

        tk.Label(
            nav_bar, text=f"ORDER & PHỤC VỤ - {table.name.upper()} ({table.area})",
            font=("Segoe UI", 12, "bold"), bg="#2c3e50", fg="white"
        ).pack(side="right")

        # Tải OrderMenuView lồng thẳng vào order_container
        if OrderMenuView:
            order_view = OrderMenuView(self.order_container, table=table, on_close=self.close_embedded_order_view)
            order_view.pack(fill="both", expand=True)

    def close_embedded_order_view(self):
        """Đóng giao diện Order và quay lại Sơ đồ bàn"""
        self.order_container.pack_forget()
        self.floorplan_container.pack(fill="both", expand=True)
        self.load_data() # Cập nhật lại màu sắc bàn và đồng hồ

    def on_area_changed(self):
        selected_area = self.cbo_area.get()
        if selected_area == "Tất cả" or self.role != "Quản lý":
            self.is_edit_mode = False
            self.btn_save_layout.pack_forget()
            self.btn_add_table.pack_forget()
        else:
            self.is_edit_mode = True
            self.btn_save_layout.pack(side="left", padx=5)
            self.btn_add_table.pack(side="left", padx=5)
        self.draw_tables()

    def add_new_table(self):
        current_area = self.cbo_area.get()
        if current_area == "Tất cả": return
        new_id = f"T-{str(uuid.uuid4().hex)[:6].upper()}"
        new_name = f"Bàn mới {len(self.tables) + 1}"
        new_table = Table(id=new_id, name=new_name, area=current_area, capacity=4, x=60, y=60)
        self.tables.append(new_table)
        self.save_data_to_file(show_toast=False)
        self.draw_tables()
        messagebox.showinfo("Thêm bàn", f"Đã thêm '{new_name}' vào {current_area}.\nKéo thả để di chuyển, nhấp đúp để đổi tên!")

    def create_rounded_rect(self, x1, y1, x2, y2, radius=12, **kwargs):
        points = [
            x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius,
            x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def draw_tables(self):
        self.canvas.delete("all")
        selected_area = self.cbo_area.get()
        w_table, h_table = 130, 95

        if selected_area == "Tất cả":
            areas = sorted(list(set(t.area for t in self.tables)))
            current_y = 30
            padding_x = 40
            spacing_x = 150

            for area in areas:
                self.canvas.create_text(40, current_y, text=f"📍 {area.upper()}", anchor="w", font=("Segoe UI", 12, "bold"), fill="#2c3e50")
                self.canvas.create_line(40, current_y + 16, 780, current_y + 16, fill="#dcdde1", width=1.5)

                area_tables = [t for t in self.tables if t.area == area]
                start_x = padding_x
                start_y = current_y + 35

                for idx, table in enumerate(area_tables):
                    x = start_x + (idx % 5) * spacing_x
                    y = start_y + (idx // 5) * 115
                    self.render_single_table(table, x, y, w_table, h_table)

                rows = ((len(area_tables) - 1) // 5) + 1 if area_tables else 1
                current_y = start_y + rows * 115 + 25
        else:
            if self.is_edit_mode:
                w_canv = self.canvas.winfo_width() or 1000
                h_canv = self.canvas.winfo_height() or 700
                for x in range(0, w_canv, self.GRID_SIZE):
                    for y in range(0, h_canv, self.GRID_SIZE):
                        self.canvas.create_oval(x-1, y-1, x+1, y+1, fill="#bdc3c7", outline="", tags="grid")

            filtered_tables = [t for t in self.tables if t.area == selected_area]
            for table in filtered_tables:
                self.render_single_table(table, table.x, table.y, w_table, h_table)

    def render_single_table(self, table, x, y, w, h):
        theme = self.THEME_MAP.get(table.status, self.THEME_MAP["Trống"])
        tag_name = f"table_{table.id}"

        shadow_offset = 3
        self.create_rounded_rect(
            x + shadow_offset, y + shadow_offset, x + w + shadow_offset, y + h + shadow_offset,
            radius=12, fill="#d6dbdf", outline="", tags=(tag_name, "table_group")
        )

        border_color = "#e74c3c" if self.is_edit_mode else theme["border"]
        card_id = self.create_rounded_rect(
            x, y, x + w, y + h,
            radius=12, fill=theme["bg"], outline=border_color, width=2,
            tags=(tag_name, "table_group")
        )

        self.create_rounded_rect(
            x, y, x + w, y + 28,
            radius=10, fill=theme["header"], outline="",
            tags=(tag_name, "table_group")
        )
        self.canvas.create_rectangle(
            x, y + 14, x + w, y + 28,
            fill=theme["header"], outline="", tags=(tag_name, "table_group")
        )

        self.canvas.create_text(
            x + w / 2, y + 14, text=table.name, fill=theme["text_hdr"],
            font=("Segoe UI", 10, "bold"), tags=(tag_name, "table_group")
        )

        self.canvas.create_text(
            x + w / 2, y + 45, text=f"👤 {table.capacity} chỗ ngồi", fill=theme["text_body"],
            font=("Segoe UI", 9), tags=(tag_name, "table_group")
        )

        if self.is_edit_mode:
            status_text = "↔️ Di chuyển"
            badge_bg, badge_fg = "#ebedef", "#2c3e50"
        else:
            if table.status == "Đang phục vụ":
                timer_str = self.calculate_elapsed_time(table.start_time)
                status_text = f"⏱️ {timer_str}" if timer_str else "Đang phục vụ"
                badge_bg, badge_fg = theme["badge_bg"], theme["badge_fg"]
            else:
                status_text = table.status
                badge_bg, badge_fg = theme["badge_bg"], theme["badge_fg"]

        badge_x1, badge_y1 = x + 12, y + 62
        badge_x2, badge_y2 = x + w - 12, y + 84
        self.create_rounded_rect(
            badge_x1, badge_y1, badge_x2, badge_y2,
            radius=8, fill=badge_bg, outline="", tags=(tag_name, "table_group")
        )
        self.canvas.create_text(
            x + w / 2, y + 73, text=status_text, fill=badge_fg,
            font=("Segoe UI", 8, "bold" if table.status == "Đang phục vụ" else "normal"),
            tags=(tag_name, "table_group")
        )

        def on_hover(e):
            if not self.is_edit_mode:
                self.canvas.itemconfig(card_id, outline="#2980b9", width=3)
                self.canvas.config(cursor="hand2")

        def on_leave(e):
            if not self.is_edit_mode:
                self.canvas.itemconfig(card_id, outline=theme["border"], width=2)
                self.canvas.config(cursor="")

        self.canvas.tag_bind(tag_name, "<Enter>", on_hover)
        self.canvas.tag_bind(tag_name, "<Leave>", on_leave)

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

    def is_overlapping(self, current_table, target_x, target_y, w=130, h=95):
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
        if self.is_edit_mode:
            self.open_edit_table_dialog(table)
        else:
            # Gọi hàm mở booking/order mặc định đã có sẵn trong OrderMenuView
            if self.open_booking_callback:
                self.open_booking_callback(table, self.tables, self.draw_tables, self)
            elif OrderMenuView and hasattr(OrderMenuView, 'open_booking_dialog'):
                OrderMenuView.open_booking_dialog(table, self.tables, self.draw_tables, self)

    def open_edit_table_dialog(self, table):
        dialog = tk.Toplevel(self)
        dialog.title(f"⚙️ CẤU HÌNH BÀN - {table.name}")
        dialog.geometry("360x300")
        dialog.configure(bg="white")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="THÔNG TIN BÀN", font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10))

        frame_inputs = tk.Frame(dialog, bg="white")
        frame_inputs.pack(fill="both", expand=True, padx=20)

        tk.Label(frame_inputs, text="Tên bàn (*):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        txt_name = tk.Entry(frame_inputs, width=25, font=("Segoe UI", 10))
        txt_name.insert(0, table.name)
        txt_name.grid(row=0, column=1, pady=8, padx=5)

        tk.Label(frame_inputs, text="Khu vực (*):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        txt_area = tk.Entry(frame_inputs, width=25, font=("Segoe UI", 10))
        txt_area.insert(0, table.area)
        txt_area.grid(row=1, column=1, pady=8, padx=5)

        tk.Label(frame_inputs, text="Sức chứa:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        spn_cap = tk.Spinbox(frame_inputs, from_=1, to=100, width=23, font=("Segoe UI", 10))
        spn_cap.delete(0, "end")
        spn_cap.insert(0, table.capacity)
        spn_cap.grid(row=2, column=1, pady=8, padx=5)

        def save_changes():
            new_name = txt_name.get().strip()
            new_area = txt_area.get().strip()
            
            if not new_name or not new_area:
                messagebox.showerror("Lỗi", "Tên bàn và Khu vực không được để trống!", parent=dialog)
                return
            try:
                new_cap = int(spn_cap.get())
                if new_cap <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Sức chứa phải là số nguyên dương lớn hơn 0!", parent=dialog)
                return

            for t in self.tables:
                if t.id != table.id and t.name.lower() == new_name.lower():
                    messagebox.showwarning("Cảnh báo", f"Tên bàn '{new_name}' đã tồn tại!\nVui lòng chọn tên khác.", parent=dialog)
                    return

            table.name = new_name
            table.area = new_area
            table.capacity = new_cap
            areas = ["Tất cả"] + sorted(list(set(t.area for t in self.tables)))
            self.cbo_area["values"] = areas
            self.cbo_area.set(new_area)
            self.on_area_changed()
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
                areas = ["Tất cả"] + sorted(list(set(t.area for t in self.tables)))
                self.cbo_area["values"] = areas
                if not any(t.area == self.cbo_area.get() for t in self.tables):
                    self.cbo_area.set("Tất cả")
                    self.on_area_changed()
                else:
                    self.draw_tables()
                messagebox.showinfo("Thành công", "Đã xóa bàn thành công!", parent=dialog)
                dialog.destroy()

        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        tk.Button(btn_frame, text="💾 Lưu Thay Đổi", bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"), command=save_changes, pady=5).pack(side="left", expand=True, fill="x", padx=(0, 5))
        tk.Button(btn_frame, text="🗑️ Xóa Bàn", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), command=delete_table, pady=5).pack(side="right", expand=True, fill="x", padx=(5, 0))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("HỆ THỐNG QUẢN LÝ BÀN NHÀ HÀNG")
    root.geometry("1000x700")
    app = FloorplanView(root, role="Quản lý")
    app.pack(fill="both", expand=True)
    root.mainloop()