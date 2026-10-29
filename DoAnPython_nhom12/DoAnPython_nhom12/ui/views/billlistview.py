import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

class BillListView(tk.Frame):
    def __init__(self, parent=None, role="Lễ tân"):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        
        # Tự động dò tìm file bills.json
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(CURRENT_DIR, "..", "..", "data", "bills.json"),
            os.path.join(CURRENT_DIR, "..", "data", "bills.json"),
            os.path.join("data", "bills.json")
        ]
        
        self.DATA_FILE = possible_paths[0]
        for path in possible_paths:
            if os.path.exists(path):
                self.DATA_FILE = path
                break

        self.bills_data = [] # Lưu dữ liệu thô để dùng cho thống kê
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- HEADER ---
        header_frame = tk.Frame(self, bg="white", padx=20, pady=15)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame, 
            text="🧾 QUẢN LÝ LỊCH SỬ HÓA ĐƠN", 
            font=("Segoe UI", 14, "bold"), 
            bg="white", 
            fg="#2c3e50"
        ).pack(side="left")

        # NÚT XEM BÁO CÁO TỔNG HỢP (XEM THÊM)
        tk.Button(
            header_frame, 
            text="📊 Báo Cáo Tổng Hợp", 
            bg="#27ae60", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            command=self.show_summary_report,
            relief="flat",
            cursor="hand2",
            padx=10
        ).pack(side="right", padx=5)

        tk.Button(
            header_frame, 
            text="🔄 Làm mới", 
            bg="#3498db", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            command=self.load_data,
            relief="flat",
            cursor="hand2",
            padx=10
        ).pack(side="right", padx=5)

        # --- BẢNG DỮ LIỆU (TREEVIEW) ---
        table_frame = tk.Frame(self, bg="white", padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        cols = ("id", "date", "table", "customer", "total", "method", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=13)
        
        self.tree.heading("id", text="Mã Bill")
        self.tree.heading("date", text="Ngày giờ xuất")
        self.tree.heading("table", text="Bàn")
        self.tree.heading("customer", text="Khách hàng")
        self.tree.heading("total", text="Tổng thu (VNĐ)")
        self.tree.heading("method", text="Hình thức")
        self.tree.heading("status", text="Trạng thái")
        
        self.tree.column("id", width=110, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("table", width=100, anchor="center")
        self.tree.column("customer", width=180)
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("method", width=140, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- BOTTOM ACTION BAR ---
        bottom_frame = tk.Frame(self, bg="#f5f6fa", padx=20, pady=5)
        bottom_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Button(
            bottom_frame,
            text="👁️ Xem Chi Tiết Bill Chọn",
            bg="#2980b9",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self.show_bill_detail,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=5
        ).pack(side="left")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        self.bills_data = []
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    self.bills_data = json.load(f)
                    
                    for b in reversed(self.bills_data):
                        self.tree.insert("", "end", values=(
                            b.get("id", "N/A"),
                            b.get("created_at", ""),
                            b.get("table_name", ""),
                            b.get("customer_name", "Khách vãng lai"),
                            f"{b.get('total_amount', 0):,}",
                            b.get("payment_method", ""),
                            b.get("status", "Hoàn tất")
                        ))
            except Exception as e:
                print(f"Lỗi đọc file bills.json: {e}")

    # ==========================================
    # HỘP THOẠI BÁO CÁO TỔNG HỢP (NÂNG CẤP)
    # ==========================================
    def show_summary_report(self):
        if not self.bills_data:
            messagebox.showinfo("Thông báo", "Chưa có dữ liệu hóa đơn nào để thống kê!")
            return

        total_revenue = 0
        total_bills = len(self.bills_data)
        total_items_count = 0
        
        # Các biến lưu thống kê chi tiết
        pay_methods_revenue = {} # Lưu tổng tiền theo từng phương thức
        pay_methods_count = {}   # Lưu số lần thanh toán theo từng phương thức
        dish_stats = {}          # Lưu số lượng từng món ăn

        for b in self.bills_data:
            # 1. Tổng doanh thu
            total_revenue += b.get("total_amount", 0)
            
            # 2. Thống kê phương thức thanh toán (Tiền mặt, QR, Thẻ...)
            method = b.get("payment_method", "Chưa rõ")
            pay_methods_revenue[method] = pay_methods_revenue.get(method, 0) + b.get("total_amount", 0)
            pay_methods_count[method] = pay_methods_count.get(method, 0) + 1
            
            # 3. Thống kê món ăn
            items = b.get("items", [])
            for item in items:
                qty = item.get("qty", 1)
                name = item.get("name", "Món khác")
                total_items_count += qty
                dish_stats[name] = dish_stats.get(name, 0) + qty

        # Tạo cửa sổ Báo cáo
        report_dlg = tk.Toplevel(self)
        report_dlg.title("📊 BÁO CÁO & THỐNG KÊ CHI TIẾT")
        report_dlg.geometry("500x650") # Tăng chiều cao để chứa bảng món ăn
        report_dlg.configure(bg="white")
        report_dlg.transient(self)
        report_dlg.grab_set()

        tk.Label(
            report_dlg, 
            text="📈 TỔNG HỢP KẾT QUẢ KINH DOANH", 
            font=("Segoe UI", 12, "bold"), 
            bg="white", 
            fg="#2c3e50"
        ).pack(pady=(15, 10))

        # Khung hiển thị chỉ số chính
        frame_box = tk.Frame(report_dlg, bg="#f8f9fa", bd=1, relief="solid", padx=15, pady=10)
        frame_box.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_box, text=f"💰 TỔNG DOANH THU: {total_revenue:,} VNĐ", font=("Segoe UI", 11, "bold"), fg="#27ae60", bg="#f8f9fa", anchor="w").pack(fill="x", pady=3)
        tk.Label(frame_box, text=f"🧾 Tổng số hóa đơn: {total_bills} bill", font=("Segoe UI", 10), bg="#f8f9fa", anchor="w").pack(fill="x", pady=2)
        tk.Label(frame_box, text=f"🍲 Tổng số món đã phục vụ: {total_items_count} đĩa/phần", font=("Segoe UI", 10), bg="#f8f9fa", anchor="w").pack(fill="x", pady=2)

        # Thống kê theo phương thức thanh toán
        tk.Label(report_dlg, text="💳 Phương thức thanh toán (Số lần - Doanh thu):", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w", padx=20, pady=(15, 5))

        frame_methods = tk.Frame(report_dlg, bg="white", padx=20)
        frame_methods.pack(fill="x")

        for method_name in pay_methods_revenue:
            count = pay_methods_count[method_name]
            amount = pay_methods_revenue[method_name]
            
            row = tk.Frame(frame_methods, bg="white")
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"• {method_name} ({count} lần):", font=("Segoe UI", 9), bg="white", width=25, anchor="w").pack(side="left")
            tk.Label(row, text=f"{amount:,} VNĐ", font=("Segoe UI", 9, "bold"), fg="#e67e22", bg="white").pack(side="right")

        # Bảng danh sách chi tiết món ăn đã bán
        tk.Label(report_dlg, text="🍲 Danh sách các món ăn đã bán:", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w", padx=20, pady=(15, 5))
        
        frame_dishes = tk.Frame(report_dlg, bg="white", padx=20)
        frame_dishes.pack(fill="both", expand=True, pady=5)
        
        cols = ("dish", "qty")
        tree_dishes = ttk.Treeview(frame_dishes, columns=cols, show="headings", height=8)
        tree_dishes.heading("dish", text="Tên món ăn")
        tree_dishes.heading("qty", text="Số lượng bán ra")
        tree_dishes.column("dish", width=250)
        tree_dishes.column("qty", width=120, anchor="center")
        
        scroll_dishes = ttk.Scrollbar(frame_dishes, orient="vertical", command=tree_dishes.yview)
        tree_dishes.configure(yscroll=scroll_dishes.set)
        tree_dishes.pack(side="left", fill="both", expand=True)
        scroll_dishes.pack(side="right", fill="y")
        
        # Sắp xếp món ăn theo số lượng bán (Từ cao xuống thấp)
        sorted_dishes = sorted(dish_stats.items(), key=lambda x: x[1], reverse=True)
        for d_name, d_qty in sorted_dishes:
            tree_dishes.insert("", "end", values=(d_name, f"{d_qty} phần"))

        tk.Button(
            report_dlg, 
            text="Đóng Báo Cáo", 
            bg="#95a5a6", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            command=report_dlg.destroy,
            width=15
        ).pack(pady=15)

    # ==========================================
    # HỘP THOẠI XEM CHI TIẾT 1 BILL
    # ==========================================
    def show_bill_detail(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hóa đơn để xem!")
            return

        item_vals = self.tree.item(selected[0])['values']
        bill_id = item_vals[0]

        # Tìm dữ liệu hóa đơn tương ứng
        bill = next((b for b in self.bills_data if b.get("id") == bill_id), None)
        if not bill:
            return

        detail_dlg = tk.Toplevel(self)
        detail_dlg.title(f"CHI TIẾT HÓA ĐƠN - {bill_id}")
        detail_dlg.geometry("400x500")
        detail_dlg.configure(bg="white")
        detail_dlg.transient(self)
        detail_dlg.grab_set()

        tk.Label(detail_dlg, text=f"HÓA ĐƠN THANH TOÁN", font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 5))
        tk.Label(detail_dlg, text=f"Mã: {bill.get('id')} - Bàn: {bill.get('table_name')}", font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack()
        tk.Label(detail_dlg, text=f"Thời gian: {bill.get('created_at')}", font=("Segoe UI", 8), bg="white", fg="#95a5a6").pack(pady=(0, 10))

        # Bảng danh sách món ăn trong Bill
        cols = ("name", "qty", "price", "total")
        tree_items = ttk.Treeview(detail_dlg, columns=cols, show="headings", height=8)
        tree_items.heading("name", text="Tên món")
        tree_items.heading("qty", text="SL")
        tree_items.heading("price", text="Đơn giá")
        tree_items.heading("total", text="Thành tiền")

        tree_items.column("name", width=150)
        tree_items.column("qty", width=40, anchor="center")
        tree_items.column("price", width=80, anchor="e")
        tree_items.column("total", width=90, anchor="e")
        tree_items.pack(fill="both", expand=True, padx=15, pady=5)

        for it in bill.get("items", []):
            tree_items.insert("", "end", values=(
                it.get("name"),
                it.get("qty"),
                f"{it.get('price', 0):,}",
                f"{it.get('total', 0):,}"
            ))

        tk.Label(detail_dlg, text=f"Tổng thanh toán: {bill.get('total_amount', 0):,} VNĐ", font=("Segoe UI", 11, "bold"), fg="#e74c3c", bg="white").pack(pady=10)
        tk.Label(detail_dlg, text=f"Hình thức: {bill.get('payment_method')}", font=("Segoe UI", 9, "italic"), bg="white").pack(pady=(0, 10))