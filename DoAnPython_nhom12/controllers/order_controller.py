import json
import os
import shutil
from datetime import datetime
from services.order_service import OrderService

try:
    from services.monan_service import MonAnService
except (ImportError, ModuleNotFoundError):
    MonAnService = None


class OrderController:
    def __init__(self, table=None):
        self.table = table
        self.service = OrderService()
        self.monan_service = MonAnService() if MonAnService is not None else None
        self.menu_items = self.service.load_menu_data()
        self.selected_category = "Tất cả"
        self.current_order = []
        self._latest_dishes_by_name = {}
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

    def _get_menu_json_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "..", "data", "menumonan.json")
        if not os.path.exists(file_path):
            return "data/menumonan.json"
        return file_path

    def get_dishes_data(self):
        """Đọc danh sách món từ MonAnService / data/menumonan.json và lưu cache tra cứu tồn kho."""
        dishes_list = []
        expired_items = []

        if self.monan_service is not None:
            expired_items = self.monan_service.check_and_expire_dishes() or []
            dishes = self.monan_service.load_dishes()
            if dishes:
                dishes_list = [d.to_dict() for d in dishes]

        if not dishes_list:
            menu_path = self._get_menu_json_path()
            if os.path.exists(menu_path):
                try:
                    with open(menu_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        dishes_list = [item for item in data if isinstance(item, dict)]
                except (json.JSONDecodeError, OSError):
                    dishes_list = []

        self._latest_dishes_by_name = {
            str(d.get("name") or "").strip().lower(): d
            for d in dishes_list
            if str(d.get("name") or "").strip()
        }
        return dishes_list, expired_items

    def get_dish_stock_qty(self, item: dict) -> int:
        """Lấy số lượng phục vụ mới nhất của món từ kho/JSON."""
        name_key = str(item.get("name") or "").strip().lower()
        if name_key in self._latest_dishes_by_name:
            latest = self._latest_dishes_by_name[name_key]
            try:
                return max(0, int(latest.get("number", 0)))
            except (TypeError, ValueError):
                return 0
        if "number" in item:
            try:
                return max(0, int(item.get("number", 0)))
            except (TypeError, ValueError):
                return 0
        return 999999

    def get_categories_list(self):
        """Lấy danh sách loại món từ dữ liệu món ăn và menu hiện tại."""
        categories = ["Tất cả", "Món ăn", "Đồ uống", "Lẩu", "Khai vị", "Tráng miệng", "Khác"]
        seen = {c.lower() for c in categories}

        dishes_list, _ = self.get_dishes_data()
        for item in dishes_list:
            cat = str(item.get("category") or "").strip()
            if cat and cat.lower() not in seen:
                seen.add(cat.lower())
                categories.insert(-1, cat)

        for item in self.filter_menu("Tất cả", ""):
            cat = str(item.get("category") or "").strip()
            if cat and cat.lower() not in seen:
                seen.add(cat.lower())
                categories.insert(-1, cat)

        categories.append("📅 Đặt bàn")
        return categories

    def get_transferable_table_names(self):
        """Lấy danh sách tên bàn hợp lệ có thể chuyển tới."""
        table_options = []
        try:
            t_path = self._get_tables_file_path()
            if os.path.exists(t_path):
                with open(t_path, "r", encoding="utf-8") as f:
                    all_tables = json.load(f)

                current_name = getattr(self.table, "name", str(self.table))
                for t in all_tables:
                    t_name = str(t.get("name", "")).strip()
                    t_status = str(t.get("status", "")).strip()
                    if t_name != current_name and t_status != "Đang phục vụ":
                        table_options.append(t_name)
        except Exception as e:
            print("Lỗi lấy danh sách bàn:", e)
        return table_options

    def deduct_stock_after_checkout(self, ordered_items: list[dict]):
        """Trừ số lượng món đã thanh toán trong kho (menumonan.json)."""
        ordered_qty_by_name = {}
        for row in ordered_items or []:
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            try:
                qty = int(row.get("qty", 0))
            except (TypeError, ValueError):
                qty = 0
            if qty > 0:
                key = name.lower()
                ordered_qty_by_name[key] = ordered_qty_by_name.get(key, 0) + qty

        if not ordered_qty_by_name:
            return

        menu_path = self._get_menu_json_path()
        if not os.path.exists(menu_path):
            return

        try:
            with open(menu_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return

            changed = False
            for dish in data:
                if not isinstance(dish, dict):
                    continue
                d_key = str(dish.get("name") or "").strip().lower()
                if d_key in ordered_qty_by_name:
                    try:
                        current_qty = int(dish.get("number", 0))
                    except (TypeError, ValueError):
                        current_qty = 0
                    new_qty = max(0, current_qty - ordered_qty_by_name[d_key])
                    if new_qty != current_qty:
                        dish["number"] = new_qty
                        changed = True

            if changed:
                bak_path = f"{menu_path}.bak"
                shutil.copy2(menu_path, bak_path)
                with open(menu_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Lỗi cập nhật tồn kho sau thanh toán:", e)

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
                            if t.get("id"):
                                valid_identifiers.add(str(t.get("id")).strip())
                            if t.get("name"):
                                valid_identifiers.add(str(t.get("name")).strip())

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

            target_table["orders"] = self.current_order
            current_start_time = getattr(self.table, "start_time", None) or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            target_table["start_time"] = current_start_time
            target_table["status"] = "Đang phục vụ"

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
        dishes_list, _ = self.get_dishes_data()
        source_items = dishes_list if dishes_list else self.menu_items
        filtered = source_items
        if category and category != "Tất cả" and category != "📅 Đặt bàn":
            cat_l = str(category).strip().lower()
            filtered = [m for m in filtered if str(m.get("category") or "").strip().lower() == cat_l]
        if keyword:
            kw = str(keyword).strip().lower()
            filtered = [
                m for m in filtered
                if kw in str(m.get("name") or "").lower()
                or kw in str(m.get("category") or "").lower()
                or kw in str(m.get("note") or "").lower()
            ]
        return filtered

    def add_item_to_order(self, item):
        stock_qty = self.get_dish_stock_qty(item)
        dish_name = str(item.get("name") or "").strip()
        if stock_qty <= 0:
            return False, f"Món '{dish_name}' đã hết số lượng phục vụ."

        already_in_order = 0
        for row in self.current_order:
            if str(row.get("name") or "").strip().lower() == dish_name.lower():
                try:
                    already_in_order += int(row.get("qty", 0))
                except (TypeError, ValueError):
                    pass

        if already_in_order >= stock_qty:
            return False, f"Món '{dish_name}' chỉ còn {stock_qty} phần có thể phục vụ."

        item_id = item.get("id")
        for ord_item in self.current_order:
            if ord_item.get("id") == item_id or str(ord_item.get("name") or "").strip().lower() == dish_name.lower():
                ord_item["qty"] += 1
                ord_item["total"] = ord_item["qty"] * ord_item["price"]
                return True, ""

        new_ord = {
            "id": item_id,
            "name": dish_name,
            "price": item.get("price"),
            "qty": 1,
            "total": item.get("price"),
        }
        self.current_order.append(new_ord)
        return True, ""

    def increase_item_qty(self, idx):
        if 0 <= idx < len(self.current_order):
            row = self.current_order[idx]
            stock_qty = self.get_dish_stock_qty(row)
            if stock_qty <= 0:
                return False, f"Món '{row.get('name', '')}' đã hết số lượng phục vụ."
            try:
                cur_qty = int(row.get("qty", 0))
            except (TypeError, ValueError):
                cur_qty = 0
            if cur_qty >= stock_qty:
                return False, f"Món '{row.get('name', '')}' chỉ còn {stock_qty} phần có thể phục vụ."
            self.current_order[idx]["qty"] += 1
            self.current_order[idx]["total"] = self.current_order[idx]["qty"] * self.current_order[idx]["price"]
            return True, ""
        return False, "Món không tồn tại trong hóa đơn."

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
        """Xử lý thanh toán: Trừ tồn kho, hoàn thành booking, cập nhật trạng thái bàn."""
        if not self.current_order:
            return False, "Hóa đơn trống, không thể thanh toán!"

        if not self.table:
            return False, "Không xác định được thông tin bàn!"

        ordered_snapshot = list(self.current_order)
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
                        t["status"] = "Đã đặt" if has_future_booking else "Trống"

                with open(t_path, "w", encoding="utf-8") as f:
                    json.dump(tables, f, ensure_ascii=False, indent=2)

            self.deduct_stock_after_checkout(ordered_snapshot)

            self.current_order = []
            if hasattr(self.table, "orders"):
                self.table.orders = []
            if hasattr(self.table, "status"):
                self.table.status = "Đã đặt" if has_future_booking else "Trống"

            return True, table_name
        except Exception as e:
            print("Lỗi trong quá trình thanh toán:", e)
            return False, str(e)