import tkinter as tk
from tkinter import messagebox, ttk

class TableActions:
    
    @staticmethod
    def setup_action_menu(header_frame, table, parent_app, dialog, refresh_callback):
        bg_color = header_frame.cget("bg")
        
        btn_actions = tk.Menubutton(
            header_frame,
            text="☰", 
            font=("Segoe UI", 13, "bold"),
            bg=bg_color,
            fg="white",
            activebackground="#2c3e50",
            activeforeground="white",
            cursor="hand2",
            relief="flat",
        )
        btn_actions.pack(side="right", padx=15)

        action_menu = tk.Menu(btn_actions, tearoff=0, font=("Segoe UI", 10))
        
        # --- 1. LOGIC CHUYỂN BÀN ---
        def handle_transfer_table():
            if table.status == "Trống":
                messagebox.showwarning("Cảnh báo", "Bàn đang trống, không có gì để chuyển!")
                return

            # Lấy danh sách các bàn trống
            empty_tables = [t for t in parent_app.tables if t.status == "Trống" and t.id != table.id]
            if not empty_tables:
                messagebox.showerror("Lỗi", "Không có bàn trống nào để chuyển đến!")
                return

            # Tạo hộp thoại chọn bàn
            trans_dlg = tk.Toplevel(dialog)
            trans_dlg.title("Chuyển bàn")
            trans_dlg.geometry("320x180")
            trans_dlg.transient(dialog)
            trans_dlg.grab_set()
            trans_dlg.configure(bg="white")

            tk.Label(trans_dlg, text=f"Chuyển từ: {table.name}", font=("Segoe UI", 10, "bold"), bg="white").pack(pady=(15, 5))
            tk.Label(trans_dlg, text="Chọn bàn muốn chuyển đến:", bg="white").pack()

            cbo_target = ttk.Combobox(trans_dlg, values=[t.name for t in empty_tables], state="readonly", width=25)
            cbo_target.pack(pady=10)
            cbo_target.current(0)

            def do_transfer():
                target_name = cbo_target.get()
                target_table = next((t for t in empty_tables if t.name == target_name), None)
                
                if target_table:
                    # Bê nguyên dữ liệu sang bàn mới
                    target_table.status = table.status
                    target_table.bookings = table.bookings.copy()
                    target_table.orders = table.orders.copy()
                    
                    # Xóa dữ liệu bàn cũ
                    table.status = "Trống"
                    table.bookings = []
                    table.orders = []
                    
                    if hasattr(parent_app, "save_data_to_file"):
                        parent_app.save_data_to_file(show_toast=False)
                        
                    messagebox.showinfo("Thành công", f"Đã chuyển toàn bộ sang {target_name}!")
                    if refresh_callback:
                        refresh_callback()
                    trans_dlg.destroy()
                    dialog.destroy() # Đóng luôn hộp thoại bàn cũ

            tk.Button(trans_dlg, text="🔄 Xác nhận Chuyển", bg="#2980b9", fg="white", font=("Segoe UI", 9, "bold"), command=do_transfer).pack(pady=5)


        # --- 2. LOGIC GỘP BÀN ---
        def handle_merge_tables():
            if table.status == "Trống":
                messagebox.showwarning("Cảnh báo", "Bàn đang trống, không có gì để gộp!")
                return

            # Lấy danh sách các bàn khác (bàn đích có thể đang có khách hoặc trống)
            other_tables = [t for t in parent_app.tables if t.id != table.id]
            if not other_tables:
                messagebox.showerror("Lỗi", "Không có bàn nào khác để gộp!")
                return

            merge_dlg = tk.Toplevel(dialog)
            merge_dlg.title("Gộp bàn")
            merge_dlg.geometry("320x180")
            merge_dlg.transient(dialog)
            merge_dlg.grab_set()
            merge_dlg.configure(bg="white")

            tk.Label(merge_dlg, text=f"Bàn hiện tại: {table.name}", font=("Segoe UI", 10, "bold"), bg="white").pack(pady=(15, 5))
            tk.Label(merge_dlg, text="Chọn bàn đích muốn gộp vào:", bg="white").pack()

            cbo_target = ttk.Combobox(merge_dlg, values=[t.name for t in other_tables], state="readonly", width=25)
            cbo_target.pack(pady=10)
            cbo_target.current(0)

            def do_merge():
                target_name = cbo_target.get()
                target_table = next((t for t in other_tables if t.name == target_name), None)
                
                if target_table:
                    # Gộp món ăn (cộng dồn nếu trùng)
                    for item in table.orders:
                        existing = next((i for i in target_table.orders if i["name"] == item["name"]), None)
                        if existing:
                            existing["qty"] += item["qty"]
                            existing["total"] += item["total"]
                        else:
                            target_table.orders.append(item.copy())
                    
                    # Gộp thông tin cọc/đặt bàn
                    target_table.bookings.extend(table.bookings.copy())
                    
                    # Cập nhật trạng thái bàn đích
                    if target_table.orders:
                        target_table.status = "Đang phục vụ"
                    elif target_table.bookings and target_table.status == "Trống":
                        target_table.status = "Đã đặt"
                    
                    # Dọn dẹp bàn hiện tại
                    table.status = "Trống"
                    table.bookings = []
                    table.orders = []
                    
                    if hasattr(parent_app, "save_data_to_file"):
                        parent_app.save_data_to_file(show_toast=False)
                        
                    messagebox.showinfo("Thành công", f"Đã gộp chung vào {target_name}!")
                    if refresh_callback:
                        refresh_callback()
                    merge_dlg.destroy()
                    dialog.destroy()

            tk.Button(merge_dlg, text="🔗 Xác nhận Gộp", bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"), command=do_merge).pack(pady=5)


        # --- 3. LOGIC HỦY ĐẶT BÀN ---
        def handle_cancel_booking():
            if table.status == "Trống":
                messagebox.showinfo("Thông báo", "Bàn này đang trống.")
                return
                
            if messagebox.askyesno("Xác nhận Hủy", f"Hủy đặt bàn/Trả bàn trống cho {getattr(table, 'name', 'bàn')}?\nToàn bộ thông tin món ăn và cọc sẽ bị xóa."):
                table.status = "Trống"
                table.bookings = []
                table.orders = []
                
                if parent_app and hasattr(parent_app, "save_data_to_file"):
                    parent_app.save_data_to_file(show_toast=False)
                
                messagebox.showinfo("Thành công", "Đã dọn dẹp và hủy đặt bàn thành công!")
                
                if refresh_callback:
                    refresh_callback()
                dialog.destroy()

        # --- GẮN CHỨC NĂNG VÀO MENU ---
        action_menu.add_command(label="🔄 Chuyển bàn", command=handle_transfer_table)
        action_menu.add_command(label="🔗 Gộp bàn", command=handle_merge_tables)
        action_menu.add_separator()
        action_menu.add_command(label="❌ Hủy / Trả bàn", command=handle_cancel_booking)

        btn_actions.config(menu=action_menu)