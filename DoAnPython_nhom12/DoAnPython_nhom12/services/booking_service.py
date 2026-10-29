class BookingService:

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def get_all_bookings(self):
        """Lấy danh sách tất cả các đơn đặt bàn từ DataManager"""
        if hasattr(self.data_manager, "load_bookings"):
            return self.data_manager.load_bookings()
        elif hasattr(self.data_manager, "get_bookings"):
            return self.data_manager.get_bookings()
        return []

    def save_all_bookings(self, bookings):
        """Lưu lại danh sách xuống File / DB"""
        if hasattr(self.data_manager, "save_bookings"):
            return self.data_manager.save_bookings(bookings)
        return False

    def cancel_booking(self, booking_id):
        """Quản lý thực hiện hủy trực tiếp đơn đặt bàn"""
        bookings = self.get_all_bookings()
        found = False

        for b in bookings:
            b_id = str(b.get("id", b.get("booking_id", "")))
            if b_id == str(booking_id):
                b["status"] = "Đã hủy"
                found = True
                break

        if found:
            self.save_all_bookings(bookings)
            return True, "Hủy đơn đặt bàn thành công."
        return False, f"Không tìm thấy đơn đặt bàn có mã {booking_id}."

    def request_cancel(self, booking_id, reason=""):
        """Lễ tân gửi Yêu cầu Hủy bàn tới Quản lý"""
        bookings = self.get_all_bookings()
        found = False

        for b in bookings:
            b_id = str(b.get("id", b.get("booking_id", "")))
            if b_id == str(booking_id):
                b["status"] = "Chờ duyệt hủy"
                b["cancel_reason"] = reason if reason else "Lễ tân yêu cầu hủy"
                found = True
                break

        if found:
            self.save_all_bookings(bookings)
            return True, "Đã cập nhật trạng thái Chờ duyệt hủy."
        return False, f"Không tìm thấy đơn đặt bàn có mã {booking_id}."