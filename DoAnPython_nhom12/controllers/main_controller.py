import os
import json
from datetime import datetime

class MainController:
    def __init__(self, parent_view):
        self.parent_view = parent_view
        # Tập hợp lưu các ID lịch đặt đã thông báo để KHÔNG BAO GIỜ bị lặp lại
        self.notified_booking_ids = set()

    def get_bookings_file_path(self):
        """Lấy đường dẫn tuyệt đối tới file bookings.json"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "..", "data", "bookings.json")
        if not os.path.exists(file_path):
            return "data/bookings.json"
        return file_path

    def get_upcoming_bookings(self):
        """Kiểm tra và chỉ trả về danh sách lịch đặt cần cảnh báo ĐÚNG MỘT LẦN DUY NHẤT"""
        notifications = []
        try:
            file_path = self.get_bookings_file_path()
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                today_str = datetime.now().strftime("%Y-%m-%d")
                now = datetime.now()
                
                for b in bookings:
                    b_date = str(b.get("booking_date", "")).strip()
                    status = str(b.get("status", "")).strip()
                    
                    # Chỉ xét lịch đặt trong ngày hôm nay và đã xác nhận
                    if b_date == today_str and status in ["Đã xác nhận", "Đã đặt"]:
                        dt_str = f"{b_date} {b.get('booking_time')}"
                        try:
                            b_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                            diff_mins = (b_time - now).total_seconds() / 60
                            
                            # Lấy mã định danh độc nhất của lịch đặt
                            b_id = b.get("booking_id") or f"{b.get('table_id')}_{b.get('booking_time')}"
                            
                            # Điều kiện: Còn từ 0 đến 30 phút VÀ chưa từng xuất hiện trong tập đã báo
                            if 0 <= diff_mins <= 30:
                                if b_id not in self.notified_booking_ids:
                                    # Đánh dấu đã đưa vào danh sách thông báo
                                    self.notified_booking_ids.add(b_id)
                                    
                                    notifications.append({
                                        "table_id": b.get("table_id", "N/A"),
                                        "customer_name": b.get("customer_name", "Khách"),
                                        "customer_phone": b.get("customer_phone", "N/A"),
                                        "guest_count": b.get("guest_count") or b.get("guests") or 1,
                                        "booking_time": b.get("booking_time"),
                                        "diff_mins": int(diff_mins)
                                    })
                        except Exception as ex:
                            print("Lỗi parse thời gian booking:", ex)
        except Exception as e:
            print("Lỗi đọc file bookings ở MainController:", e)
            
        return notifications