import tkinter as tk
from tkinter import ttk, messagebox
from controllers.bill_controller import BillController

class BillListView(tk.Frame):
    def __init__(self, parent=None, role="Lễ tân"):
        super().__init__(parent, bg="#f5f6fa")
        self.role = role
        self.controller = BillController(role=role)
        self.bills_data = [] 
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- HEADER ---
        header_frame = tk.Frame(self, bg="white", padx=20, pady=15)
        header_frame.pack(fill="x", padx=20, pady=(15, 0))
        
        tk.Label(
            header_frame, 
            text="🧾 QUẢN LÝ LỊCH SỬ HÓA ĐƠN", 
            font=("Segoe UI", 15, "bold"), 
            bg="white", 
            fg="#2c3e50"
        ).pack(side="left")

        # NÚT XEM BÁO CÁO & LÀM MỚI
        tk.Button(
            header_frame, 
            text="🔄 Làm mới", 
            bg="#3498db", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            command=self.load_data,
            relief="flat", cursor="hand2", padx=12, pady=6
        ).pack(side="right", padx=4)

        tk.Button(
            header_frame, 
            text="📊 Báo Cáo Tổng Hợp", 
            bg="#27ae60", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            command=self.show_summary_report,
            relief="flat", cursor="hand2", padx=12, pady=6
        ).pack(side="right", padx=4)

        # --- BẢNG DỮ LIỆU (TREEVIEW) ---
        table_container = tk.Frame(self, bg="white", padx=15, pady=15)
        table_container.pack(fill="both", expand=True, padx=20, pady=15)

        cols = ("id", "date", "table", "customer", "total", "method", "status")
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", height=14)
        
        headers = [
            ("id", "Mã Bill", 110, "center"),
            ("date", "Ngày giờ xuất", 150, "center"),
            ("table", "Bàn", 100, "center"),
            ("customer", "Khách hàng", 180, "w"),
            ("total", "Tổng thu (VNĐ)", 120, "e"),
            ("method", "Hình thức", 140, "center"),
            ("status", "Trạng thái", 120, "center")
        ]
        
        for col, text, width, anchor in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)
        
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
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
            relief="flat", cursor="hand2", padx=12, pady=6
        ).pack(side="left")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        self.bills_data = self.controller.get_bills()
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

    def show_summary_report(self):
        if not self.bills_data:
            return messagebox.showinfo("Thông báo", "Chưa có dữ liệu hóa đơn nào để thống kê!")

        report = self.controller.calculate_summary_report(self.bills_data)

        report_dlg = tk.Toplevel(self)
        report_dlg.title("📊 BÁO CÁO & THỐNG KÊ CHI TIẾT")
        report_dlg.geometry("520x680")
        report_dlg.configure(bg="white")
        report_dlg.transient(self)
        report_dlg.grab_set()

        tk.Label(
            report_dlg, 
            text="📈 TỔNG HỢP KẾT QUẢ KINH DOANH", 
            font=("Segoe UI", 13, "bold"), 
            bg="white", 
            fg="#2c3e50"
        ).pack(pady=(15, 10))

        # Khung chỉ số chính
        frame_box = tk.Frame(report_dlg, bg="#f8f9fa", bd=1, relief="solid", padx=15, pady=10)
        frame_box.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_box, text=f"💰 TỔNG DOANH THU: {report['total_revenue']:,} VNĐ", font=("Segoe UI", 11, "bold"), fg="#27ae60", bg="#f8f9fa", anchor="w").pack(fill="x", pady=3)
        tk.Label(frame_box, text=f"🧾 Tổng số hóa đơn: {report['total_bills']} bill", font=("Segoe UI", 10), bg="#f8f9fa", anchor="w").pack(fill="x", pady=2)
        tk.Label(frame_box, text=f"🍲 Tổng số món đã phục vụ: {report['total_items_count']} đĩa/phần", font=("Segoe UI", 10), bg="#f8f9fa", anchor="w").pack(fill="x", pady=2)

        # Thống kê theo phương thức thanh toán
        tk.Label(report_dlg, text="💳 Phương thức thanh toán:", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w", padx=20, pady=(12, 4))

        frame_methods = tk.Frame(report_dlg, bg="white", padx=20)
        frame_methods.pack(fill="x")

        for method_name, amount in report['pay_methods_revenue'].items():
            count = report['pay_methods_count'][method_name]
            row = tk.Frame(frame_methods, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"• {method_name} ({count} lần):", font=("Segoe UI", 9), bg="white", width=25, anchor="w").pack(side="left")
            tk.Label(row, text=f"{amount:,} VNĐ", font=("Segoe UI", 9, "bold"), fg="#e67e22", bg="white").pack(side="right")

        # Bảng món ăn đã bán
        tk.Label(report_dlg, text="🍲 Danh sách các món ăn đã bán:", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w", padx=20, pady=(12, 4))
        
        frame_dishes = tk.Frame(report_dlg, bg="white", padx=20)
        frame_dishes.pack(fill="both", expand=True, pady=5)
        
        cols = ("dish", "qty")
        tree_dishes = ttk.Treeview(frame_dishes, columns=cols, show="headings", height=8)
        tree_dishes.heading("dish", text="Tên món ăn")
        tree_dishes.heading("qty", text="Số lượng bán ra")
        tree_dishes.column("dish", width=260)
        tree_dishes.column("qty", width=120, anchor="center")
        
        scroll_dishes = ttk.Scrollbar(frame_dishes, orient="vertical", command=tree_dishes.yview)
        tree_dishes.configure(yscroll=scroll_dishes.set)
        tree_dishes.pack(side="left", fill="both", expand=True)
        scroll_dishes.pack(side="right", fill="y")
        
        for d_name, d_qty in report['sorted_dishes']:
            tree_dishes.insert("", "end", values=(d_name, f"{d_qty} phần"))

        tk.Button(
            report_dlg, 
            text="Đóng Báo Cáo", 
            bg="#95a5a6", 
            fg="white", 
            font=("Segoe UI", 9, "bold"), 
            command=report_dlg.destroy,
            relief="flat", cursor="hand2", padx=15, pady=6
        ).pack(pady=15)

    def show_bill_detail(self):
        selected = self.tree.selection()
        if not selected:
            return messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hóa đơn để xem!")

        item_vals = self.tree.item(selected[0])['values']
        bill_id = item_vals[0]

        bill = self.controller.get_bill_detail(self.bills_data, bill_id)
        if not bill:
            return

        detail_dlg = tk.Toplevel(self)
        detail_dlg.title(f"CHI TIẾT HÓA ĐƠN - {bill_id}")
        detail_dlg.geometry("420x520")
        detail_dlg.configure(bg="white")
        detail_dlg.transient(self)
        detail_dlg.grab_set()

        tk.Label(detail_dlg, text="HÓA ĐƠN THANH TOÁN", font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 5))
        tk.Label(detail_dlg, text=f"Mã: {bill.get('id')} | Bàn: {bill.get('table_name')}", font=("Segoe UI", 9, "bold"), bg="white", fg="#7f8c8d").pack()
        tk.Label(detail_dlg, text=f"Thời gian: {bill.get('created_at')}", font=("Segoe UI", 8), bg="white", fg="#95a5a6").pack(pady=(0, 10))

        # Bảng món ăn trong Bill
        cols = ("name", "qty", "price", "total")
        tree_items = ttk.Treeview(detail_dlg, columns=cols, show="headings", height=9)
        tree_items.heading("name", text="Tên món")
        tree_items.heading("qty", text="SL")
        tree_items.heading("price", text="Đơn giá")
        tree_items.heading("total", text="Thành tiền")

        tree_items.column("name", width=160)
        tree_items.column("qty", width=40, anchor="center")
        tree_items.column("price", width=85, anchor="e")
        tree_items.column("total", width=95, anchor="e")
        tree_items.pack(fill="both", expand=True, padx=20, pady=5)

        for it in bill.get("items", []):
            tree_items.insert("", "end", values=(
                it.get("name"),
                it.get("qty"),
                f"{it.get('price', 0):,}",
                f"{it.get('total', 0):,}"
            ))

        tk.Label(detail_dlg, text=f"Tổng thanh toán: {bill.get('total_amount', 0):,} VNĐ", font=("Segoe UI", 11, "bold"), fg="#e74c3c", bg="white").pack(pady=10)
        tk.Label(detail_dlg, text=f"Hình thức: {bill.get('payment_method')}", font=("Segoe UI", 9, "italic"), bg="white").pack(pady=(0, 15))