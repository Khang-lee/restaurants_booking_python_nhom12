class TableActionController:
    def __init__(self, table, parent_app):
        self.table = table
        self.parent_app = parent_app

    def get_empty_tables(self):
        return [t for t in self.parent_app.tables if t.status == "Trống" and t.id != self.table.id]

    def get_other_tables(self):
        return [t for t in self.parent_app.tables if t.id != self.table.id]

    def transfer_table(self, target_name):
        empty_tables = self.get_empty_tables()
        target_table = next((t for t in empty_tables if t.name == target_name), None)
        
        if not target_table:
            return False, "Không tìm thấy bàn trống đích!"

        # Bê nguyên dữ liệu sang bàn mới
        target_table.status = self.table.status
        target_table.bookings = self.table.bookings.copy()
        target_table.orders = self.table.orders.copy()
        
        # Xóa dữ liệu bàn cũ
        self.table.status = "Trống"
        self.table.bookings = []
        self.table.orders = []
        
        if hasattr(self.parent_app, "save_data_to_file"):
            self.parent_app.save_data_to_file(show_toast=False)
            
        return True, f"Đã chuyển toàn bộ sang {target_name}!"

    def merge_tables(self, target_name):
        other_tables = self.get_other_tables()
        target_table = next((t for t in other_tables if t.name == target_name), None)
        
        if not target_table:
            return False, "Không tìm thấy bàn đích!"

        # Gộp món ăn (cộng dồn nếu trùng tên món)
        for item in self.table.orders:
            existing = next((i for i in target_table.orders if i["name"] == item["name"]), None)
            if existing:
                existing["qty"] += item["qty"]
                existing["total"] += item["total"]
            else:
                target_table.orders.append(item.copy())
        
        # Gộp thông tin cọc/đặt bàn
        target_table.bookings.extend(self.table.bookings.copy())
        
        # Cập nhật trạng thái bàn đích
        if target_table.orders:
            target_table.status = "Đang phục vụ"
        elif target_table.bookings and target_table.status == "Trống":
            target_table.status = "Đã đặt"
        
        # Dọn dẹp bàn hiện tại
        self.table.status = "Trống"
        self.table.bookings = []
        self.table.orders = []
        
        if hasattr(self.parent_app, "save_data_to_file"):
            self.parent_app.save_data_to_file(show_toast=False)
            
        return True, f"Đã gộp chung vào {target_name}!"

    def cancel_booking(self):
        self.table.status = "Trống"
        self.table.bookings = []
        self.table.orders = []
        
        if self.parent_app and hasattr(self.parent_app, "save_data_to_file"):
            self.parent_app.save_data_to_file(show_toast=False)
            
        return True, "Đã dọn dẹp và hủy đặt bàn thành công!"