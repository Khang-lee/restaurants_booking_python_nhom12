import json
import os

class OrderService:
    def __init__(self):
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "data"))
        if not os.path.exists(data_dir):
            data_dir = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data"))

        self.MENU_FILE = os.path.join(data_dir, "menumonan.json")
        self.TABLE_FILE = os.path.join(data_dir, "tables.json")
        self.BILL_FILE = os.path.join(data_dir, "bills.json")

    def load_menu_data(self):
        if os.path.exists(self.MENU_FILE):
            try:
                with open(self.MENU_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Lỗi đọc file menu: {e}")
        return []

    def save_tables_to_json(self, table):
        if not os.path.exists(self.TABLE_FILE): return
        try:
            with open(self.TABLE_FILE, "r", encoding="utf-8") as f:
                tables_data = json.load(f)

            for t in tables_data:
                if t.get("id") == table.id or t.get("name") == table.name:
                    t["status"] = table.status
                    t["orders"] = table.orders
                    t["start_time"] = getattr(table, 'start_time', None)
                    break

            with open(self.TABLE_FILE, "w", encoding="utf-8") as f:
                json.dump(tables_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi cập nhật file tables.json: {e}")

    def save_bill(self, new_bill):
        bills = []
        if os.path.exists(self.BILL_FILE):
            try:
                with open(self.BILL_FILE, "r", encoding="utf-8") as f:
                    bills = json.load(f)
            except: pass
        
        bills.append(new_bill)
        try:
            with open(self.BILL_FILE, "w", encoding="utf-8") as f:
                json.dump(bills, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu hóa đơn: {e}")