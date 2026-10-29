import json
import os

class Booking:
    def __init__(self, booking_id, table_id, customer_phone, booking_date, booking_time, guest_count, status="Đã xác nhận", pre_orders=None, deposit_amount=0, customer_name="Khách vãng lai"):
        self.booking_id = booking_id
        self.table_id = table_id
        self.customer_name = customer_name  # Thêm Tên khách để khớp UI
        self.customer_phone = customer_phone
        self.booking_date = booking_date
        self.booking_time = booking_time
        self.guest_count = guest_count
        self.status = status  # Đã xác nhận, Đã hủy, Hoàn thành
        self.pre_orders = pre_orders if pre_orders is not None else []
        self.deposit_amount = deposit_amount

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "table_id": self.table_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "booking_date": self.booking_date,
            "booking_time": self.booking_time,
            "guest_count": self.guest_count,
            "status": self.status,
            "pre_orders": self.pre_orders,
            "deposit_amount": self.deposit_amount
        }

def save_booking_to_json(booking_dict):
    """Hàm lưu Đơn đặt bàn vào thẳng file data/bookings.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "data", "bookings.json")
    
    bookings = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bookings = json.load(f)
        except Exception:
            bookings = []
            
    bookings.append(booking_dict)
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(bookings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi khi lưu Booking: {e}")