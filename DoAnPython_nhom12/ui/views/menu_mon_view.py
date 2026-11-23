from datetime import date, datetime
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from services.monan_service import MonAnService
from services.menu_service import ExternalMenuService


class MenuMonView(tk.Frame):
    """Một view chia rõ 2 chức năng: 'Menu món ăn' và 'Kho món ăn'."""

    PANEL_RIGHT_WIDTH = 320
    PANEL_HEIGHT = 520

    def __init__(self, parent=None, role="Lễ tân", dish_service=None, api_service=None):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.dish_service = dish_service or MonAnService()
        self.api_service = api_service or ExternalMenuService()

        self.selected_dish_id = None
        self.selected_stock_dish_id = None
        self.checked_dish_ids = set()
        self.active_mode = "menu"

        self._build_ui()
        self.switch_mode("menu", notify_expired=True)

    def _build_ui(self):
        top_bar = tk.Frame(self, bg="white", padx=14, pady=10, bd=1, relief="solid")
        top_bar.pack(fill="x", padx=10, pady=(10, 6))

        self.lbl_title = tk.Label(
            top_bar,
            text="🍽️ CHỨC NĂNG: MENU MÓN ĂN",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#2c3e50",
        )
        self.lbl_title.pack(side="left")

        mode_box = tk.Frame(top_bar, bg="white")
        mode_box.pack(side="left", padx=20)

        self.btn_mode_menu = tk.Button(
            mode_box,
            text="📋 Menu món ăn",
            bg="#16a085",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=lambda: self.switch_mode("menu", notify_expired=False),
        )
        self.btn_mode_menu.pack(side="left", padx=(0, 6))

        self.btn_mode_kho = tk.Button(
            mode_box,
            text="📦 Kho món ăn",
            bg="#34495e",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=lambda: self.switch_mode("kho", notify_expired=True),
        )
        self.btn_mode_kho.pack(side="left")

        self.api_box = tk.Frame(top_bar, bg="white")
        self.api_box.pack(side="right", padx=(6, 0))

        tk.Label(
            self.api_box,
            text="SL món API:",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(side="left", padx=(0, 4))

        self.spn_api_limit = tk.Spinbox(
            self.api_box,
            from_=1,
            to=50,
            width=4,
            font=("Segoe UI", 9, "bold"),
            justify="center",
        )
        self.spn_api_limit.delete(0, tk.END)
        self.spn_api_limit.insert(0, "10")
        self.spn_api_limit.pack(side="left", padx=(0, 6), ipady=2)

        self.btn_sync_api = tk.Button(
            self.api_box,
            text="🌐 Đồng bộ API món",
            bg="#2980b9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=5,
            command=self.sync_api_menu,
        )
        self.btn_sync_api.pack(side="left")

        tk.Button(
            top_bar,
            text="🔄 Làm mới & Kiểm tra hạn",
            bg="#7f8c8d",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5,
            command=lambda: self.refresh_all(notify_expired=True),
        ).pack(side="right")

        self.content_container = tk.Frame(self, bg="#f5f6fa")
        self.content_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.frame_menu_func = tk.Frame(self.content_container, bg="#f5f6fa")
        self.frame_kho_func = tk.Frame(self.content_container, bg="#f5f6fa")

        self._build_menu_function()
        self._build_kho_function()

    def _create_split_panels(self, parent_frame):
        """Tạo cặp khung trái (bảng) và khung phải (form) có cùng kích thước chuẩn."""
        left = tk.Frame(
            parent_frame,
            bg="white",
            padx=10,
            pady=10,
            bd=1,
            relief="solid",
            height=self.PANEL_HEIGHT,
        )
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        left.pack_propagate(False)

        right = tk.Frame(
            parent_frame,
            bg="white",
            padx=12,
            pady=12,
            bd=1,
            relief="solid",
            width=self.PANEL_RIGHT_WIDTH,
            height=self.PANEL_HEIGHT,
        )
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        return left, right

    def _build_treeview_with_scroll(self, parent_frame, columns_spec):
        """Khởi tạo Treeview đồng bộ chiều cao và thanh cuộn dọc."""
        wrap = tk.Frame(parent_frame, bg="white")
        wrap.pack(fill="both", expand=True)

        cols = [c[0] for c in columns_spec]
        tree = ttk.Treeview(wrap, columns=cols, show="headings", selectmode="browse", height=18)

        for col_id, title, width, align in columns_spec:
            tree.heading(col_id, text=title)
            tree.column(col_id, width=width, anchor=align)

        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def switch_mode(self, mode: str, notify_expired: bool = False):
        self.active_mode = mode
        is_menu = mode == "menu"

        self.lbl_title.config(
            text="🍽️ CHỨC NĂNG: MENU MÓN ĂN" if is_menu else "📦 CHỨC NĂNG: KHO MÓN ĂN & HẠN SỬ DỤNG"
        )
        self.btn_mode_menu.config(bg="#16a085" if is_menu else "#34495e")
        self.btn_mode_kho.config(bg="#34495e" if is_menu else "#16a085")

        if is_menu:
            self.api_box.pack(side="right", padx=(6, 0))
            self.frame_kho_func.pack_forget()
            self.frame_menu_func.pack(fill="both", expand=True)
        else:
            self.api_box.pack_forget()
            self.frame_menu_func.pack_forget()
            self.frame_kho_func.pack(fill="both", expand=True)

        self.refresh_all(notify_expired=notify_expired)

    # ==================== CHỨC NĂNG 1: MENU MÓN ĂN ====================
    def _build_menu_function(self):
        left, right = self._create_split_panels(self.frame_menu_func)

        tick_bar = tk.Frame(left, bg="white")
        tick_bar.pack(fill="x", pady=(0, 6))

        for text, bg, cmd in (
            ("☑ Chọn tất cả", "#16a085", self._tick_all),
            ("☐ Bỏ tick tất cả", "#95a5a6", self._untick_all),
        ):
            tk.Button(
                tick_bar,
                text=text,
                bg=bg,
                fg="white",
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                padx=8,
                pady=3,
                command=cmd,
            ).pack(side="left", padx=(0, 4))

        tk.Button(
            tick_bar,
            text="🗑️ Xóa món đã tick",
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=3,
            command=self._delete_checked_dishes,
        ).pack(side="right")

        menu_cols = [
            ("tick", "Chọn", 48, "center"),
            ("id", "Mã", 72, "center"),
            ("name", "Tên món", 140, "center"),
            ("category", "Loại món", 90, "center"),
            ("price", "Giá (VNĐ)", 88, "center"),
            ("evaluate", "Đánh giá", 68, "center"),
            ("number", "SL còn", 58, "center"),
            ("expiration_date", "Hạn SD", 92, "center"),
            ("note", "Ghi chú", 150, "w"),
        ]
        self.tree_menu = self._build_treeview_with_scroll(left, menu_cols)
        self.tree_menu.bind("<<TreeviewSelect>>", self._on_select_menu_row)
        self.tree_menu.bind("<ButtonRelease-1>", self._on_tree_click)

        tk.Label(
            right,
            text="THÊM / SỬA / XÓA MÓN ĂN",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", pady=(0, 8))

        self.ent_name = self._add_labeled_entry(right, "Tên món (*):")
        self.cmb_category = self._add_labeled_combo(
            right, "Loại món (*):", ["Món ăn", "Đồ uống", "Khác", "Món chính", "Lẩu"], "Món ăn"
        )
        self.ent_price = self._add_labeled_entry(right, "Giá (VNĐ) (*):")
        self.ent_evaluate = self._add_labeled_entry(right, "Đánh giá:", "5.0")
        self.ent_image = self._add_labeled_entry(right, "Hình ảnh:")
        self.ent_note = self._add_labeled_entry(right, "Ghi chú:", pady_bottom=10)

        for text, bg, cmd in (
            ("➕ Thêm món (SL = 0)", "#2ecc71", self._handle_add_dish),
            ("✏️ Cập nhật món", "#f39c12", self._handle_update_dish),
            ("🗑️ Xóa món", "#e74c3c", self._handle_delete_dish),
            ("🧹 Làm mới form", "#95a5a6", self._clear_menu_form),
        ):
            tk.Button(
                right,
                text=text,
                bg=bg,
                fg="white",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                cursor="hand2",
                pady=5,
                command=cmd,
            ).pack(fill="x", pady=3)

    # ==================== CHỨC NĂNG 2: KHO MÓN ĂN ====================
    def _build_kho_function(self):
        left, right = self._create_split_panels(self.frame_kho_func)

        self.kho_alert_banner = tk.Frame(left, bg="#eafaf1", padx=10, pady=6, bd=1, relief="solid")
        self.kho_alert_banner.pack(fill="x", pady=(0, 6))

        self.lbl_kho_out_of_stock = tk.Label(
            self.kho_alert_banner,
            text="✅ Kho đang đủ số lượng cho tất cả món ăn",
            font=("Segoe UI", 9, "bold"),
            bg="#eafaf1",
            fg="#1e8449",
            anchor="w",
            justify="left",
        )
        self.lbl_kho_out_of_stock.pack(fill="x")

        self.kho_quick_chips_frame = tk.Frame(self.kho_alert_banner, bg="#fdecea")
        self.kho_quick_chips_frame.pack(fill="x", pady=(4, 0))
        self.kho_quick_chips_frame.pack_forget()

        kho_cols = [
            ("id", "Mã", 80, "center"),
            ("name", "Tên món", 160, "center"),
            ("category", "Loại món", 100, "center"),
            ("number", "SL tồn kho", 90, "center"),
            ("expiration_date", "Hạn sử dụng", 110, "center"),
            ("note", "Ghi chú", 180, "w"),
        ]
        self.tree_kho = self._build_treeview_with_scroll(left, kho_cols)
        self.tree_kho.tag_configure("out_of_stock", background="#fdecea", foreground="#c0392b")
        self.tree_kho.bind("<<TreeviewSelect>>", self._on_select_kho_row)

        tk.Label(
            right,
            text="CẬP NHẬT SỐ LƯỢNG & HẠN SD",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", pady=(0, 6))

        self.lbl_kho_selected = tk.Label(
            right,
            text="Chưa chọn món nào",
            font=("Segoe UI", 9, "bold"),
            bg="white",
            fg="#2980b9",
            wraplength=280,
            justify="left",
        )
        self.lbl_kho_selected.pack(anchor="w", pady=(0, 8))

        tk.Label(right, text="Ngày nhập / bắt đầu tính hạn:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.date_start = DateEntry(right, font=("Segoe UI", 9), date_pattern="yyyy-mm-dd")
        self.date_start.pack(fill="x", pady=(0, 6), ipady=2)

        tk.Label(right, text="Hạn sử dụng:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.date_exp = DateEntry(right, font=("Segoe UI", 9), date_pattern="yyyy-mm-dd")
        self.date_exp.pack(fill="x", pady=(0, 6), ipady=2)

        self.ent_qty = self._add_labeled_entry(right, "Số lượng:", "10", pady_bottom=10)

        for text, bg, mode in (
            ("📥 Cộng thêm số lượng & Lưu hạn SD", "#27ae60", False),
            ("📝 Đặt lại tổng số lượng & Lưu hạn SD", "#2980b9", True),
        ):
            tk.Button(
                right,
                text=text,
                bg=bg,
                fg="white",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                cursor="hand2",
                pady=6,
                command=lambda m=mode: self._handle_save_kho(replace_mode=m),
            ).pack(fill="x", pady=4)

    # ==================== HELPER UI ====================
    def _add_labeled_entry(self, parent, label_text, default="", pady_bottom=6):
        tk.Label(parent, text=label_text, bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        entry = tk.Entry(parent, font=("Segoe UI", 9), bd=1, relief="solid")
        if default:
            entry.insert(0, default)
        entry.pack(fill="x", pady=(0, pady_bottom), ipady=2)
        return entry

    def _add_labeled_combo(self, parent, label_text, values, default):
        tk.Label(parent, text=label_text, bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        combo = ttk.Combobox(parent, values=values, font=("Segoe UI", 9))
        combo.set(default)
        combo.pack(fill="x", pady=(0, 6), ipady=2)
        return combo

    def _set_entry(self, entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, str(value))

    def _parse_price(self):
        try:
            return int(float(self.ent_price.get().strip()))
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Giá món ăn phải là số hợp lệ.")
            return None

    def _collect_menu_form(self):
        price = self._parse_price()
        if price is None:
            return None
        return {
            "name": self.ent_name.get(),
            "price": price,
            "category": self.cmb_category.get(),
            "note": self.ent_note.get(),
            "evaluate": self.ent_evaluate.get(),
            "image": self.ent_image.get(),
        }

    # ==================== TICKBOX & API ====================
    def _get_api_limit(self) -> int:
        try:
            val = int(str(self.spn_api_limit.get()).strip())
            return max(1, min(50, val))
        except ValueError:
            return 10

    def _on_tree_click(self, event):
        if self.tree_menu.identify("region", event.x, event.y) != "cell":
            return
        if self.tree_menu.identify_column(event.x) != "#1":
            return
        row_id = self.tree_menu.identify_row(event.y)
        if not row_id:
            return
        vals = self.tree_menu.item(row_id, "values")
        if vals:
            dish_id = vals[1]
            if dish_id in self.checked_dish_ids:
                self.checked_dish_ids.remove(dish_id)
            else:
                self.checked_dish_ids.add(dish_id)
            self._populate_menu_tree(self.dish_service.load_dishes())

    def _tick_all(self):
        self.checked_dish_ids = {d.id for d in self.dish_service.load_dishes()}
        self._populate_menu_tree(self.dish_service.load_dishes())

    def _untick_all(self):
        self.checked_dish_ids.clear()
        self._populate_menu_tree(self.dish_service.load_dishes())

    def _delete_checked_dishes(self):
        if not self.checked_dish_ids:
            messagebox.showwarning("Chú ý", "Bạn chưa tick món nào để xóa.")
            return
        count = len(self.checked_dish_ids)
        if not messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa {count} món đã tick không?"):
            return

        deleted = 0
        for dish_id in list(self.checked_dish_ids):
            ok, _ = self.dish_service.delete_dish(dish_id)
            if ok:
                deleted += 1
                self.checked_dish_ids.discard(dish_id)

        self._clear_menu_form()
        self.refresh_all(notify_expired=False)
        messagebox.showinfo("Thành công", f"Đã xóa {deleted}/{count} món đã tick.")

    # ==================== DỮ LIỆU & SỰ KIỆN ====================
    def _populate_menu_tree(self, dishes):
        for row in self.tree_menu.get_children():
            self.tree_menu.delete(row)
        for d in dishes:
            tick_icon = "☑" if d.id in self.checked_dish_ids else "☐"
            self.tree_menu.insert(
                "",
                "end",
                values=(
                    tick_icon,
                    d.id,
                    d.name,
                    d.category,
                    f"{d.price:,}",
                    d.evaluate,
                    d.number,
                    d.expiration_date or "-",
                    d.note,
                ),
            )

    def _select_kho_dish_by_id(self, dish_id: str):
        for row_id in self.tree_kho.get_children():
            vals = self.tree_kho.item(row_id, "values")
            if vals and vals[0] == dish_id:
                self.tree_kho.selection_set(row_id)
                self.tree_kho.see(row_id)
                self._on_select_kho_row(None)
                self.ent_qty.focus_set()
                self.ent_qty.select_range(0, tk.END)
                break

    def _update_kho_out_of_stock_banner(self, dishes):
        if not hasattr(self, "lbl_kho_out_of_stock") or not self.lbl_kho_out_of_stock.winfo_exists():
            return

        for child in self.kho_quick_chips_frame.winfo_children():
            child.destroy()

        out_dishes = [d for d in dishes if int(getattr(d, "number", 0) or 0) <= 0]
        if not out_dishes:
            self.kho_alert_banner.config(bg="#eafaf1")
            self.lbl_kho_out_of_stock.config(
                text="✅ Kho đang đủ số lượng cho tất cả món ăn",
                bg="#eafaf1",
                fg="#1e8449",
            )
            self.kho_quick_chips_frame.pack_forget()
            return

        names_preview = ", ".join(f"{d.name} ({d.id})" for d in out_dishes[:6])
        extra = f" và +{len(out_dishes) - 6} món khác" if len(out_dishes) > 6 else ""
        self.kho_alert_banner.config(bg="#fdecea")
        self.lbl_kho_out_of_stock.config(
            text=f"⚠️ HẾT SỐ LƯỢNG ({len(out_dishes)} món) — Bấm vào món bên dưới để nhập thêm: {names_preview}{extra}",
            bg="#fdecea",
            fg="#c0392b",
        )
        self.kho_quick_chips_frame.config(bg="#fdecea")
        self.kho_quick_chips_frame.pack(fill="x", pady=(4, 0))

        for d in out_dishes[:10]:
            tk.Button(
                self.kho_quick_chips_frame,
                text=f"+ {d.name}",
                bg="#e74c3c",
                fg="white",
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                padx=6,
                pady=2,
                command=lambda did=d.id: self._select_kho_dish_by_id(did),
            ).pack(side="left", padx=(0, 4), pady=2)

    def _populate_kho_tree(self, dishes):
        for row in self.tree_kho.get_children():
            self.tree_kho.delete(row)
        self._update_kho_out_of_stock_banner(dishes)
        for d in dishes:
            qty = int(getattr(d, "number", 0) or 0)
            tags = ("out_of_stock",) if qty <= 0 else ()
            self.tree_kho.insert(
                "",
                "end",
                values=(d.id, d.name, d.category, qty, d.expiration_date or "-", d.note),
                tags=tags,
            )

    def refresh_all(self, notify_expired=False):
        expired_items = self.dish_service.check_and_expire_dishes()
        if notify_expired and expired_items:
            messagebox.showwarning(
                "Cảnh báo món hết hạn",
                "Các món sau đã hết hạn sử dụng và chuyển số lượng về 0:\n- " + "\n- ".join(expired_items),
            )

        dishes = self.dish_service.load_dishes()
        self._populate_menu_tree(dishes)
        self._populate_kho_tree(dishes)

    def sync_api_menu(self):
        limit = self._get_api_limit()
        result = self.api_service.fetch_and_save_menu(timeout=10, limit=limit)
        if result.get("ok"):
            added_count = 0
            for item in result.get("items", []):
                ok, _ = self.dish_service.create_dish(
                    name=item.get("name", ""),
                    price=item.get("price", 50000),
                    category=item.get("category", "Món ăn"),
                    note=item.get("note", "Đồng bộ từ API"),
                    evaluate=item.get("evaluate", "4.5"),
                    image=item.get("image", ""),
                )
                if ok:
                    added_count += 1
            self.refresh_all(notify_expired=False)
            messagebox.showinfo(
                "Đồng bộ API món",
                f"{result.get('message')}\nĐã chọn {limit} món từ API và thêm mới {added_count} món vào Menu.",
            )
        else:
            messagebox.showwarning("Đồng bộ API món", result.get("message", "Không thể đồng bộ API."))

    def _on_select_menu_row(self, _event):
        selected = self.tree_menu.selection()
        if not selected:
            return
        vals = self.tree_menu.item(selected[0], "values")
        self.selected_dish_id = vals[1]
        self._set_entry(self.ent_name, vals[2])
        self.cmb_category.set(vals[3])
        self._set_entry(self.ent_price, str(vals[4]).replace(",", ""))
        self._set_entry(self.ent_evaluate, vals[5])
        self._set_entry(self.ent_note, vals[8])

    def _on_select_kho_row(self, _event):
        selected = self.tree_kho.selection()
        if not selected:
            return
        vals = self.tree_kho.item(selected[0], "values")
        self.selected_stock_dish_id = vals[0]
        self.lbl_kho_selected.config(text=f"Đang chọn: [{vals[0]}] {vals[1]} | SL hiện tại: {vals[3]}")

        if vals[4] and vals[4] != "-":
            try:
                self.date_exp.set_date(datetime.strptime(vals[4], "%Y-%m-%d").date())
            except ValueError:
                self.date_exp.set_date(date.today())

    def _clear_menu_form(self):
        self.selected_dish_id = None
        self.ent_name.delete(0, tk.END)
        self.cmb_category.set("Món ăn")
        self.ent_price.delete(0, tk.END)
        self._set_entry(self.ent_evaluate, "5.0")
        self.ent_image.delete(0, tk.END)
        self.ent_note.delete(0, tk.END)

    def _handle_add_dish(self):
        form = self._collect_menu_form()
        if not form:
            return
        ok, msg = self.dish_service.create_dish(**form)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self._clear_menu_form()
            self.refresh_all(notify_expired=False)
        else:
            messagebox.showerror("Không thể thêm món", msg)

    def _handle_update_dish(self):
        if not self.selected_dish_id:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một món trong bảng trước khi sửa.")
            return
        form = self._collect_menu_form()
        if not form:
            return
        ok, msg = self.dish_service.update_dish(dish_id=self.selected_dish_id, **form)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.refresh_all(notify_expired=False)
        else:
            messagebox.showerror("Lỗi cập nhật", msg)

    def _handle_delete_dish(self):
        if not self.selected_dish_id:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một món trong bảng trước khi xóa.")
            return
        if not messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa món này không?"):
            return
        ok, msg = self.dish_service.delete_dish(self.selected_dish_id)
        if ok:
            self.checked_dish_ids.discard(self.selected_dish_id)
            messagebox.showinfo("Thành công", msg)
            self._clear_menu_form()
            self.refresh_all(notify_expired=False)
        else:
            messagebox.showerror("Lỗi xóa", msg)

    def _handle_save_kho(self, replace_mode: bool):
        if not self.selected_stock_dish_id:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một món trong bảng kho trước.")
            return
        try:
            qty = int(self.ent_qty.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Số lượng phải là số nguyên.")
            return

        if self.date_exp.get_date() < self.date_start.get_date():
            messagebox.showwarning("Chú ý", "Hạn sử dụng không được sớm hơn ngày bắt đầu tính hạn.")
            return

        ok, msg = self.dish_service.update_stock_and_expiry(
            dish_id=self.selected_stock_dish_id,
            added_qty=qty,
            expiration_date=self.date_exp.get_date().strftime("%Y-%m-%d"),
            replace_mode=replace_mode,
        )
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.refresh_all(notify_expired=False)
        else:
            messagebox.showerror("Cảnh báo kho", msg)