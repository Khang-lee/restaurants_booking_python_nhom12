import uuid
from datetime import datetime, timedelta
from services.booking_service import BookingService

class BookingController:
    def __init__(self, view=None):
        self.view = view
        self.service = BookingService()

    def get_bookings(self):
        """Lấy danh sách booking, tự động kiểm tra và hủy các đơn quá 45 phút khách không đến"""
        bookings = self.service.load_bookings()
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        updated = False

        for b in bookings:
            status = str(b.get("status", "")).strip()
            # Chỉ kiểm tra các lịch đang "Đã xác nhận" trong ngày hôm nay
            if status == "Đã xác nhận":
                b_date_raw = str(b.get("booking_date", "")).strip()
                b_date = b_date_raw.split(" ")[0].strip()
                b_time = str(b.get("booking_time", "")).strip()

                if b_date == today_str and b_time:
                    try:
                        booking_dt = datetime.strptime(f"{b_date} {b_time}", "%Y-%m-%d %H:%M")
                        # Nếu thời gian hiện tại đã vượt quá giờ đặt 45 phút mà khách chưa đến/chưa xác nhận
                        if now > booking_dt + timedelta(minutes=45):
                            b["status"] = "Đã hủy"
                            updated = True
                    except Exception:
                        pass

        if updated:
            self.service.save_bookings(bookings)

        return bookings

    def get_table_options(self):
        """Lấy danh sách bàn từ file tables.json cho Combobox"""
        return self.service.load_tables()

    def _validate_booking_rules(self, data, exclude_booking_id=None):
        """
        Kiểm tra các quy tắc đặt bàn:
        1. Tiền cọc tối thiểu ít nhất 50K / người (guest_count * 50,000).
        2. Các lịch đặt của cùng một bàn trong ngày phải cách nhau tối thiểu 30 phút.
        """
        table_id = data.get("table_id")
        booking_date = data.get("booking_date", datetime.now().strftime("%Y-%m-%d"))
        booking_time = data.get("booking_time")
        guest_count = int(data.get("guest_count", 1))
        deposit_amount = float(data.get("deposit_amount", 0))

        # Quy tắc 1: Tiền cọc tối thiểu 50K/người
        min_required_deposit = guest_count * 50000
        if deposit_amount < min_required_deposit:
            return False, f"Tiền cọc tối thiểu cho {guest_count} khách là {min_required_deposit:,.0f} VNĐ (50,000đ/người)!"

        target_date = str(booking_date).split(" ")[0].strip()
        try:
            new_dt_start = datetime.strptime(f"{target_date} {booking_time}", "%Y-%m-%d %H:%M")
            new_dt_end = new_dt_start + timedelta(hours=2)
        except Exception:
            return False, "Định dạng ngày giờ không hợp lệ!"

        bookings = self.service.load_bookings()
        for b in bookings:
            b_id = b.get("booking_id")
            if exclude_booking_id and b_id == exclude_booking_id:
                continue

            b_table = str(b.get("table_id", "")).strip()
            b_date_raw = str(b.get("booking_date", "")).strip()
            b_date = b_date_raw.split(" ")[0].strip()
            b_time = str(b.get("booking_time", "")).strip()
            b_status = str(b.get("status", "")).strip()

            if b_table == str(table_id).strip() and b_date == target_date and b_status != "Đã hủy":
                try:
                    existing_dt_start = datetime.strptime(f"{b_date} {b_time}", "%Y-%m-%d %H:%M")
                    existing_dt_end = existing_dt_start + timedelta(hours=2)

                    # Quy tắc 2: Các bàn phải cách nhau tối thiểu 30 phút
                    buffer_td = timedelta(minutes=30)
                    buffered_new_start = new_dt_start - buffer_td
                    buffered_new_end = new_dt_end + buffer_td

                    if max(buffered_new_start, existing_dt_start) < min(buffered_new_end, existing_dt_end):
                        return False, f"Trùng lịch hoặc không đủ khoảng cách tối thiểu 30 phút với lịch lúc {b_time} của bàn này!"
                except Exception:
                    pass

        return True, ""

    def add_booking(self, data):
        """Xử lý logic thêm mới lịch đặt bàn (Hỗ trợ nhận ngày từ DateEntry)"""
        is_valid, err_msg = self._validate_booking_rules(data)
        if not is_valid:
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(err_msg)
            return False, err_msg

        bookings = self.service.load_bookings()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Lấy ngày đặt từ data (được truyền từ DateEntry của View)
        booking_date = data.get("booking_date", today_str)

        new_booking = {
            "booking_id": f"B{str(uuid.uuid4().hex)[:5].upper()}",
            "table_id": data.get("table_id"),
            "customer_name": data.get("customer_name"),
            "customer_phone": data.get("customer_phone"),
            "booking_date": booking_date,  # Lưu ngày chuẩn từ DateEntry
            "booking_time": data.get("booking_time"),
            "guest_count": int(data.get("guest_count", 1)),
            "status": "Đã xác nhận",
            "pre_orders": data.get("pre_orders", []),
            "deposit_amount": float(data.get("deposit_amount", 0))
        }
        bookings.append(new_booking)
        success = self.service.save_bookings(bookings)
        return success, "Thêm lịch đặt thành công!" if success else "Lỗi khi lưu file!"

    def update_booking(self, booking_id, data):
        """Xử lý logic cập nhật thông tin lịch đặt bàn (Hỗ trợ cập nhật ngày mới từ DateEntry)"""
        is_valid, err_msg = self._validate_booking_rules(data, exclude_booking_id=booking_id)
        if not is_valid:
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(err_msg)
            return False, err_msg

        bookings = self.service.load_bookings()
        target_date = None
        for b in bookings:
            if b.get("booking_id") == booking_id:
                target_date = data.get("booking_date", b.get("booking_date"))
                break

        if target_date and self._validate_booking_rules(data, exclude_booking_id=booking_id)[0] == False:
            pass

        updated = False
        for b in bookings:
            if b.get("booking_id") == booking_id:
                b["table_id"] = data.get("table_id")
                b["customer_name"] = data.get("customer_name")
                b["customer_phone"] = data.get("customer_phone")
                b["guest_count"] = int(data.get("guest_count", 1))
                b["booking_time"] = data.get("booking_time")
                if "booking_date" in data:
                    b["booking_date"] = data.get("booking_date")  # Cập nhật ngày mới từ DateEntry
                if "deposit_amount" in data:
                    b["deposit_amount"] = float(data.get("deposit_amount", 0))
                updated = True
                break
        
        if updated:
            success = self.service.save_bookings(bookings)
            return success, "Cập nhật lịch đặt thành công!" if success else "Lỗi khi lưu file!"
        return False, "Không tìm thấy mã đặt bàn cần sửa!"

    def delete_booking(self, booking_id):
        """Xóa lịch đặt bàn, nếu không còn lịch nào khác trong ngày -> bàn tự động về 'Trống'"""
        bookings = self.service.load_bookings()
        
        target_table_id = None
        target_date = None
        for b in bookings:
            if b.get("booking_id") == booking_id:
                target_table_id = str(b.get("table_id", "")).strip()
                b_date_raw = str(b.get("booking_date", "")).strip()
                target_date = b_date_raw.split(" ")[0].strip()
                break

        new_bookings = [b for b in bookings if b.get("booking_id") != booking_id]
        if len(new_bookings) >= len(bookings):
            return False, "Không tìm thấy mã đặt bàn cần xóa!"

        success = self.service.save_bookings(new_bookings)
        if not success:
            return False, "Lỗi khi lưu file bookings.json!"

        if target_table_id and target_date:
            try:
                import os
                import json
                current_dir = os.path.dirname(os.path.abspath(__file__))
                t_path = os.path.join(current_dir, "..", "data", "tables.json")
                if not os.path.exists(t_path):
                    t_path = "data/tables.json"

                if os.path.exists(t_path):
                    with open(t_path, "r", encoding="utf-8") as f:
                        tables = json.load(f)

                    has_other_booking = False
                    for b in new_bookings:
                        b_table = str(b.get("table_id", "")).strip()
                        b_date_raw = str(b.get("booking_date", "")).strip()
                        b_date = b_date_raw.split(" ")[0].strip()
                        b_status = str(b.get("status", "")).strip()

                        if b_table == target_table_id and b_date == target_date and b_status not in ["Đã hủy", "Đã hoàn thành"]:
                            has_other_booking = True
                            break

                    for t in tables:
                        t_name = str(t.get("name", "")).strip()
                        t_id = str(t.get("id", "")).strip()
                        if t_name == target_table_id or t_id == target_table_id:
                            current_status = str(t.get("status", ""))
                            if current_status != "Đang phục vụ":
                                if has_other_booking:
                                    t["status"] = "Đã đặt"
                                else:
                                    t["status"] = "Trống"  # Hoàn thành/hết lịch thì về Trống
                                    t["orders"] = []
                                    t["start_time"] = None
                            break

                    with open(t_path, "w", encoding="utf-8") as f:
                        json.dump(tables, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print("Lỗi đồng bộ trạng thái bàn:", e)

        return True, "Đã xóa lịch đặt và cập nhật trạng thái bàn thành công!"