import uuid
from datetime import datetime
from services.floorplan_service import FloorplanService

class TableModel:
    def __init__(self, id, name, area, capacity=4, status="Trống", x=50, y=50, bookings=None, orders=None, start_time=None):
        self.id = id
        self.name = name
        self.area = area
        self.capacity = capacity
        self.status = status
        self.x = x
        self.y = y
        self.bookings = bookings if bookings is not None else []
        self.orders = orders if orders is not None else []
        self.start_time = start_time

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "area": self.area,
            "capacity": self.capacity, "status": self.status,
            "x": self.x, "y": self.y, "bookings": self.bookings,
            "orders": self.orders, "start_time": self.start_time
        }

class FloorplanController:
    def __init__(self, role="Lễ tân"):
        self.role = role
        self.service = FloorplanService()
        self.tables = []
        self.notified_bookings = set()
        self.load_data()

    def load_data(self):
        raw_data = self.service.load_tables()
        self.tables = [TableModel(**item) for item in raw_data]
        self.sync_tables_status()  # Tự động đồng bộ trạng thái bàn khi load

    def sync_tables_status(self):
        """Tự động chuyển về 'Trống' nếu bàn không đang phục vụ và không còn lịch đặt active nào trong ngày"""
        bookings = self.service.load_bookings()
        today_str = datetime.now().strftime("%Y-%m-%d")
        updated = False

        for table in self.tables:
            if table.status == "Đang phục vụ":
                continue

            table_name = str(table.name).strip()
            table_id = str(table.id).strip()

            has_active_booking = any(
                (str(b.get("table_id", "")).strip() == table_name or str(b.get("table_id", "")).strip() == table_id) and
                str(b.get("booking_date", "")).split(" ")[0] == today_str and
                str(b.get("status", "")).strip() in ["Đã xác nhận", "Đã đặt"]
                for b in bookings
            )

            if has_active_booking:
                if table.status != "Đã đặt":
                    table.status = "Đã đặt"
                    updated = True
            else:
                if table.status != "Trống":
                    table.status = "Trống"
                    table.orders = []
                    table.start_time = None
                    updated = True

        if updated:
            self.save_data()

    def save_data(self):
        raw_data = [t.to_dict() for t in self.tables]
        return self.service.save_tables(raw_data)

    def get_areas(self):
        return sorted(list(set(t.area for t in self.tables)))

    def add_table(self, area):
        new_t = TableModel(
            id=f"T-{uuid.uuid4().hex[:6].upper()}",
            name=f"Bàn mới {len(self.tables) + 1}",
            area=area,
            capacity=4,
            x=60,
            y=60
        )
        self.tables.append(new_t)
        self.save_data()
        return new_t

    def get_table_display_status(self, table):
        """Xác định trạng thái hiển thị thời gian thực của bàn"""
        if table.status == "Đang phục vụ":
            return "Đang phục vụ"
        
        # Kiểm tra xem hôm nay bàn có lịch đặt active không (bỏ qua hoàn thành/hủy)
        today_str = datetime.now().strftime("%Y-%m-%d")
        bookings = self.service.load_bookings()
        
        table_name = str(table.name).strip()
        table_id = str(table.id).strip()

        has_active_booking = any(
            (str(b.get("table_id", "")).strip() == table_name or str(b.get("table_id", "")).strip() == table_id) and 
            str(b.get("booking_date", "")).split(" ")[0] == today_str and 
            str(b.get("status", "")).strip() in ["Đã xác nhận", "Đã đặt"]
            for b in bookings
        )
        
        if has_active_booking:
            return "Đặt hôm nay"
        return "Trống"

    def calculate_elapsed_time(self, start_time_str):
        """Tính thời gian phục vụ theo thời gian thực (HH:MM:SS)"""
        if not start_time_str: return ""
        try:
            start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            diff = datetime.now() - start_dt
            total_seconds = max(0, int(diff.total_seconds()))
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except Exception:
            return ""

    def check_reminders(self):
        """Cảnh báo lịch đặt trước 30 phút"""
        try:
            bookings = self.service.load_bookings()
            now = datetime.now()
            reminders = []
            
            for b in bookings:
                if b.get("status") in ["Đã xác nhận", "Đã đặt"]:
                    dt_str = f"{b.get('booking_date')} {b.get('booking_time')}"
                    try:
                        b_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                        diff_mins = (b_time - now).total_seconds() / 60
                        
                        if 0 <= diff_mins <= 30:
                            b_id = b.get("booking_id", dt_str)
                            if b_id not in self.notified_bookings:
                                reminders.append(f"📌 Bàn: {b.get('table_id')} | Khách: {b.get('customer_name')} | Giờ đến: {b.get('booking_time')}")
                                self.notified_bookings.add(b_id)
                    except: pass
            return reminders
        except Exception as e:
            print("Lỗi nhắc lịch:", e)
            return []

    def is_overlapping(self, current_table, target_x, target_y, w=130, h=95):
        for other in self.tables:
            if other.id == current_table.id or other.area != current_table.area:
                continue
            if not (target_x + w <= other.x or target_x >= other.x + w or target_y + h <= other.y or target_y >= other.y + h):
                return True
        return False