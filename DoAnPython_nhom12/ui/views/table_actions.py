import tkinter as tk
from tkinter import ttk, messagebox
from controllers.table_action_controller import TableActionController

class TableActions:
    
    @staticmethod
    def setup_action_menu(header_frame, table, parent_app, dialog, refresh_callback):
        controller = TableActionController(table, parent_app)
        bg_color = header_frame.cget("bg")
        
        # Nút menu hành động (☰)
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

            empty_tables = controller.get_empty_tables()
            if not empty_tables:
                messagebox.showerror("Lỗi", "Không có bàn trống nào để chuyển đến!")
                return

            # Hộp thoại chọn bàn chuyển
            trans_dlg = tk.Toplevel(dialog)
            trans_dlg.title("Chuyển bàn")
            trans_dlg.geometry("340x200")
            trans_dlg.transient(dialog)
            trans_dlg.grab_set()
            trans_dlg.configure(bg="white")

            tk.Label(
                trans_dlg, text=f"Chuyển từ: {table.name}", 
                font=("Segoe UI", 11, "bold"), bg="white", fg="#2c3e50"
            ).pack(pady=(20, 5))
            
            tk.Label(trans_dlg, text="Chọn bàn muốn chuyển đến:", font=("Segoe UI", 9), bg="white", fg="#7f8c8d").pack()

            cbo_target = ttk.Combobox(trans_dlg, values=[t.name for t in empty_tables], state="readonly", width=26, font=("Segoe UI", 10))
            cbo_target.pack(pady=12)
            cbo_target.current(0)

            def do_transfer():
                target_name = cbo_target.get()
                success, msg = controller.transfer_table(target_name)
                if success:
                    messagebox.showinfo("Thành công", msg, parent=trans_dlg)
                    if refresh_callback:
                        refresh_callback()
                    trans_dlg.destroy()
                    dialog.destroy()
                else:
                    messagebox.showerror("Lỗi", msg, parent=trans_dlg)

            tk.Button(
                trans_dlg, text="🔄 Xác nhận Chuyển", bg="#2980b9", fg="white", 
                font=("Segoe UI", 9, "bold"), command=do_transfer, relief="flat", cursor="hand2", padx=15, pady=6
            ).pack(pady=5)

        # --- 2. LOGIC GỘP BÀN ---
        def handle_merge_tables():
            if table.status == "Trống":
                messagebox.showwarning("Cảnh báo", "Bàn đang trống, không có gì để gộp!")
                return

            other_tables = controller.get_other_tables()
            if not other_tables:
                messagebox.showerror("Lỗi", "Không có bàn nào khác để gộp!")
                return

            # Hộp thoại chọn bàn gộp
            merge_dlg = tk.Toplevel(dialog)
            merge_dlg.title("Gộp bàn")
            merge_dlg.geometry("340x200")
            merge_dlg.transient(dialog)
            merge_dlg.grab_set()
            merge_dlg.configure(bg="white")

            tk.Label(
                merge_dlg, text=f"Bàn hiện tại: {table.name}", 
                font=("Segoe UI", 11, "bold"), bg="white", fg="#2c3e50"
            ).pack(pady=(20, 5))
            
            tk.Label(merge_dlg, text="Chọn bàn đích muốn gộp vào:", font=("Segoe UI", 9), bg="white", fg="#7f8c8d").pack()

            cbo_target = ttk.Combobox(merge_dlg, values=[t.name for t in other_tables], state="readonly", width=26, font=("Segoe UI", 10))
            cbo_target.pack(pady=12)
            cbo_target.current(0)

            def do_merge():
                target_name = cbo_target.get()
                success, msg = controller.merge_tables(target_name)
                if success:
                    messagebox.showinfo("Thành công", msg, parent=merge_dlg)
                    if refresh_callback:
                        refresh_callback()
                    merge_dlg.destroy()
                    dialog.destroy()
                else:
                    messagebox.showerror("Lỗi", msg, parent=merge_dlg)

            tk.Button(
                merge_dlg, text="🔗 Xác nhận Gộp", bg="#27ae60", fg="white", 
                font=("Segoe UI", 9, "bold"), command=do_merge, relief="flat", cursor="hand2", padx=15, pady=6
            ).pack(pady=5)

        # --- 3. LOGIC HỦY ĐẶT BÀN ---
        def handle_cancel_booking():
            if table.status == "Trống":
                messagebox.showinfo("Thông báo", "Bàn này đang trống.")
                return
                
            if messagebox.askyesno("Xác nhận Hủy", f"Hủy đặt bàn/Trả bàn trống cho {getattr(table, 'name', 'bàn')}?\nToàn bộ thông tin món ăn và cọc sẽ bị xóa."):
                success, msg = controller.cancel_booking()
                if success:
                    messagebox.showinfo("Thành công", msg)
                    if refresh_callback:
                        refresh_callback()
                    dialog.destroy()

        # --- GẮN CHỨC NĂNG VÀO MENU ---
        action_menu.add_command(label="🔄 Chuyển bàn", command=handle_transfer_table)
        action_menu.add_command(label="🔗 Gộp bàn", command=handle_merge_tables)
        action_menu.add_separator()
        action_menu.add_command(label="❌ Hủy / Trả bàn", command=handle_cancel_booking)

        btn_actions.config(menu=action_menu)