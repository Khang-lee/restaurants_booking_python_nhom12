import json
import os
import uuid
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class OrderMenuView(tk.Frame):
    def __init__(self, parent=None, table=None, on_close=None, *args, **kwargs):
        super().__init__(parent, bg="#dcdde1", *args, **kwargs)
        self.table = table
        self.on_close = on_close

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "data"))
        if not os.path.exists(data_dir):
            data_dir = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data"))

        self.MENU_FILE = os.path.join(data_dir, "menumonan.json")
        self.TABLE_FILE = os.path.join(data_dir, "tables.json")
        self.BILL_FILE = os.path.join(data_dir, "bills.json")

        self.menu_items = []
        self.current_order = []

        self.load_menu_data()
        self.load_current_table_orders()
        self.setup_ui()

    def load_menu_data(self):
        if os.path.exists(self.MENU_FILE):
            try:
                with open(self.MENU_FILE, "r", encoding="utf-8") as f:
                    self.menu_items = json.load(f)
            except Exception as e:
                print(f"Lỗi đọc file menu: {e}")

    def load_current_table_orders(self):
        if self.table and hasattr(self.table, 'orders') and self.table.orders:
            self.current_order = [dict(item) for item in self.table.orders]
        else:
            self.current_order = []

    def setup_ui(self):
        left_frame = tk.Frame(self, bg="#f5f6fa", width=550)
        left_frame.pack(side="left", fill="both", expand=True, padx=(5, 2), pady=5)

        right_frame = tk.Frame(self, bg="white", width=420)
        right_frame.pack(side="right", fill="both", padx=(2, 5), pady=5)

        # 1. Thanh Lọc Danh Mục
        cat_frame = tk.Frame(left_frame, bg="#2980b9", padx=3, pady=3)
        cat_frame.pack(fill="x", padx=5, pady=(5, 0))

        self.selected_category = "Tất cả"
        categories = ["Tất cả", "Món ăn", "Đồ uống", "Khác"]
        for cat in categories:
            btn = tk.Button(
                cat_frame, text=cat, font=("Segoe UI", 9, "bold"),
                bg="#3498db" if cat == "Tất cả" else "#2980b9", fg="white",
                relief="flat", cursor="hand2", padx=10, pady=4,
                command=lambda c=cat: self.filter_by_category(c)
            )
            btn.pack(side="left", padx=2)

        # 2. Ô Tìm Kiếm Món
        search_frame = tk.Frame(left_frame, bg="white", padx=8, pady=6)
        search_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(search_frame, text="🔍", bg="white", font=("Segoe UI", 11)).pack(side="left")
        self.txt_search = tk.Entry(search_frame, font=("Segoe UI", 10), bd=0, bg="white")
        self.txt_search.pack(side="left", fill="x", expand=True, padx=5)
        self.txt_search.bind("<KeyRelease>", lambda e: self.render_menu_cards())

        # 3. Danh Sách Thẻ Món Ăn
        cards_container = tk.Frame(left_frame, bg="#f5f6fa")
        cards_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self.canvas_menu = tk.Canvas(cards_container, bg="#f5f6fa", highlightthickness=0)
        scroll_menu = ttk.Scrollbar(cards_container, orient="vertical", command=self.canvas_menu.yview)
        
        self.grid_cards = tk.Frame(self.canvas_menu, bg="#f5f6fa")
        self.grid_cards.bind("<Configure>", lambda e: self.canvas_menu.configure(scrollregion=self.canvas_menu.bbox("all")))
        
        self.canvas_menu.create_window((0, 0), window=self.grid_cards, anchor="nw")
        self.canvas_menu.configure(yscrollcommand=scroll_menu.set)

        self.canvas_menu.pack(side="left", fill="both", expand=True)
        scroll_menu.pack(side="right", fill="y")

        self.render_menu_cards()

        # ==========================================
        # CỘT PHẢI: HÓA ĐƠN & THAO TÁC
        # ==========================================
        header_right = tk.Frame(right_frame, bg="#34495e", padx=10, pady=10)
        header_right.pack(fill="x")

        table_title = self.table.name if self.table else "BÀN CHỌN"
        tk.Label(header_right, text=f"📋 HÓA ĐƠN - {table_title.upper()}", font=("Segoe UI", 11, "bold"), fg="white", bg="#34495e").pack(side="left")
        
        if self.table:
            tk.Label(header_right, text=f"👤 {self.table.capacity} chỗ", font=("Segoe UI", 9), fg="#bdc3c7", bg="#34495e").pack(side="right")

        table_order_frame = tk.Frame(right_frame, bg="white", padx=5, pady=5)
        table_order_frame.pack(fill="both", expand=True)

        cols = ("name", "qty", "price", "total")
        self.tree_order = ttk.Treeview(table_order_frame, columns=cols, show="headings", height=7)
        
        self.tree_order.heading("name", text="Tên món")
        self.tree_order.heading("qty", text="SL")
        self.tree_order.heading("price", text="Đơn giá")
        self.tree_order.heading("total", text="Thành tiền")

        self.tree_order.column("name", width=130)
        self.tree_order.column("qty", width=40, anchor="center")
        self.tree_order.column("price", width=75, anchor="e")
        self.tree_order.column("total", width=85, anchor="e")

        self.tree_order.bind("<<TreeviewSelect>>", self.on_order_item_selected)

        scroll_tree = ttk.Scrollbar(table_order_frame, orient="vertical", command=self.tree_order.yview)
        self.tree_order.configure(yscroll=scroll_tree.set)

        self.tree_order.pack(side="left", fill="both", expand=True)
        scroll_tree.pack(side="right", fill="y")

        # Khung preview ảnh và thông tin món khi chọn ở hóa đơn
        self.preview_frame = tk.Frame(right_frame, bg="#f8f9fa", height=65, padx=10, pady=5, bd=1, relief="solid")
        self.preview_frame.pack(fill="x", padx=5, pady=2)
        self.preview_frame.pack_propagate(False)

        self.lbl_preview_img = tk.Label(self.preview_frame, text="🍲", font=("Segoe UI", 16), bg="#f8f9fa")
        self.lbl_preview_img.pack(side="left", padx=5)

        self.lbl_preview_text = tk.Label(self.preview_frame, text="Nhấn chọn món trong bảng trên\nđể xem ảnh & thao tác nhanh", font=("Segoe UI", 8, "italic"), bg="#f8f9fa", fg="#7f8c8d", anchor="w")
        self.lbl_preview_text.pack(side="left", fill="x", expand=True, padx=5)

        action_bar = tk.Frame(right_frame, bg="#ecf0f1", padx=10, pady=5)
        action_bar.pack(fill="x")

        tk.Button(action_bar, text="➕ Tăng", bg="#2ecc71", fg="white", font=("Segoe UI", 9, "bold"), command=self.increase_item_qty, relief="flat", padx=8).pack(side="left", padx=2)
        tk.Button(action_bar, text="➖ Giảm", bg="#f39c12", fg="white", font=("Segoe UI", 9, "bold"), command=self.decrease_item_qty, relief="flat", padx=8).pack(side="left", padx=2)
        tk.Button(action_bar, text="🗑️ Xóa món", bg="#e74c3c", fg="white", font=("Segoe UI", 9, "bold"), command=self.remove_item, relief="flat", padx=8).pack(side="left", padx=2)

        total_frame = tk.Frame(right_frame, bg="#f8f9fa", padx=15, pady=10, bd=1, relief="solid")
        total_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(total_frame, text="TỔNG CỘNG:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(side="left")
        self.lbl_total_amount = tk.Label(total_frame, text="0 VNĐ", font=("Segoe UI", 14, "bold"), bg="#f8f9fa", fg="#e74c3c")
        self.lbl_total_amount.pack(side="right")

        btn_footer = tk.Frame(right_frame, bg="white", padx=10, pady=10)
        btn_footer.pack(fill="x")

        tk.Button(
            btn_footer, text="💾 LƯU / ĐÓN KHÁCH", bg="#27ae60", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=8,
            command=self.save_order_and_serve
        ).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(
            btn_footer, text="💳 TÍNH TIỀN", bg="#e67e22", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=8,
            command=self.checkout
        ).pack(side="left", expand=True, fill="x", padx=2)

        if self.on_close:
            tk.Button(
                btn_footer, text="❌ THOÁT", bg="#95a5a6", fg="white",
                font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", pady=8,
                command=self.on_close
            ).pack(side="left", expand=True, fill="x", padx=2)

        self.update_order_table()

    def filter_by_category(self, cat_name):
        self.selected_category = cat_name
        self.render_menu_cards()

    def render_menu_cards(self):
        for child in self.grid_cards.winfo_children():
            child.destroy()

        search_kw = self.txt_search.get().strip().lower()
        
        filtered = []
        for item in self.menu_items:
            match_cat = (self.selected_category == "Tất cả") or (item.get("category") == self.selected_category)
            match_kw = search_kw in item.get("name", "").lower()
            if match_cat and match_kw:
                filtered.append(item)

        cols = 3
        for idx, item in enumerate(filtered):
            r = idx // cols
            c = idx % cols

            card = tk.Frame(self.grid_cards, bg="white", bd=1, relief="solid", width=150, height=130)
            card.grid(row=r, column=c, padx=6, pady=6)
            card.pack_propagate(False)

            price = item.get("price", 0)
            price_text = f"{price//1000}K" if price >= 1000 else f"{price}"
            badge = tk.Label(card, text=price_text, bg="#e74c3c", fg="white", font=("Segoe UI", 8, "bold"), padx=5)
            badge.place(x=105, y=5)

            img_path = item.get("image", "")
            img_tk = None
            if img_path and os.path.exists(img_path):
                try:
                    from PIL import Image, ImageTk
                    pil_img = Image.open(img_path).resize((55, 55))
                    img_tk = ImageTk.PhotoImage(pil_img)
                    card.img_ref = img_tk
                except Exception:
                    pass

            if img_tk:
                lbl_img = tk.Label(card, image=img_tk, bg="white")
                lbl_img.pack(pady=(10, 2))
            else:
                lbl_img = tk.Label(card, text="🍲", font=("Segoe UI", 20), bg="white")
                lbl_img.pack(pady=(10, 2))

            lbl_name = tk.Label(card, text=item.get("name"), font=("Segoe UI", 9, "bold"), bg="white", fg="#2c3e50", wraplength=130)
            lbl_name.pack()

            for widget in (card, badge, lbl_img, lbl_name):
                widget.bind("<Button-1>", lambda e, it=item: self.add_item_to_order(it))
                widget.config(cursor="hand2")

    def on_order_item_selected(self, event):
        selected = self.tree_order.selection()
        if not selected: return
        
        item_vals = self.tree_order.item(selected[0])['values']
        if not item_vals: return
        
        dish_name = item_vals[0]
        qty = item_vals[1]
        
        target_dish = next((m for m in self.menu_items if m.get("name") == dish_name), None)
        
        self.lbl_preview_text.config(text=f"Đang chọn: {dish_name}\nSố lượng: {qty} phần", fg="#2c3e50")

        if target_dish and target_dish.get("image") and os.path.exists(target_dish.get("image")):
            try:
                from PIL import Image, ImageTk
                pil_img = Image.open(target_dish.get("image")).resize((40, 40))
                img_tk = ImageTk.PhotoImage(pil_img)
                self.lbl_preview_img.config(image=img_tk, text="")
                self.lbl_preview_img.image = img_tk
            except Exception:
                self.lbl_preview_img.config(image="", text="🍲", font=("Segoe UI", 16))
        else:
            self.lbl_preview_img.config(image="", text="🍲", font=("Segoe UI", 16))

    def add_item_to_order(self, item):
        for it in self.current_order:
            if it["name"] == item["name"]:
                it["qty"] += 1
                it["total"] = it["qty"] * it["price"]
                self.update_order_table()
                return

        self.current_order.append({
            "name": item["name"],
            "qty": 1,
            "price": item["price"],
            "total": item["price"]
        })
        self.update_order_table()

    def update_order_table(self):
        for row in self.tree_order.get_children():
            self.tree_order.delete(row)

        total_amount = 0
        for item in self.current_order:
            total_amount += item["total"]
            self.tree_order.insert("", "end", values=(
                item["name"], item["qty"], f"{item['price']:,}", f"{item['total']:,}"
            ))

        self.lbl_total_amount.config(text=f"{total_amount:,} VNĐ")

    def increase_item_qty(self):
        selected = self.tree_order.selection()
        if not selected: return
        idx = self.tree_order.index(selected[0])
        self.current_order[idx]["qty"] += 1
        self.current_order[idx]["total"] = self.current_order[idx]["qty"] * self.current_order[idx]["price"]
        self.update_order_table()

    def decrease_item_qty(self):
        selected = self.tree_order.selection()
        if not selected: return
        idx = self.tree_order.index(selected[0])
        if self.current_order[idx]["qty"] > 1:
            self.current_order[idx]["qty"] -= 1
            self.current_order[idx]["total"] = self.current_order[idx]["qty"] * self.current_order[idx]["price"]
        else:
            self.current_order.pop(idx)
        self.update_order_table()

    def remove_item(self):
        selected = self.tree_order.selection()
        if not selected: return
        idx = self.tree_order.index(selected[0])
        self.current_order.pop(idx)
        self.update_order_table()

    def save_order_and_serve(self):
        if not self.table: return

        self.table.orders = self.current_order
        self.table.status = "Đang phục vụ"
        if not getattr(self.table, 'start_time', None):
            self.table.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.save_tables_to_json()
        messagebox.showinfo("Thành công", f"Đã lưu Oder và chuyển {self.table.name} sang trạng thái 'Đang phục vụ'!")
        if self.on_close:
            self.on_close()

    def checkout(self):
        if not self.current_order:
            messagebox.showwarning("Cảnh báo", "Chưa có món ăn nào trong hóa đơn!")
            return

        total_amount = sum(it["total"] for it in self.current_order)
        
        if messagebox.askyesno("Xác nhận thanh toán", f"Tổng tiền cần thanh toán: {total_amount:,} VNĐ.\nXác nhận thanh toán hóa đơn này?"):
            new_bill = {
                "id": f"BILL-{str(uuid.uuid4().hex)[:6].upper()}",
                "table_name": self.table.name if self.table else "Bàn vãng lai",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "customer_name": "Khách vãng lai",
                "items": self.current_order,
                "total_amount": total_amount,
                "payment_method": "Tiền mặt",
                "status": "Hoàn tất"
            }

            bills = []
            if os.path.exists(self.BILL_FILE):
                try:
                    with open(self.BILL_FILE, "r", encoding="utf-8") as f:
                        bills = json.load(f)
                except: pass
            
            bills.append(new_bill)
            try:
                with open(self.BILL_FILE, "w", encoding="utf-8") as f:
                    json.dump(bills, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Lỗi lưu hóa đơn: {e}")

            if self.table:
                self.table.status = "Trống"
                self.table.orders = []
                self.table.start_time = None
                self.save_tables_to_json()

            messagebox.showinfo("Thành công", f"Thanh toán thành công hóa đơn {new_bill['id']}!")
            if self.on_close:
                self.on_close()

    def save_tables_to_json(self):
        if not os.path.exists(self.TABLE_FILE): return
        try:
            with open(self.TABLE_FILE, "r", encoding="utf-8") as f:
                tables_data = json.load(f)

            for t in tables_data:
                if t.get("id") == self.table.id or t.get("name") == self.table.name:
                    t["status"] = self.table.status
                    t["orders"] = self.table.orders
                    t["start_time"] = getattr(self.table, 'start_time', None)
                    break

            with open(self.TABLE_FILE, "w", encoding="utf-8") as f:
                json.dump(tables_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi cập nhật file tables.json: {e}")

    @staticmethod
    def open_booking_dialog(table, tables_list, refresh_callback, parent_view):
        if hasattr(parent_view, 'open_embedded_order_view'):
            parent_view.open_embedded_order_view(table)