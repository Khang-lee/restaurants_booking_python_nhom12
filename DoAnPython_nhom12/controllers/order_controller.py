import os
import json
from datetime import datetime
from services.order_service import OrderService

class OrderController:
    def __init__(self, table=None):
        self.table = table
        self.service = OrderService()
        self.menu_items = self.service.load_menu_data()
        self.selected_category = "Tất cả"
        self.current_order = []
        if self.table and hasattr(self.table, "orders") and self.table.orders:
            self.current_order = self.table.orders

        # Khi mở bàn gọi món, nếu bàn đang Trống hoặc Đã đặt mà bắt đầu thao tác -> Chuyển sang Đang phục vụ trên memory
        if self.table:
            current_status = getattr(self.table, "status", "Trống")
            if current_status in ["Trống", "Đã đặt"]:
                self.table.status = "Đang phục vụ"
                if not getattr(self.table, "start_time", None):
                    self.table.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_bookings_file_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "..", "data", "bookings.json")
        if not os.path.exists(file_path):
            return "data/bookings.json"
        return file_path

    def _get_tables_file_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "..", "data", "tables.json")
        if not os.path.exists(file_path):
            return "data/tables.json"
        return file_path

    def get_elapsed_time(self):
        """Tính thời gian bàn đang phục vụ"""
        if not self.table or not getattr(self.table, 'start_time', None):
            return "00:00:00"
        try:
            start_dt = datetime.strptime(str(self.table.start_time), "%Y-%m-%d %H:%M:%S")
            diff = datetime.now() - start_dt
            secs = int(diff.total_seconds())
            if secs < 0:
                return "00:00:00"
            hrs = secs // 3600
            mins = (secs % 3600) // 60
            s = secs % 60
            return f"{hrs:02d}:{mins:02d}:{s:02d}"
        except Exception:
            return "00:00:00"

    def get_nearest_booking_info(self):
        """Lấy lịch đặt bàn gần nhất tiếp theo trong ngày (ưu tiên lịch chưa hoàn thành)"""
        if not self.table:
            return None
        
        table_name = getattr(self.table, "name", str(self.table))
        table_id = getattr(self.table, "id", None)
        
        valid_identifiers = {str(table_name).strip()}
        if table_id:
            valid_identifiers.add(str(table_id).strip())

        try:
            file_path = self._get_bookings_file_path()
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                today_str = datetime.now().strftime("%Y-%m-%d")
                now = datetime.now()
                
                valid_bookings = []
                for b in bookings:
                    b_table = str(b.get("table_id", "")).strip()
                    b_date_raw = str(b.get("booking_date", "")).strip()
                    b_date = b_date_raw.split(" ")[0] if " " in b_date_raw else b_date_raw
                    status = str(b.get("status", "")).strip()
                    
                    if b_table in valid_identifiers and b_date == today_str and status not in ["Đã hoàn thành", "Đã hủy"]:
                        dt_str = f"{b_date} {b.get('booking_time')}"
                        try:
                            b_time_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                            diff_mins = int((b_time_dt - now).total_seconds() / 60)
                            valid_bookings.append({
                                "booking_id": b.get("booking_id"),
                                "diff_mins": diff_mins,
                                "customer_name": b.get("customer_name", "Khách vãng lai"),
                                "booking_time": b.get("booking_time"),
                                "guests": b.get("guest_count", 1),
                                "status": status,
                                "dt": b_time_dt
                            })
                        except Exception:
                            pass
                
                if valid_bookings:
                    valid_bookings.sort(key=lambda x: abs(x["diff_mins"]))
                    return valid_bookings[0]
        except Exception as e:
            print("Lỗi đọc bookings trong OrderController:", e)
        return None

    def get_table_bookings(self):
        """Lấy danh sách tất cả các lịch đặt trong ngày của bàn (trừ lịch đã hủy)"""
        if not self.table:
            return []
        
        table_name = getattr(self.table, "name", str(self.table))
        table_id = getattr(self.table, "id", None)
        
        valid_identifiers = {str(table_name).strip()}
        if table_id:
            valid_identifiers.add(str(table_id).strip())

        try:
            t_path = self._get_tables_file_path()
            if os.path.exists(t_path):
                with open(t_path, "r", encoding="utf-8") as f:
                    tables = json.load(f)
                    for t in tables:
                        if t.get("name") == table_name or t.get("id") == table_id:
                            if t.get("id"): valid_identifiers.add(str(t.get("id")).strip())
                            if t.get("name"): valid_identifiers.add(str(t.get("name")).strip())

            file_path = self._get_bookings_file_path()
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                today_str = datetime.now().strftime("%Y-%m-%d")
                matched_bookings = []
                for b in bookings:
                    b_table = str(b.get("table_id", "")).strip()
                    b_date_raw = str(b.get("booking_date", "")).strip()
                    b_date = b_date_raw.split(" ")[0] if " " in b_date_raw else b_date_raw
                    status = str(b.get("status", "")).strip()
                    
                    if b_table in valid_identifiers and b_date == today_str and status != "Đã hủy":
                        matched_bookings.append(b)
                return matched_bookings
        except Exception as e:
            print("Lỗi khi lấy danh sách đặt bàn trong OrderController:", e)
        return []

    def confirm_customer_arrival(self, booking_id):
        """Xác nhận khách đến: Chuyển booking sang 'Đang phục vụ' và bàn sang 'Đang phục vụ'"""
        if not booking_id or not self.table:
            return False, "Không xác định được lịch đặt hoặc bàn!"
        
        table_name = getattr(self.table, "name", str(self.table))
        table_id = getattr(self.table, "id", None)
        
        valid_identifiers = {str(table_name).strip()}
        if table_id:
            valid_identifiers.add(str(table_id).strip())

        try:
            b_path = self._get_bookings_file_path()
            updated = False
            if os.path.exists(b_path):
                with open(b_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                for b in bookings:
                    if b.get("booking_id") == booking_id:
                        b["status"] = "Đang phục vụ"
                        updated = True
                        break
                
                if updated:
                    with open(b_path, "w", encoding="utf-8") as f:
                        json.dump(bookings, f, ensure_ascii=False, indent=2)

            t_path = self._get_tables_file_path()
            if os.path.exists(t_path):
                with open(t_path, "r", encoding="utf-8") as f:
                    tables = json.load(f)
                
                for t in tables:
                    if t.get("name") == table_name or t.get("id") == table_id or t.get("name") == table_id or t.get("id") == table_name:
                        t["status"] = "Đang phục vụ"
                        if not t.get("start_time"):
                            t["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(t_path, "w", encoding="utf-8") as f:
                    json.dump(tables, f, ensure_ascii=False, indent=2)

            if hasattr(self.table, "status"):
                self.table.status = "Đang phục vụ"
            if hasattr(self.table, "start_time") and not self.table.start_time:
                self.table.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return True, "Đã xác nhận khách đến, bàn chuyển sang Đang phục vụ!"
        except Exception as e:
            print("Lỗi xác nhận khách đến:", e)
            return False, str(e)

    def save_table_state_to_json(self):
        """Đồng bộ trạng thái và danh sách món ăn từ bộ nhớ tạm lên tables.json, tự động trả về Trống nếu không có món và không có lịch đặt"""
        if not self.table:
            return
        table_name = getattr(self.table, "name", str(self.table))
        table_id = getattr(self.table, "id", None)
        
        try:
            t_path = self._get_tables_file_path()
            if os.path.exists(t_path):
                with open(t_path, "r", encoding="utf-8") as f:
                    tables = json.load(f)
                
                has_booking = len(self.get_table_bookings()) > 0

                for t in tables:
                    if t.get("name") == table_name or t.get("id") == table_id:
                        if not self.current_order:
                            t["orders"] = []
                            t["start_time"] = None
                            t["status"] = "Đã đặt" if has_booking else "Trống"
                        else:
                            t["status"] = getattr(self.table, "status", "Đang phục vụ")
                            t["start_time"] = getattr(self.table, "start_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            t["orders"] = self.current_order
                
                with open(t_path, "w", encoding="utf-8") as f:
                    json.dump(tables, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Lỗi lưu trạng thái bàn lên JSON:", e)

    def transfer_table(self, target_table_name):
        """Thực hiện chuyển toàn bộ giỏ hàng, thời gian và cập nhật tables.json & bookings.json sang bàn đích"""
        if not self.table:
            return False, "Không xác định được bàn hiện tại!"
        
        current_table_name = getattr(self.table, "name", str(self.table))
        table_id = getattr(self.table, "id", None)
        
        if current_table_name == target_table_name:
            return False, "Không thể chuyển đến chính bàn đang ngồi!"

        valid_identifiers = {str(current_table_name).strip()}
        if table_id:
            valid_identifiers.add(str(table_id).strip())

        try:
            t_path = self._get_tables_file_path()
            if not os.path.exists(t_path):
                return False, "Không tìm thấy file tables.json!"

            with open(t_path, "r", encoding="utf-8") as f:
                tables = json.load(f)

            source_table = None
            target_table = None

            for t in tables:
                t_name = str(t.get("name", "")).strip()
                t_id = str(t.get("id", "")).strip()
                if t_name in valid_identifiers or t_id in valid_identifiers:
                    source_table = t
                elif t_name == target_table_name or t_id == target_table_name:
                    target_table = t

            if not target_table:
                return False, f"Không tìm thấy bàn đích [{target_table_name}]!"

            if str(target_table.get("status")) == "Đang phục vụ":
                return False, f"Bàn đích [{target_table_name}] đang có khách phục vụ, không thể chuyển sang!"

            # 1. Chuyển orders và start_time sang bàn đích
            target_table["orders"] = self.current_order
            current_start_time = getattr(self.table, "start_time", None) or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            target_table["start_time"] = current_start_time
            target_table["status"] = "Đang phục vụ"

            # 2. Cập nhật lại table_id trong bookings.json cho các lịch của bàn cũ trong ngày
            b_path = self._get_bookings_file_path()
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            if os.path.exists(b_path):
                with open(b_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                for b in bookings:
                    b_table = str(b.get("table_id", "")).strip()
                    b_date = str(b.get("booking_date", "")).split(" ")[0]
                    if b_table in valid_identifiers and b_date == today_str and b.get("status") in ["Đang phục vụ", "Đã xác nhận", "Đã đặt"]:
                        b["table_id"] = target_table_name

                with open(b_path, "w", encoding="utf-8") as f:
                    json.dump(bookings, f, ensure_ascii=False, indent=2)

            # Kiểm tra xem bàn cũ còn lịch đặt nào khác chưa hoàn thành không
            has_other_booking = False
            if os.path.exists(b_path):
                with open(b_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                for b in bookings:
                    b_table = str(b.get("table_id", "")).strip()
                    b_date = str(b.get("booking_date", "")).split(" ")[0]
                    b_status = str(b.get("status", "")).strip()
                    if b_table == target_table_name and b_date == today_str and b_status not in ["Đã hủy", "Đã hoàn thành"]:
                        has_other_booking = True
                        break

            if source_table:
                source_table["orders"] = []
                source_table["start_time"] = None
                source_table["status"] = "Đã đặt" if has_other_booking else "Trống"

            with open(t_path, "w", encoding="utf-8") as f:
                json.dump(tables, f, ensure_ascii=False, indent=2)

            if self.table:
                self.table.orders = []
                self.table.start_time = None
                self.table.status = "Đã đặt" if has_other_booking else "Trống"

            return True, f"Đã chuyển thành công sang {target_table_name}!"
        except Exception as e:
            print("Lỗi chuyển bàn:", e)
            return False, str(e)

    def filter_menu(self, category, keyword=""):
        filtered = self.menu_items
        if category and category != "Tất cả" and category != "📅 Đặt bàn":
            filtered = [m for m in filtered if m.get("category") == category]
        if keyword:
            kw = keyword.lower()
            filtered = [m for m in filtered if kw in m.get("name", "").lower()]
        return filtered

    def add_item_to_order(self, item):
        item_id = item.get("id")
        for ord_item in self.current_order:
            if ord_item.get("id") == item_id:
                ord_item["qty"] += 1
                ord_item["total"] = ord_item["qty"] * ord_item["price"]
                return
        
        new_ord = {
            "id": item_id,
            "name": item.get("name"),
            "price": item.get("price"),
            "qty": 1,
            "total": item.get("price")
        }
        self.current_order.append(new_ord)

    def increase_item_qty(self, idx):
        if 0 <= idx < len(self.current_order):
            self.current_order[idx]["qty"] += 1
            self.current_order[idx]["total"] = self.current_order[idx]["qty"] * self.current_order[idx]["price"]

    def decrease_item_qty(self, idx):
        if 0 <= idx < len(self.current_order):
            if self.current_order[idx]["qty"] > 1:
                self.current_order[idx]["qty"] -= 1
                self.current_order[idx]["total"] = self.current_order[idx]["qty"] * self.current_order[idx]["price"]
            else:
                self.current_order.pop(idx)

    def remove_item(self, idx):
        if 0 <= idx < len(self.current_order):
            self.current_order.pop(idx)

    def calculate_total(self):
        return sum(item.get("total", 0) for item in self.current_order)

    def save_on_exit(self):
        """Cập nhật trạng thái và lưu xuống tables.json khi thoát giao diện gọi món"""
        if self.table:
            has_booking = len(self.get_table_bookings()) > 0
            if not self.current_order:
                if has_booking:
                    self.table.status = "Đã đặt"
                else:
                    self.table.status = "Trống"
                    self.table.start_time = None
            
            if hasattr(self.table, "orders"):
                self.table.orders = self.current_order
            
            self.save_table_state_to_json()

    def checkout(self):
        """Xử lý thanh toán: Hoàn thành booking, cập nhật trạng thái bàn. Nếu không còn lịch hẹn nào khác -> Bàn về 'Trống'."""
        if not self.current_order:
            return False, "Hóa đơn trống, không thể thanh toán!"
        
        if not self.table:
            return False, "Không xác định được thông tin bàn!"

        table_name = getattr(self.table, "name", str(self.table))
        table_id = getattr(self.table, "id", None)
        
        valid_identifiers = {str(table_name).strip()}
        if table_id:
            valid_identifiers.add(str(table_id).strip())

        try:
            b_path = self._get_bookings_file_path()
            remaining_bookings = []
            if os.path.exists(b_path):
                with open(b_path, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
                
                today_str = datetime.now().strftime("%Y-%m-%d")
                for b in bookings:
                    b_table = str(b.get("table_id", "")).strip()
                    b_date_raw = str(b.get("booking_date", "")).strip()
                    b_date = b_date_raw.split(" ")[0] if " " in b_date_raw else b_date_raw
                    
                    if b_table in valid_identifiers and b_date == today_str and b.get("status") == "Đang phục vụ":
                        b["status"] = "Đã hoàn thành"
                    remaining_bookings.append(b)
                
                with open(b_path, "w", encoding="utf-8") as f:
                    json.dump(remaining_bookings, f, ensure_ascii=False, indent=2)

            # Kiểm tra xem bàn này còn lịch đặt nào khác chưa hoàn thành/chưa hủy trong hôm nay không
            has_future_booking = False
            for b in remaining_bookings:
                b_table = str(b.get("table_id", "")).strip()
                b_date_raw = str(b.get("booking_date", "")).strip()
                b_date = b_date_raw.split(" ")[0] if " " in b_date_raw else b_date_raw
                
                if b_table in valid_identifiers and b_date == datetime.now().strftime("%Y-%m-%d"):
                    if b.get("status") not in ["Đã hoàn thành", "Đã hủy"]:
                        has_future_booking = True
                        break

            t_path = self._get_tables_file_path()
            if os.path.exists(t_path):
                with open(t_path, "r", encoding="utf-8") as f:
                    tables = json.load(f)
                
                for t in tables:
                    if str(t.get("name", "")).strip() in valid_identifiers or str(t.get("id", "")).strip() in valid_identifiers:
                        t["orders"] = []
                        t["start_time"] = None
                        # QUY TẮC: Nếu đã hoàn thành hết và không còn lịch nào khác -> Bàn về "Trống"
                        if has_future_booking:
                            t["status"] = "Đã đặt"
                        else:
                            t["status"] = "Trống"
                
                with open(t_path, "w", encoding="utf-8") as f:
                    json.dump(tables, f, ensure_ascii=False, indent=2)

            self.current_order = []
            if hasattr(self.table, "orders"):
                self.table.orders = []
            if hasattr(self.table, "status"):
                self.table.status = "Đã đặt" if has_future_booking else "Trống"

            return True, table_name
        except Exception as e:
            print("Lỗi trong quá trình thanh toán:", e)
            return False, str(e)