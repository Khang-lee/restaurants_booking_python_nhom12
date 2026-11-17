import json
import os

class FloorplanService:
    def __init__(self):
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        self.TABLE_FILE = self._find_path(curr_dir, "tables.json")
        self.BOOKING_FILE = self._find_path(curr_dir, "bookings.json")

    def _find_path(self, curr_dir, filename):
        paths = [
            os.path.join(curr_dir, "..", "..", "data", filename),
            os.path.join(curr_dir, "..", "data", filename),
            os.path.join("data", filename)
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return paths[0]

    def load_tables(self):
        if os.path.exists(self.TABLE_FILE):
            try:
                with open(self.TABLE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Lỗi đọc file tables.json: {e}")
        return []

    def save_tables(self, tables_data):
        try:
            with open(self.TABLE_FILE, "w", encoding="utf-8") as f:
                json.dump(tables_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi ghi file tables.json: {e}")
            return False

    def load_bookings(self):
        if os.path.exists(self.BOOKING_FILE):
            try:
                with open(self.BOOKING_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Lỗi đọc file bookings.json: {e}")
        return []