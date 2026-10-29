from datetime import datetime, timedelta
import io
import json
import os
import uuid
import tkinter as tk
from tkinter import messagebox, ttk
import urllib.request

from PIL import Image, ImageTk

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

# Gọi file TableActions để xử lý Menu 3 gạch
try:
    from ui.views.table_actions import TableActions
except ImportError:
    try:
        from table_actions import TableActions
    except ImportError:
        TableActions = None

# --- HÀM HỖ TRỢ TÌM ĐƯỜNG DẪN CHUẨN XÁC 100% ---
def get_data_path(filename):
    """Luôn trỏ chính xác về thư mục 'data' ở gốc dự án"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(base_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, filename)


class OrderMenuView(tk.Frame):

    def __init__(self, parent, role="Lễ tân"):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.setup_ui()

    def setup_ui(self):
        label = tk.Label(
            self,
            text="🍽️ QUẢN LÝ THỰC ĐƠN & ĐẶT MÓN",
            font=("Segoe UI", 14, "bold"),
            bg="#f5f6fa",
            fg="#2c3e50",
        )
        label.pack(pady=20)

    # --- HỘP THOẠI CHUNG DÙNG CHO CẢ ĐẶT BÀN & GỌI MÓN / THANH TOÁN ---
    @staticmethod
    def open_booking_dialog(
        table, all_tables, refresh_callback=None, parent=None
    ):
        dialog = tk.Toplevel(parent)
        dialog.title(f"QUẢN LÝ BÀN - {getattr(table, 'name', 'Bàn').upper()}")
        dialog.geometry("560x720")
        dialog.resizable(False, False)
        dialog.configure(bg="white")
        dialog.transient(parent)
        dialog.grab_set()

        if not hasattr(table, "bookings"):
            table.bookings = []
        if not hasattr(table, "orders"):
            table.orders = []

        # 1. Tải danh sách món ăn từ file menumonan.json
        menu_data = []
        MENU_FILE = get_data_path("menumonan.json")
        if os.path.exists(MENU_FILE):
            try:
                with open(MENU_FILE, "r", encoding="utf-8") as f:
                    menu_data = json.load(f)
            except Exception as e:
                print(f"Lỗi đọc file JSON thực đơn: {e}")

        if not menu_data:
            menu_data = [
                {"id": "M01", "name": "Cơm chiên hải sản", "price": 65000, "category": "Món chính", "image": ""},
                {"id": "M02", "name": "Lẩu thái hải sản", "price": 250000, "category": "Lẩu", "image": ""},
                {"id": "M08", "name": "Trà đào cam sả", "price": 35000, "category": "Đồ uống", "image": ""},
            ]

        # ==========================================
        # HEADER GIAO DIỆN (CHỨA MENU 3 GẠCH)
        # ==========================================
        COLOR_MAP = {
            "Trống": "#95a5a6",
            "Đã đặt": "#e67e22",
            "Đang phục vụ": "#2ecc71",
        }
        header_color = COLOR_MAP.get(
            getattr(table, "status", "Trống"), "#34495e"
        )

        header = tk.Frame(dialog, bg=header_color, pady=10)
        header.pack(fill="x")
        
        lbl_status = tk.Label(
            header,
            text=f"{getattr(table, 'name', 'Bàn')} ({getattr(table, 'area', 'N/A')}) - Trạng thái: {getattr(table, 'status', 'Trống')}",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg=header_color,
        )
        lbl_status.pack(side="left", padx=15)

        if TableActions:
            TableActions.setup_action_menu(
                header_frame=header, 
                table=table, 
                parent_app=parent, 
                dialog=dialog, 
                refresh_callback=refresh_callback
            )

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # ==========================================
        # TAB 1: ĐẶT BÀN & CỌC
        # ==========================================
        tab_book = tk.Frame(notebook, bg="white", padx=10, pady=10)
        notebook.add(tab_book, text="📌 Đặt bàn / Cọc")

        tk.Label(tab_book, text="Tên khách hàng:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        txt_cust = tk.Entry(tab_book, width=22)
        txt_cust.grid(row=0, column=1, pady=5)

        tk.Label(tab_book, text="Số điện thoại:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        txt_phone = tk.Entry(tab_book, width=22)
        txt_phone.grid(row=1, column=1, pady=5)

        tk.Label(tab_book, text="Số lượng khách:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        spn_guests = tk.Spinbox(tab_book, from_=1, to=50, width=20)
        spn_guests.delete(0, tk.END)
        spn_guests.insert(0, getattr(table, 'capacity', 4))
        spn_guests.grid(row=2, column=1, pady=5)

        tk.Label(tab_book, text="Tiền cọc (VNĐ):", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        txt_deposit = tk.Entry(tab_book, width=22)
        txt_deposit.grid(row=3, column=1, pady=5)

        def auto_calc_deposit(*args):
            try:
                guests = int(spn_guests.get())
                deposit = guests * 120000
                txt_deposit.delete(0, tk.END)
                txt_deposit.insert(0, f"{deposit:,}")
            except ValueError:
                pass

        spn_guests.config(command=auto_calc_deposit)
        spn_guests.bind("<KeyRelease>", auto_calc_deposit)
        auto_calc_deposit()

        tk.Label(tab_book, text="Ngày đặt:", bg="white").grid(row=4, column=0, sticky="w", pady=5)
        if DateEntry:
            dt_entry = DateEntry(tab_book, width=19, background="darkblue", date_pattern="yyyy-mm-dd")
        else:
            dt_entry = tk.Entry(tab_book, width=22)
            dt_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        dt_entry.grid(row=4, column=1, pady=5)

        tk.Label(tab_book, text="Giờ đặt:", bg="white").grid(row=5, column=0, sticky="w", pady=5)
        time_slots = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in (0, 30)]
        cbo_time = ttk.Combobox(tab_book, values=time_slots, state="readonly", width=19)
        cbo_time.set("18:00")
        cbo_time.grid(row=5, column=1, pady=5)

        if table.bookings:
            latest_b = table.bookings[-1]
            txt_cust.insert(0, latest_b.get("customer", ""))
            txt_phone.insert(0, latest_b.get("phone", ""))
            
            saved_guests = latest_b.get("guests", getattr(table, 'capacity', 4))
            spn_guests.delete(0, tk.END)
            spn_guests.insert(0, saved_guests)
            
            saved_deposit = str(latest_b.get("deposit", "0"))
            txt_deposit.delete(0, tk.END)
            try:
                txt_deposit.insert(0, f"{int(saved_deposit):,}")
            except ValueError:
                txt_deposit.insert(0, saved_deposit)

        # --- LOGIC XÁC NHẬN ĐẶT BÀN ---
        def save_booking():
            cust = txt_cust.get().strip()
            phone = txt_phone.get().strip()
            deposit_str = txt_deposit.get().replace(",", "").strip() 
            booking_date = dt_entry.get_date().strftime("%Y-%m-%d") if DateEntry and hasattr(dt_entry, "get_date") else dt_entry.get().strip()
            booking_time = cbo_time.get()
            
            if not cust or not phone.isdigit() or len(phone) < 10 or not deposit_str.isdigit():
                messagebox.showerror("Lỗi", "Vui lòng kiểm tra lại thông tin (Tên, SĐT hợp lệ, Tiền cọc)!")
                return

            BOOKING_FILE = get_data_path("bookings.json")

            # 2. ĐỌC DỮ LIỆU ĐỂ KIỂM TRA TRÙNG LỊCH
            bookings = []
            if os.path.exists(BOOKING_FILE):
                try:
                    with open(BOOKING_FILE, "r", encoding="utf-8") as f:
                        bookings = json.load(f)
                except Exception:
                    pass

            new_dt_str = f"{booking_date} {booking_time}"
            try:
                new_dt = datetime.strptime(new_dt_str, "%Y-%m-%d %H:%M")
                for b in bookings:
                    if b.get("table_id") == getattr(table, 'name', '') and b.get("status") not in ["Đã hủy", "Hoàn thành"]:
                        existing_date = b.get("booking_date")
                        existing_time = b.get("booking_time")
                        if existing_date and existing_time:
                            exist_dt = datetime.strptime(f"{existing_date} {existing_time}", "%Y-%m-%d %H:%M")
                            # Trùng lịch nếu khoảng cách < 2 tiếng (7200 giây)
                            if abs((new_dt - exist_dt).total_seconds()) < 7200:
                                messagebox.showerror(
                                    "Trùng lịch", 
                                    f"Bàn này đã có khách đặt lúc {existing_time} ngày {existing_date}.\n"
                                    "Vui lòng chọn giờ khác (cách khách cũ ít nhất 2 tiếng)!"
                                )
                                return
            except Exception as e:
                print(f"Lỗi kiểm tra ngày giờ: {e}")

            # 3. LƯU VÀO FILE BOOKINGS.JSON
            b_id = "B" + str(uuid.uuid4().hex)[:5].upper()
            new_booking = {
                "booking_id": b_id,
                "table_id": getattr(table, 'name', ''),
                "customer_name": cust,
                "customer_phone": phone,
                "booking_date": booking_date,
                "booking_time": booking_time,
                "guest_count": int(spn_guests.get()),
                "status": "Đã xác nhận",
                "pre_orders": [],
                "deposit_amount": int(deposit_str)
            }
            
            bookings.append(new_booking)
            
            try:
                with open(BOOKING_FILE, "w", encoding="utf-8") as f:
                    json.dump(bookings, f, ensure_ascii=False, indent=2)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu vào bookings.json: {e}")
                return

            # 4. LƯU VÀO BÀN VÀ ĐỔI MÀU SƠ ĐỒ (TABLES.JSON)
            table.bookings.append({
                "customer": cust,
                "phone": phone,
                "guests": int(spn_guests.get()),
                "deposit": int(deposit_str),
                "time": new_dt_str,
            })
            table.status = "Đã đặt"

            if parent and hasattr(parent, "save_data_to_file"):
                parent.save_data_to_file(show_toast=False)

            messagebox.showinfo("Thành công", f"Đã lưu Đơn đặt bàn cho {getattr(table, 'name', 'bàn')}!")
            
            if refresh_callback:
                refresh_callback()
            dialog.destroy()

        tk.Button(
            tab_book,
            text="✅ Xác Nhận Đặt Bàn",
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=save_booking,
        ).grid(row=6, column=0, columnspan=2, pady=15, sticky="we")

        # ==========================================
        # TAB 2: NHẬN MÓN
        # ==========================================
        tab_order = tk.Frame(notebook, bg="white", padx=10, pady=10)
        notebook.add(tab_order, text="📝 Nhận món")

        categories = ["Tất cả"] + sorted(list(set(m.get("category", "Món khác") for m in menu_data)))

        frame_select = tk.Frame(tab_order, bg="white")
        frame_select.pack(fill="x", pady=5)

        frame_inputs = tk.Frame(frame_select, bg="white")
        frame_inputs.pack(side="left", fill="both", expand=True)

        row1 = tk.Frame(frame_inputs, bg="white")
        row1.pack(fill="x", pady=4)
        tk.Label(row1, text="Loại:", bg="white", width=6, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
        cbo_cat = ttk.Combobox(row1, values=categories, state="readonly", width=18)
        cbo_cat.pack(side="left", padx=5)
        cbo_cat.set("Tất cả")

        row2 = tk.Frame(frame_inputs, bg="white")
        row2.pack(fill="x", pady=4)
        tk.Label(row2, text="Món:", bg="white", width=6, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
        cbo_menu = ttk.Combobox(row2, state="readonly", width=18)
        cbo_menu.pack(side="left", padx=5)

        row3 = tk.Frame(frame_inputs, bg="white")
        row3.pack(fill="x", pady=4)
        tk.Label(row3, text="SL:", bg="white", width=6, anchor="w", font=("Segoe UI", 9, "bold")).pack(side="left")
        spn_qty = tk.Spinbox(row3, from_=1, to=20, width=6)
        spn_qty.pack(side="left", padx=5)

        row4 = tk.Frame(frame_inputs, bg="white")
        row4.pack(fill="x", pady=6)

        lbl_img = tk.Label(
            frame_select,
            text="Không có ảnh",
            bg="#f8f9fa",
            width=140,
            height=140,
            relief="groove",
            bd=2,
            font=("Segoe UI", 8, "italic")
        )
        lbl_img.pack_propagate(False)
        lbl_img.pack(side="right", padx=10)

        img_cache = {}

        def load_dish_image(image_url):
            if not image_url:
                lbl_img.config(image="", text="Không có ảnh")
                return
            if image_url in img_cache:
                lbl_img.config(image=img_cache[image_url], text="")
                return
            try:
                req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    img_data = response.read()
                pil_img = Image.open(io.BytesIO(img_data))
                pil_img = pil_img.resize((136, 136), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)
                img_cache[image_url] = tk_img
                lbl_img.config(image=tk_img, text="")
            except Exception:
                lbl_img.config(image="", text="Lỗi tải ảnh")

        def update_menu_options(e=None):
            selected_cat = cbo_cat.get()
            if selected_cat == "Tất cả":
                filtered = menu_data
            else:
                filtered = [m for m in menu_data if m.get("category") == selected_cat]

            menu_names = [m["name"] for m in filtered]
            cbo_menu["values"] = menu_names
            if menu_names:
                cbo_menu.current(0)
                on_dish_changed()
            else:
                cbo_menu.set("")
                lbl_img.config(image="", text="Không có ảnh")

        def on_dish_changed(e=None):
            selected_name = cbo_menu.get()
            dish = next((m for m in menu_data if m["name"] == selected_name), None)
            if dish:
                load_dish_image(dish.get("image", ""))

        cbo_cat.bind("<<ComboboxSelected>>", update_menu_options)
        cbo_menu.bind("<<ComboboxSelected>>", on_dish_changed)

        cols = ("name", "qty", "price", "total")
        tree_orders = ttk.Treeview(
            tab_order, columns=cols, show="headings", height=6
        )
        tree_orders.heading("name", text="Tên món")
        tree_orders.heading("qty", text="SL")
        tree_orders.heading("price", text="Đơn giá")
        tree_orders.heading("total", text="Thành tiền")

        tree_orders.column("name", width=160)
        tree_orders.column("qty", width=40, anchor="center")
        tree_orders.column("price", width=90, anchor="e")
        tree_orders.column("total", width=100, anchor="e")
        tree_orders.pack(fill="both", expand=True, pady=5)

        def update_order_tree():
            for row in tree_orders.get_children():
                tree_orders.delete(row)
            for item in table.orders:
                tree_orders.insert(
                    "",
                    "end",
                    values=(
                        item["name"],
                        item["qty"],
                        f"{item['price']:,}",
                        f"{item['total']:,}",
                    ),
                )

        update_order_tree()

        def add_item():
            item_name = cbo_menu.get()
            if not item_name:
                return

            qty = int(spn_qty.get())
            dish = next((m for m in menu_data if m["name"] == item_name), None)
            price = dish["price"] if dish else 0
            total = price * qty

            for item in table.orders:
                if item["name"] == item_name:
                    item["qty"] += qty
                    item["total"] = item["qty"] * item["price"]
                    break
            else:
                table.orders.append(
                    {
                        "name": item_name,
                        "qty": qty,
                        "price": price,
                        "total": total,
                    }
                )

            table.status = "Đang phục vụ"
            
            if parent and hasattr(parent, "save_data_to_file"):
                parent.save_data_to_file(show_toast=False)

            update_order_tree()
            if refresh_callback:
                refresh_callback()

        btn_add = tk.Button(
            row4,
            text="+ Thêm Món Vào Bàn",
            bg="#2980b9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=add_item,
        )
        btn_add.pack(side="left")

        update_menu_options()

        # ==========================================
        # TAB 3: THANH TOÁN
        # ==========================================
        tab_pay = tk.Frame(notebook, bg="white", padx=10, pady=10)
        notebook.add(tab_pay, text="💳 Thanh toán")

        lbl_total = tk.Label(tab_pay, text="Tổng tiền món: 0 VNĐ", font=("Segoe UI", 10, "bold"), bg="white", anchor="w")
        lbl_total.pack(fill="x", pady=5)

        lbl_deposit_info = tk.Label(tab_pay, text="Đã cọc: 0 VNĐ", font=("Segoe UI", 10), fg="#e67e22", bg="white", anchor="w")
        lbl_deposit_info.pack(fill="x", pady=5)

        lbl_final = tk.Label(tab_pay, text="CẦN THANH TOÁN: 0 VNĐ", font=("Segoe UI", 12, "bold"), fg="#e74c3c", bg="white", anchor="w")
        lbl_final.pack(fill="x", pady=10)

        tk.Label(tab_pay, text="Hình thức thanh toán:", bg="white", anchor="w").pack(fill="x")
        cbo_pay_method = ttk.Combobox(tab_pay, values=["Tiền mặt", "Chuyển khoản (QR)", "Thẻ ATM/Credit"], state="readonly")
        cbo_pay_method.pack(fill="x", pady=5)
        cbo_pay_method.current(0)

        def calculate_payment():
            subtotal = sum(item["total"] for item in table.orders)
            deposit = 0
            if table.bookings:
                deposit = int(table.bookings[-1].get("deposit", 0))

            final_total = max(0, subtotal - deposit)
            lbl_total.config(text=f"Tổng tiền món: {subtotal:,} VNĐ")
            lbl_deposit_info.config(text=f"Đã đặt cọc: {deposit:,} VNĐ")
            lbl_final.config(text=f"CẦN THANH TOÁN: {final_total:,} VNĐ")
            return final_total

        def on_tab_change(event):
            selected_tab = notebook.tab(notebook.select(), "text")
            if "Thanh toán" in selected_tab:
                calculate_payment()

        notebook.bind("<<NotebookTabChanged>>", on_tab_change)

        def process_checkout():
            if not table.orders:
                messagebox.showwarning("Cảnh báo", "Bàn chưa gọi món nào để thanh toán!")
                return

            final_amt = calculate_payment()
            method = cbo_pay_method.get()

            if messagebox.askyesno("Xác nhận", f"Xác nhận thu {final_amt:,} VNĐ bằng hình thức '{method}'?"):
                # 1. TẠO VÀ LƯU BILL
                customer_name = "Khách vãng lai"
                if table.bookings:
                    customer_name = table.bookings[-1].get("customer", "Khách vãng lai")
                
                BILL_FILE = get_data_path("bills.json")
                bills = []
                if os.path.exists(BILL_FILE):
                    try:
                        with open(BILL_FILE, "r", encoding="utf-8") as f:
                            bills = json.load(f)
                    except: pass
                
                new_bill = {
                    "id": "BILL-" + str(uuid.uuid4().hex)[:6].upper(),
                    "table_name": table.name,
                    "customer_name": customer_name,
                    "total_amount": final_amt,
                    "payment_method": method,
                    "items": table.orders.copy(),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Đã thanh toán"
                }
                bills.append(new_bill)
                
                try:
                    with open(BILL_FILE, "w", encoding="utf-8") as f:
                        json.dump(bills, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Lỗi lưu bill: {e}")

                # Cập nhật trạng thái "Hoàn thành" cho Booking của bàn này
                BOOKING_FILE = get_data_path("bookings.json")
                if os.path.exists(BOOKING_FILE):
                    try:
                        with open(BOOKING_FILE, "r", encoding="utf-8") as f:
                            bookings = json.load(f)
                        
                        # Chuyển các booking của bàn này thành "Hoàn thành"
                        for b in bookings:
                            if b.get("table_id") == table.name and b.get("status") == "Đã xác nhận":
                                b["status"] = "Hoàn thành"
                                
                        with open(BOOKING_FILE, "w", encoding="utf-8") as f:
                            json.dump(bookings, f, ensure_ascii=False, indent=2)
                    except: pass

                # 2. LÀM SẠCH BÀN HIỆN TẠI
                table.status = "Trống"
                table.bookings = []
                table.orders = []

                if parent and hasattr(parent, "save_data_to_file"):
                    parent.save_data_to_file(show_toast=False)

                messagebox.showinfo("Thành công", f"Đã thanh toán xong cho {table.name}!")
                if refresh_callback:
                    refresh_callback()
                dialog.destroy()

        tk.Button(
            tab_pay, text="💰 HOÀN TẤT THANH TOÁN", bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"), pady=8, command=process_checkout,
        ).pack(fill="x", side="bottom", pady=10)