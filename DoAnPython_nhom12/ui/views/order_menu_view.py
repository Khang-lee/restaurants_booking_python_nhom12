import io
import os
import tkinter as tk
import urllib.request
from tkinter import ttk, messagebox
from controllers.order_controller import OrderController


class OrderMenuView(tk.Frame):
    def __init__(self, parent=None, table=None, on_close=None, *args, **kwargs):
        super().__init__(parent, bg="#f5f6fa", *args, **kwargs)
        self.table = table
        self.on_close = on_close
        self.controller = OrderController(table=table)
        self.timer_job = None
        self.notified_30min = False
        self._notified_expired_once = False
        self.cat_buttons = {}
        self._pil_image_cache = {}

        # Các biến lưu tham chiếu widget thông báo để cập nhật trực tiếp (tránh chập chờn)
        self._bell_content_box = None
        self._lbl_bell_msg = None
        self._btn_confirm_arrival = None

        self.setup_ui()
        self.start_order_timer()

    def handle_close(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

        self.controller.save_on_exit()
        if self.on_close:
            self.on_close()

    def destroy(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
        super().destroy()

    def start_order_timer(self):
        if self.winfo_exists():
            elapsed = self.controller.get_elapsed_time()
            start_t = getattr(self.table, 'start_time', '--:--:--')
            if start_t and len(str(start_t)) > 10:
                start_t = str(start_t).split(" ")[1]

            if hasattr(self, 'lbl_realtime_clock') and self.lbl_realtime_clock.winfo_exists():
                self.lbl_realtime_clock.config(text=f"🕒 Giờ vào: {start_t} | ⏱️ Đang dùng: {elapsed}")

            self.update_booking_bell_banner()

            self.timer_job = self.after(1000, self.start_order_timer)

    def update_booking_bell_banner(self):
        """Hiển thị và cập nhật thông tin lịch đặt (chống chập chờn, nhấp nháy hoàn toàn)"""
        if not hasattr(self, 'booking_alert_frame') or not self.booking_alert_frame.winfo_exists():
            return

        if self._bell_content_box is None or not self._bell_content_box.winfo_exists():
            for widget in self.booking_alert_frame.winfo_children():
                widget.destroy()

            self._bell_content_box = tk.Frame(self.booking_alert_frame, bg=self.booking_alert_frame.cget("bg"))
            self._bell_content_box.pack(fill="x", padx=5, pady=4)

            self._lbl_bell_msg = tk.Label(
                self._bell_content_box, text="",
                font=("Segoe UI", 9, "bold"), anchor="w"
            )
            self._lbl_bell_msg.pack(side="left", fill="x", expand=True)

            self._btn_confirm_arrival = tk.Button(
                self._bell_content_box, text="✅ Xác nhận khách đến", bg="#27ae60", fg="white",
                font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2", padx=8, pady=2
            )

        booking = self.controller.get_nearest_booking_info()

        if booking:
            diff = booking["diff_mins"]
            c_name = booking["customer_name"]
            b_time = booking["booking_time"]
            guests = booking["guests"]
            b_id = booking.get("booking_id")
            b_status = booking.get("status", "Đã xác nhận")

            if b_status == "Đang phục vụ":
                bg_color = "#d4efdf"
                msg_text = f"🟢 KHÁCH ĐANG DÙNG: '{c_name}' lúc {b_time} ({guests} khách)"
                fg_color = "#196f3d"
            elif 0 <= diff <= 30:
                bg_color = "#f9ebe9"
                msg_text = f"🔔 CẢNH BÁO: Khách '{c_name}' đặt lúc {b_time} ({guests} khách) - Còn {diff} phút!"
                fg_color = "#c0392b"

                if not self.notified_30min:
                    self.notified_30min = True
                    messagebox.showwarning(
                        "🔔 NHẮC LỊCH ĐẶT BÀN",
                        f"Bàn {getattr(self.table, 'name', 'này')} sắp có khách đặt tới!\n\n• Khách hàng: {c_name}\n• Số lượng: {guests} khách\n• Giờ hẹn: {b_time}\n(Còn lại khoảng {diff} phút)"
                    )
            elif diff < 0:
                bg_color = "#fcf3cf"
                msg_text = f"🔔 QUÁ GIỜ: Khách '{c_name}' lúc {b_time} ({guests} khách) - Quá {abs(diff)} phút!"
                fg_color = "#d35400"
            else:
                bg_color = "#e8f8f5"
                msg_text = f"🔔 Lịch đặt: Khách '{c_name}' lúc {b_time} ({guests} khách) - Còn {diff} phút"
                fg_color = "#16a085"

            self.booking_alert_frame.config(bg=bg_color)
            self._bell_content_box.config(bg=bg_color)
            self._lbl_bell_msg.config(text=msg_text, bg=bg_color, fg=fg_color)

            if b_status != "Đang phục vụ":
                self._btn_confirm_arrival.config(command=lambda bid=b_id: self.confirm_arrival(bid))
                if not self._btn_confirm_arrival.winfo_ismapped():
                    self._btn_confirm_arrival.pack(side="right", padx=5)
            else:
                if self._btn_confirm_arrival.winfo_ismapped():
                    self._btn_confirm_arrival.pack_forget()
        else:
            self.booking_alert_frame.config(bg="#f5f6fa")
            self._bell_content_box.config(bg="#f5f6fa")
            self._lbl_bell_msg.config(
                text="🔔 Không có lịch đặt bàn nào khác trong hôm nay",
                font=("Segoe UI", 8, "italic"), bg="#f5f6fa", fg="#95a5a6"
            )
            if self._btn_confirm_arrival.winfo_ismapped():
                self._btn_confirm_arrival.pack_forget()

    def confirm_arrival(self, booking_id):
        """Xử lý khi bấm nút Xác nhận khách đến"""
        success, msg = self.controller.confirm_customer_arrival(booking_id)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.update_booking_bell_banner()
            if hasattr(self, 'start_order_timer'):
                self.start_order_timer()
        else:
            messagebox.showerror("Lỗi", msg)

    def _load_dish_photo(self, img_path: str):
        """Tải ảnh món từ đường dẫn file cục bộ hoặc URL web (có cache)."""
        src = str(img_path or "").strip()
        if not src:
            return None

        try:
            from PIL import Image, ImageTk
        except ImportError:
            return None

        cache_key = (src, 42, 42)
        if cache_key in self._pil_image_cache:
            try:
                return ImageTk.PhotoImage(self._pil_image_cache[cache_key])
            except Exception:
                return None

        pil_img = None
        try:
            if src.startswith(("http://", "https://")):
                req = urllib.request.Request(
                    src,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    img_bytes = resp.read()
                pil_img = Image.open(io.BytesIO(img_bytes))
            elif os.path.exists(src):
                pil_img = Image.open(src)
        except Exception:
            return None

        if pil_img is None:
            return None

        try:
            resized = pil_img.convert("RGBA").resize((42, 42))
            self._pil_image_cache[cache_key] = resized
            return ImageTk.PhotoImage(resized)
        except Exception:
            return None

    def setup_ui(self):
        top_bar = tk.Frame(self, bg="white", padx=15, pady=10)
        top_bar.pack(fill="x", padx=10, pady=(10, 5))

        table_title = getattr(self.table, "name", "BÀN TRỐNG") if self.table else "BÀN TRỐNG"
        capacity_text = f" (👤 {getattr(self.table, 'capacity', 4)} chỗ)" if self.table else ""

        tk.Label(
            top_bar,
            text=f"🍽️ GỌI MÓN CHO: {str(table_title).upper()}{capacity_text}",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(side="left")

        if self.on_close:
            tk.Button(
                top_bar, text="⬅️ Quay lại Sơ đồ bàn (Tự động lưu)",
                bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"),
                relief="flat", cursor="hand2", padx=12, pady=5,
                command=self.handle_close
            ).pack(side="right")

        tk.Button(
            top_bar, text="🔄 Chuyển bàn", bg="#e67e22", fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=10, pady=5,
            command=self.open_transfer_dialog
        ).pack(side="right", padx=5)

        main_content = tk.Frame(self, bg="#f5f6fa")
        main_content.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = tk.Frame(main_content, bg="#f5f6fa")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=0)

        right_frame = tk.Frame(main_content, bg="white", width=460)
        right_frame.pack(side="right", fill="both", padx=(5, 0), pady=0)
        right_frame.pack_propagate(False)

        # ==================== CỘT TRÁI: MENU & DANH MỤC ====================
        cat_frame = tk.Frame(left_frame, bg="#2980b9", padx=4, pady=4)
        cat_frame.pack(fill="x", pady=(0, 5))

        categories = self.controller.get_categories_list()
        for cat in categories:
            btn = tk.Button(
                cat_frame, text=cat, font=("Segoe UI", 9, "bold"),
                bg="#3498db" if cat == "Tất cả" else "#2980b9", fg="white",
                relief="flat", cursor="hand2", padx=10, pady=5,
                command=lambda c=cat: self.filter_by_category(c)
            )
            btn.pack(side="left", padx=2)
            self.cat_buttons[cat] = btn

        search_frame = tk.Frame(left_frame, bg="white", padx=10, pady=8, bd=1, relief="solid")
        search_frame.pack(fill="x", pady=(0, 5))

        tk.Label(search_frame, text="🔍", bg="white", font=("Segoe UI", 11)).pack(side="left")
        self.txt_search = tk.Entry(search_frame, font=("Segoe UI", 10), bd=0, bg="white")
        self.txt_search.pack(side="left", fill="x", expand=True, padx=8)
        self.txt_search.bind("<KeyRelease>", lambda e: self.render_menu_cards())

        cards_container = tk.Frame(left_frame, bg="#f5f6fa")
        cards_container.pack(fill="both", expand=True, pady=(0, 5))

        self.canvas_menu = tk.Canvas(cards_container, bg="#f5f6fa", highlightthickness=0)
        scroll_menu = ttk.Scrollbar(cards_container, orient="vertical", command=self.canvas_menu.yview)

        self.grid_cards = tk.Frame(self.canvas_menu, bg="#f5f6fa")
        self.grid_cards.bind("<Configure>", lambda e: self.canvas_menu.configure(scrollregion=self.canvas_menu.bbox("all")))

        self.canvas_menu.create_window((0, 0), window=self.grid_cards, anchor="nw")
        self.canvas_menu.configure(yscrollcommand=scroll_menu.set)

        self.canvas_menu.pack(side="left", fill="both", expand=True)
        scroll_menu.pack(side="right", fill="y")

        self.render_menu_cards()

        # ==================== CỘT PHẢI: HÓA ĐƠN & CHUÔNG BÁO ====================
        header_right = tk.Frame(right_frame, bg="#34495e", padx=12, pady=10)
        header_right.pack(fill="x")

        tk.Label(
            header_right,
            text=f"📋 HÓA ĐƠN - {str(table_title).upper()}",
            font=("Segoe UI", 11, "bold"),
            fg="white", bg="#34495e"
        ).pack(side="left")

        self.lbl_realtime_clock = tk.Label(
            right_frame, text="🕒 Giờ vào: --:--:-- | ⏱️ Đang dùng: 00:00:00",
            font=("Segoe UI", 9, "bold"), bg="#f1f2f6", fg="#2c3e50", pady=6
        )
        self.lbl_realtime_clock.pack(fill="x", padx=8, pady=(4, 2))

        self.booking_alert_frame = tk.Frame(right_frame, bg="#f5f6fa", padx=5, pady=4, bd=1, relief="solid")
        self.booking_alert_frame.pack(fill="x", padx=8, pady=(0, 4))
        self.update_booking_bell_banner()

        order_list_container = tk.Frame(right_frame, bg="white", padx=5, pady=5)
        order_list_container.pack(fill="both", expand=True, padx=8, pady=5)

        self.canvas_order = tk.Canvas(order_list_container, bg="white", highlightthickness=0)
        scroll_order = ttk.Scrollbar(order_list_container, orient="vertical", command=self.canvas_order.yview)

        self.scrollable_order_items = tk.Frame(self.canvas_order, bg="white")
        self.scrollable_order_items.bind("<Configure>", lambda e: self.canvas_order.configure(scrollregion=self.canvas_order.bbox("all")))

        self.canvas_order.create_window((0, 0), window=self.scrollable_order_items, anchor="nw")
        self.canvas_order.configure(yscrollcommand=scroll_order.set)

        self.canvas_order.pack(side="left", fill="both", expand=True)
        scroll_order.pack(side="right", fill="y")

        total_frame = tk.Frame(right_frame, bg="#f8f9fa", padx=15, pady=8, bd=1, relief="solid")
        total_frame.pack(fill="x", padx=8, pady=6)

        tk.Label(total_frame, text="TỔNG CỘNG:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(side="left")
        self.lbl_total_amount = tk.Label(total_frame, text="0 VNĐ", font=("Segoe UI", 13, "bold"), bg="#f8f9fa", fg="#e74c3c")
        self.lbl_total_amount.pack(side="right")

        btn_footer = tk.Frame(right_frame, bg="white", padx=8, pady=6)
        btn_footer.pack(fill="x", padx=4)

        tk.Button(
            btn_footer, text="💳 TÍNH TIỀN & THANH TOÁN", bg="#e67e22", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=8,
            command=self.checkout
        ).pack(side="left", expand=True, fill="x", padx=2)

        self.update_order_display()

    def filter_by_category(self, cat_name):
        self.controller.selected_category = cat_name
        for c_key, btn in self.cat_buttons.items():
            if btn.winfo_exists():
                btn.config(bg="#3498db" if c_key == cat_name else "#2980b9")
        self.render_menu_cards()

    def render_menu_cards(self):
        for child in self.grid_cards.winfo_children():
            child.destroy()

        if self.controller.selected_category == "📅 Đặt bàn":
            bookings = self.controller.get_table_bookings()
            if not bookings:
                lbl = tk.Label(
                    self.grid_cards,
                    text="📭 Không có lịch đặt bàn nào cho bàn này",
                    font=("Segoe UI", 10, "italic"),
                    bg="#f5f6fa", fg="#7f8c8d"
                )
                lbl.pack(pady=40, padx=20)
                return

            for bk in bookings:
                card = tk.Frame(self.grid_cards, bg="white", bd=1, relief="solid", padx=12, pady=10)
                card.pack(fill="x", padx=5, pady=5)

                b_id = bk.get("booking_id", "N/A")
                c_name = bk.get("customer_name", "Khách")
                phone = bk.get("customer_phone", "N/A")
                guests = bk.get("guest_count", 1)
                b_date = bk.get("booking_date", "")
                b_time = bk.get("booking_time", "")
                status = bk.get("status", "Đã xác nhận")
                deposit = bk.get("deposit_amount", 0)

                tk.Label(card, text=f"📌 Mã đặt: {b_id} | Trạng thái: {status}", font=("Segoe UI", 10, "bold"), bg="white", fg="#2980b9", anchor="w").pack(fill="x")
                tk.Label(card, text=f"👤 Khách hàng: {c_name} (SĐT: {phone})", font=("Segoe UI", 9), bg="white", fg="#2c3e50", anchor="w").pack(fill="x", pady=2)
                tk.Label(card, text=f"👥 Số khách: {guests} người", font=("Segoe UI", 9), bg="white", fg="#2c3e50", anchor="w").pack(fill="x")
                tk.Label(card, text=f"🕒 Ngày giờ: {b_date} lúc {b_time}", font=("Segoe UI", 9, "bold"), bg="white", fg="#e67e22", anchor="w").pack(fill="x", pady=2)
                if deposit:
                    tk.Label(card, text=f"💵 Tiền cọc: {int(deposit):,} VNĐ", font=("Segoe UI", 9), bg="white", fg="#27ae60", anchor="w").pack(fill="x")
            return

        _, expired_items = self.controller.get_dishes_data()
        if expired_items and not self._notified_expired_once:
            self._notified_expired_once = True
            messagebox.showwarning(
                "Cảnh báo món hết hạn",
                "Các món sau đã hết hạn sử dụng và chuyển số lượng về 0:\n- " + "\n- ".join(expired_items),
            )

        search_kw = self.txt_search.get()
        filtered = self.controller.filter_menu(self.controller.selected_category, search_kw)

        cols = 3
        for idx, item in enumerate(filtered):
            r = idx // cols
            c = idx % cols

            stock_qty = self.controller.get_dish_stock_qty(item)
            is_out_of_stock = stock_qty <= 0

            card_bg = "#f2f4f4" if is_out_of_stock else "white"
            border_col = "#bdc3c7" if is_out_of_stock else "#dfe6e9"

            card = tk.Frame(
                self.grid_cards,
                bg=card_bg,
                bd=1,
                relief="solid",
                width=165,
                height=145,
                highlightbackground=border_col,
            )
            card.grid(row=r, column=c, padx=5, pady=5)
            card.pack_propagate(False)
            card.grid_propagate(False)

            price = item.get("price", 0)
            price_text = f"{price//1000}K" if price >= 1000 else f"{price}"
            badge = tk.Label(
                card,
                text=price_text,
                bg="#95a5a6" if is_out_of_stock else "#e74c3c",
                fg="white",
                font=("Segoe UI", 8, "bold"),
                padx=4,
            )
            badge.place(x=122, y=4)

            stock_badge = tk.Label(
                card,
                text="HẾT MÓN" if is_out_of_stock else f"SL: {stock_qty}",
                bg="#c0392b" if is_out_of_stock else "#27ae60",
                fg="white",
                font=("Segoe UI", 7, "bold"),
                padx=4,
            )
            stock_badge.place(x=4, y=4)

            img_path = item.get("image", "")
            img_tk = self._load_dish_photo(img_path)
            if img_tk is not None:
                card.img_ref = img_tk
                lbl_img = tk.Label(card, image=img_tk, bg=card_bg)
                lbl_img.pack(pady=(20, 2))
            else:
                lbl_img = tk.Label(card, text="🍲", font=("Segoe UI", 14), bg=card_bg)
                lbl_img.pack(pady=(18, 2))

            name_txt = str(item.get("name") or "")
            status_suffix = " [HẾT MÓN]" if is_out_of_stock else f" (Còn {stock_qty})"
            full_label_text = f"{name_txt}{status_suffix}"

            lbl_name = tk.Label(
                card,
                text=full_label_text,
                font=("Segoe UI", 8, "bold"),
                bg=card_bg,
                fg="#7f8c8d" if is_out_of_stock else "#2c3e50",
                wraplength=154,
                justify="center",
            )
            lbl_name.place(x=4, y=68, width=157, height=72)

            if is_out_of_stock:
                for widget in (card, badge, stock_badge, lbl_img, lbl_name):
                    widget.config(cursor="arrow")
            else:
                for widget in (card, badge, stock_badge, lbl_img, lbl_name):
                    widget.bind("<Button-1>", lambda e, it=item: self.add_item_to_order(it))
                    widget.config(cursor="hand2")

    def add_item_to_order(self, item):
        ok, msg = self.controller.add_item_to_order(item)
        if not ok:
            messagebox.showwarning("Thông báo", msg)
            self.render_menu_cards()
            return
        self.update_order_display()

    def update_order_display(self):
        for child in self.scrollable_order_items.winfo_children():
            child.destroy()

        if not self.controller.current_order:
            empty_frame = tk.Frame(self.scrollable_order_items, bg="white", pady=40)
            empty_frame.pack(fill="x")
            tk.Label(
                empty_frame,
                text="🛒 Chưa có món nào trong hóa đơn\nHãy chọn món từ menu bên trái",
                font=("Segoe UI", 9, "italic"),
                bg="white",
                fg="#b2bec3",
                justify="center"
            ).pack(fill="x")
        else:
            for idx, item in enumerate(self.controller.current_order):
                row = tk.Frame(self.scrollable_order_items, bg="white", bd=1, relief="solid")
                row.pack(fill="x", padx=4, pady=4)
                row.configure(highlightbackground="#dfe6e9")

                inner_frame = tk.Frame(row, bg="white", padx=10, pady=8)
                inner_frame.pack(fill="both", expand=True)

                left_info = tk.Frame(inner_frame, bg="white")
                left_info.pack(side="left", fill="x", expand=True)

                stock_qty = self.controller.get_dish_stock_qty(item)
                is_out = stock_qty <= 0
                status_tag = " [HẾT MÓN]" if is_out else f" (Kho còn: {stock_qty})"

                lbl_name = tk.Label(
                    left_info,
                    text=f"{item['name']}{status_tag}",
                    font=("Segoe UI", 10, "bold"),
                    bg="white",
                    fg="#c0392b" if is_out else "#2c3e50",
                    anchor="w",
                    wraplength=250,
                    justify="left",
                )
                lbl_name.pack(fill="x")

                lbl_unit = tk.Label(
                    left_info, text=f"Đơn giá: {item['price']:,}đ",
                    font=("Segoe UI", 8),
                    bg="white", fg="#b2bec3", anchor="w"
                )
                lbl_unit.pack(fill="x", pady=(2, 0))

                right_action = tk.Frame(inner_frame, bg="white")
                right_action.pack(side="right")

                sub_total = item["total"]
                lbl_total = tk.Label(
                    right_action, text=f"{sub_total:,}đ",
                    font=("Segoe UI", 10, "bold"),
                    bg="white", fg="#e74c3c", anchor="e"
                )
                lbl_total.pack(anchor="e", pady=(0, 4))

                ctrl_bar = tk.Frame(right_action, bg="white")
                ctrl_bar.pack(anchor="e")

                tk.Button(
                    ctrl_bar, text="-", bg="#f1f2f6", fg="#2c3e50",
                    font=("Segoe UI", 9, "bold"), width=2, height=1,
                    relief="flat", cursor="hand2",
                    command=lambda i=idx: self.decrease_qty(i)
                ).pack(side="left", padx=1)

                tk.Label(
                    ctrl_bar, text=str(item["qty"]),
                    font=("Segoe UI", 9, "bold"),
                    bg="#f8f9fa", fg="#2c3e50", width=3,
                    relief="solid", bd=1
                ).pack(side="left", padx=2)

                btn_plus = tk.Button(
                    ctrl_bar,
                    text="+",
                    bg="#bdc3c7" if is_out else "#f1f2f6",
                    fg="#7f8c8d" if is_out else "#2c3e50",
                    font=("Segoe UI", 9, "bold"),
                    width=2,
                    height=1,
                    relief="flat",
                    cursor="arrow" if is_out else "hand2",
                    state="disabled" if is_out else "normal",
                    command=lambda i=idx: self.increase_qty(i),
                )
                btn_plus.pack(side="left", padx=1)

                tk.Button(
                    ctrl_bar, text="🗑", bg="#ffeaa7", fg="#d63031",
                    font=("Segoe UI", 9), width=2, height=1,
                    relief="flat", cursor="hand2",
                    command=lambda i=idx: self.remove_single_item(i)
                ).pack(side="left", padx=(6, 0))

        total_amount = self.controller.calculate_total()
        self.lbl_total_amount.config(text=f"{total_amount:,} VNĐ")

    def increase_qty(self, idx):
        ok, msg = self.controller.increase_item_qty(idx)
        if not ok:
            messagebox.showwarning("Thông báo", msg)
            self.render_menu_cards()
            self.update_order_display()
            return
        self.update_order_display()

    def decrease_qty(self, idx):
        self.controller.decrease_item_qty(idx)
        self.update_order_display()

    def remove_single_item(self, idx):
        self.controller.remove_item(idx)
        self.update_order_display()

    def open_transfer_dialog(self):
        """Hộp thoại popup chọn bàn để chuyển sang"""
        dialog = tk.Toplevel(self)
        dialog.title("Chuyển Bàn")
        dialog.geometry("320x180")
        dialog.configure(bg="white")
        dialog.grab_set()

        tk.Label(dialog, text="Chọn bàn muốn chuyển đến:", font=("Segoe UI", 10, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 5))

        table_options = self.controller.get_transferable_table_names()

        combo_target = ttk.Combobox(dialog, values=table_options, font=("Segoe UI", 10), state="readonly")
        combo_target.pack(fill="x", padx=20, pady=10)
        if table_options:
            combo_target.current(0)

        def confirm_transfer():
            target_name = combo_target.get().strip()
            if not target_name:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn bàn đích hợp lệ!")
                return

            success, msg = self.controller.transfer_table(target_name)
            if success:
                messagebox.showinfo("Thành công", msg)
                dialog.destroy()
                if self.on_close:
                    self.on_close()
            else:
                messagebox.showerror("Lỗi", msg)

        tk.Button(
            dialog, text="Xác nhận chuyển", bg="#e67e22", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=6, cursor="hand2",
            command=confirm_transfer
        ).pack(pady=10)

    def checkout(self):
        success, msg = self.controller.checkout()
        if not success:
            messagebox.showwarning("Cảnh báo", msg)
            return

        self.render_menu_cards()
        self.update_order_display()
        messagebox.showinfo("Thành công", f"Thanh toán thành công hóa đơn {msg}!")
        if self.on_close:
            self.handle_close()