import tkinter as tk
from tkinter import messagebox, ttk
from controllers.floorplan_controller import FloorplanController
from ui.views.order_menu_view import OrderMenuView


class FloorplanView(tk.Frame):
    THEME_MAP = {
        "Trống": {"bg": "#ffffff", "header": "#7f8c8d", "border": "#bdc3c7", "text_hdr": "#ffffff", "text_body": "#2c3e50", "badge_bg": "#ecf0f1", "badge_fg": "#7f8c8d"},
        "Đặt hôm nay": {"bg": "#fef9e7", "header": "#f39c12", "border": "#f1c40f", "text_hdr": "#ffffff", "text_body": "#b7950b", "badge_bg": "#fcf3cf", "badge_fg": "#b7950b"},
        "Đã đặt": {"bg": "#fffaf0", "header": "#e67e22", "border": "#f39c12", "text_hdr": "#ffffff", "text_body": "#d35400", "badge_bg": "#fdebd0", "badge_fg": "#e67e22"},
        "Đang phục vụ": {"bg": "#f0fff4", "header": "#2ecc71", "border": "#27ae60", "text_hdr": "#ffffff", "text_body": "#1e8449", "badge_bg": "#1e8449", "badge_fg": "#ffffff"}
    }
    GRID_SIZE = 20

    def __init__(self, parent, role="Lễ tân", open_booking_callback=None):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.open_booking_callback = open_booking_callback
        self.controller = FloorplanController(role=role)
        self.is_edit_mode = False
        self.drag_data = {"x": 0, "y": 0, "item": None, "table": None}
        self.timer_job = None

        self.setup_ui()
        self.draw_tables()
        
        # Kiểm tra nhắc lịch trước 30 phút
        reminders = self.controller.check_reminders()
        if reminders:
            messagebox.showinfo("Nhắc lịch hệ thống", "🔔 KHÁCH ĐẶT SẮP ĐẾN TRONG 30 PHÚT:\n\n" + "\n\n".join(reminders))

        # Kích hoạt bộ đếm thời gian thực theo giây
        self.start_live_timer()

    def destroy(self):
        """Hủy timer và tự động lưu dữ liệu order đang mở trước khi thoát hẳn view"""
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
            
        self.force_close_order()
        super().destroy()

    def start_live_timer(self):
        """Cập nhật giao diện sơ đồ bàn theo thời gian thực mỗi giây"""
        if self.winfo_exists():
            if not self.is_edit_mode and hasattr(self, 'floorplan_container') and self.floorplan_container.winfo_ismapped():
                # Load lại data ngầm từ file để đồng bộ thời gian thực tốt nhất
                self.controller.load_data()
                self.draw_tables()
            self.timer_job = self.after(1000, self.start_live_timer)

    def setup_ui(self):
        self.floorplan_container = tk.Frame(self, bg="#f5f6fa")
        self.floorplan_container.pack(fill="both", expand=True)

        top_frame = tk.Frame(self.floorplan_container, bg="white", padx=15, pady=12)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="📌 SƠ ĐỒ MẶT BẰNG BÀN", font=("Segoe UI", 13, "bold"), bg="white", fg="#2c3e50").pack(side="left")
        tk.Label(top_frame, text=" | Khu vực:", bg="white", font=("Segoe UI", 10)).pack(side="left", padx=(10, 2))

        areas = ["Tất cả"] + self.controller.get_areas()
        self.cbo_area = ttk.Combobox(top_frame, values=areas, state="readonly", width=12, font=("Segoe UI", 9))
        self.cbo_area.set("Tất cả")
        self.cbo_area.pack(side="left", padx=5)
        self.cbo_area.bind("<<ComboboxSelected>>", lambda e: self.on_area_changed())

        self.btn_add = tk.Button(top_frame, text="➕ Thêm Bàn", bg="#2ecc71", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10, command=self.add_new_table)
        self.btn_save = tk.Button(top_frame, text="💾 Lưu Sơ Đồ", bg="#3498db", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10, command=self.save_data)

        legend = tk.Frame(top_frame, bg="white")
        legend.pack(side="right")
        for status, color in [("Trống", "#7f8c8d"), ("Đặt hôm nay", "#f39c12"), ("Đang phục vụ", "#2ecc71")]:
            tk.Label(legend, text="●", fg=color, bg="white", font=("Segoe UI", 12)).pack(side="left", padx=(10, 2))
            tk.Label(legend, text=status, bg="white", font=("Segoe UI", 9, "bold"), fg="#34495e").pack(side="left")

        canvas_wrap = tk.Frame(self.floorplan_container, bg="#eaeded", padx=2, pady=2)
        canvas_wrap.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_wrap, bg="#f8f9fa", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.order_container = tk.Frame(self, bg="#f5f6fa")

    def force_close_order(self):
        """Buộc đóng bảng order, tự động lưu dữ liệu và quay về sơ đồ bàn (Dùng khi chuyển tab hoặc bấm thoát)"""
        for widget in self.order_container.winfo_children():
            if hasattr(widget, 'controller') and hasattr(widget.controller, 'save_on_exit'):
                widget.controller.save_on_exit()
            widget.destroy()
            
        self.order_container.pack_forget()
        if hasattr(self, 'floorplan_container'):
            self.floorplan_container.pack(fill="both", expand=True)
            self.controller.load_data()
            self.draw_tables()

    def open_embedded_order_view(self, table):
        """Mở giao diện Order nhúng trực tiếp"""
        self.floorplan_container.pack_forget()
        
        for widget in self.order_container.winfo_children():
            widget.destroy()
            
        def close_order():
            self.force_close_order()
            
        order_view = OrderMenuView(self.order_container, table=table, on_close=close_order)
        order_view.pack(fill="both", expand=True)
        self.order_container.pack(fill="both", expand=True)

    def on_area_changed(self):
        area = self.cbo_area.get()
        if area == "Tất cả" or self.role != "Quản lý":
            self.is_edit_mode = False
            self.btn_save.pack_forget()
            self.btn_add.pack_forget()
        else:
            self.is_edit_mode = True
            self.btn_save.pack(side="left", padx=5)
            self.btn_add.pack(side="left", padx=5)
        self.draw_tables()

    def add_new_table(self):
        area = self.cbo_area.get()
        if area == "Tất cả": return
        new_t = self.controller.add_table(area)
        self.draw_tables()
        messagebox.showinfo("Thêm bàn", f"Đã thêm '{new_t.name}' vào {area}.")

    def save_data(self):
        if self.controller.save_data():
            messagebox.showinfo("Thành công", "Đã lưu sơ đồ bàn!")

    def create_rounded_rect(self, x1, y1, x2, y2, radius=12, **kwargs):
        points = [
            x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius,
            x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def draw_tables(self):
        if not self.winfo_exists(): return
        self.canvas.delete("all")
        area, w, h = self.cbo_area.get(), 130, 95

        if area == "Tất cả":
            areas = self.controller.get_areas()
            curr_y = 30
            for a in areas:
                self.canvas.create_text(40, curr_y, text=f"📍 {a.upper()}", anchor="w", font=("Segoe UI", 12, "bold"), fill="#2c3e50")
                self.canvas.create_line(40, curr_y + 16, 780, curr_y + 16, fill="#dcdde1", width=1.5)
                
                a_tables = [t for t in self.controller.tables if t.area == a]
                for idx, table in enumerate(a_tables):
                    self.render_single_table(table, 40 + (idx % 5) * 150, curr_y + 35 + (idx // 5) * 115, w, h)
                curr_y += 35 + (((len(a_tables) - 1) // 5) + 1 if a_tables else 1) * 115 + 25
        else:
            if self.is_edit_mode:
                for x in range(0, self.canvas.winfo_width() or 1000, self.GRID_SIZE):
                    for y in range(0, self.canvas.winfo_height() or 700, self.GRID_SIZE):
                        self.canvas.create_oval(x-1, y-1, x+1, y+1, fill="#bdc3c7", outline="", tags="grid")
            for t in [tb for tb in self.controller.tables if tb.area == area]:
                self.render_single_table(t, t.x, t.y, w, h)

    def render_single_table(self, table, x, y, w, h):
        display_status = self.controller.get_table_display_status(table)
        theme = self.THEME_MAP.get(display_status, self.THEME_MAP["Trống"])
        tag = f"table_{table.id}"

        self.create_rounded_rect(x + 3, y + 3, x + w + 3, y + h + 3, radius=12, fill="#d6dbdf", outline="", tags=(tag, "table_group"))
        border = "#e74c3c" if self.is_edit_mode else theme["border"]
        card_id = self.create_rounded_rect(x, y, x + w, y + h, radius=12, fill=theme["bg"], outline=border, width=2, tags=(tag, "table_group"))

        self.create_rounded_rect(x, y, x + w, y + 28, radius=10, fill=theme["header"], outline="", tags=(tag, "table_group"))
        self.canvas.create_rectangle(x, y + 14, x + w, y + 28, fill=theme["header"], outline="", tags=(tag, "table_group"))
        self.canvas.create_text(x + w / 2, y + 14, text=table.name, fill=theme["text_hdr"], font=("Segoe UI", 10, "bold"), tags=(tag, "table_group"))
        self.canvas.create_text(x + w / 2, y + 45, text=f"👤 {table.capacity} chỗ", fill=theme["text_body"], font=("Segoe UI", 9), tags=(tag, "table_group"))

        if self.is_edit_mode:
            status_text, b_bg, b_fg = "↔️ Di chuyển", "#ebedef", "#2c3e50"
        else:
            if table.status == "Đang phục vụ":
                timer = self.controller.calculate_elapsed_time(table.start_time)
                status_text = f"⏱️ {timer}" if timer else "Đang phục vụ"
            elif display_status == "Đặt hôm nay":
                status_text = "Đặt hôm nay"
            else:
                status_text = table.status
            b_bg, b_fg = theme["badge_bg"], theme["badge_fg"]

        self.create_rounded_rect(x + 12, y + 62, x + w - 12, y + 84, radius=8, fill=b_bg, outline="", tags=(tag, "table_group"))
        self.canvas.create_text(x + w / 2, y + 73, text=status_text, fill=b_fg, font=("Segoe UI", 8, "bold" if table.status == "Đang phục vụ" else "normal"), tags=(tag, "table_group"))

        self.canvas.tag_bind(tag, "<Enter>", lambda e: not self.is_edit_mode and (self.canvas.itemconfig(card_id, outline="#2980b9", width=3), self.canvas.config(cursor="hand2")))
        self.canvas.tag_bind(tag, "<Leave>", lambda e: not self.is_edit_mode and (self.canvas.itemconfig(card_id, outline=theme["border"], width=2), self.canvas.config(cursor="")))
        self.canvas.tag_bind(tag, "<Double-Button-1>", lambda e, t=table: self.open_edit_table_dialog(t) if self.is_edit_mode else self.open_embedded_order_view(t))
        self.canvas.tag_bind(tag, "<ButtonPress-1>", lambda e, tg=tag, t=table: self.is_edit_mode and self.drag_update(e, tg, t, start=True))
        self.canvas.tag_bind(tag, "<B1-Motion>", lambda e: self.is_edit_mode and self.drag_update(e))
        self.canvas.tag_bind(tag, "<ButtonRelease-1>", lambda e: self.is_edit_mode and self.drag_update(e, stop=True))

    def drag_update(self, event, tag=None, table=None, start=False, stop=False):
        if start:
            self.drag_data.update({"item": tag, "x": event.x, "y": event.y, "table": table, "original_x": table.x, "original_y": table.y})
        elif stop and self.drag_data["table"]:
            curr = self.drag_data["table"]
            bbox = self.canvas.bbox(self.drag_data["item"])
            if bbox:
                nx = max(0, round(bbox[0] / self.GRID_SIZE) * self.GRID_SIZE)
                ny = max(0, round(bbox[1] / self.GRID_SIZE) * self.GRID_SIZE)
                overlap = self.controller.is_overlapping(curr, nx, ny)
                if overlap:
                    messagebox.showwarning("Cảnh báo", "Vị trí bị đè lên bàn khác!")
                    curr.x, curr.y = self.drag_data["original_x"], self.drag_data["original_y"]
                else:
                    curr.x, curr.y = nx, ny
                self.draw_tables()
            self.drag_data.update({"item": None, "table": None})
        elif self.drag_data["item"]:
            self.canvas.move(self.drag_data["item"], event.x - self.drag_data["x"], event.y - self.drag_data["y"])
            self.drag_data.update({"x": event.x, "y": event.y})

    def open_edit_table_dialog(self, table):
        dialog = tk.Toplevel(self)
        dialog.title(f"⚙️ CẤU HÌNH BÀN - {table.name}")
        dialog.geometry("360x300")
        dialog.configure(bg="white")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="THÔNG TIN BÀN", font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 10))
        f_in = tk.Frame(dialog, bg="white")
        f_in.pack(fill="both", expand=True, padx=20)

        tk.Label(f_in, text="Tên bàn (*):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        txt_name = tk.Entry(f_in, width=25, font=("Segoe UI", 10))
        txt_name.insert(0, table.name)
        txt_name.grid(row=0, column=1, pady=8, padx=5)

        tk.Label(f_in, text="Khu vực (*):", bg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        txt_area = tk.Entry(f_in, width=25, font=("Segoe UI", 10))
        txt_area.insert(0, table.area)
        txt_area.grid(row=1, column=1, pady=8, padx=5)

        tk.Label(f_in, text="Sức chứa:", bg="white", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        spn_cap = tk.Spinbox(f_in, from_=1, to=100, width=23, font=("Segoe UI", 10))
        spn_cap.delete(0, "end")
        spn_cap.insert(0, table.capacity)
        spn_cap.grid(row=2, column=1, pady=8, padx=5)

        def save():
            name, area = txt_name.get().strip(), txt_area.get().strip()
            if not name or not area:
                return messagebox.showerror("Lỗi", "Không được để trống!", parent=dialog)
            try:
                cap = int(spn_cap.get())
                if cap <= 0: raise ValueError
            except:
                return messagebox.showerror("Lỗi", "Sức chứa phải lớn hơn 0!", parent=dialog)

            if any(t.id != table.id and t.name.lower() == name.lower() for t in self.controller.tables):
                return messagebox.showwarning("Cảnh báo", f"Tên bàn '{name}' đã tồn tại!", parent=dialog)

            table.name, table.area, table.capacity = name, area, cap
            self.cbo_area["values"] = ["Tất cả"] + self.controller.get_areas()
            self.cbo_area.set(area)
            self.on_area_changed()
            self.controller.save_data()
            messagebox.showinfo("Thành công", "Đã cập nhật!", parent=dialog)
            dialog.destroy()

        def delete():
            if table.status != "Trống":
                return messagebox.showerror("Lỗi", "Bàn đang có khách hoặc đã đặt, không thể xóa!", parent=dialog)
            if messagebox.askyesno("Xác nhận", f"Xóa vĩnh viễn '{table.name}'?", parent=dialog):
                self.controller.tables.remove(table)
                self.controller.save_data()
                self.cbo_area["values"] = ["Tất cả"] + self.controller.get_areas()
                if self.cbo_area.get() not in self.cbo_area["values"]:
                    self.cbo_area.set("Tất cả")
                self.on_area_changed()
                messagebox.showinfo("Thành công", "Đã xóa bàn!", parent=dialog)
                dialog.destroy()

        btn_f = tk.Frame(dialog, bg="white")
        btn_f.pack(fill="x", padx=20, pady=(10, 20))
        tk.Button(btn_f, text="💾 Lưu", bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"), command=save, pady=5).pack(side="left", expand=True, fill="x", padx=(0, 5))
        tk.Button(btn_f, text="🗑️ Xóa", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), command=delete, pady=5).pack(side="right", expand=True, fill="x", padx=(5, 0))