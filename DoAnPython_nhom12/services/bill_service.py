import json
import os

class BillService:
    def __init__(self):
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(CURRENT_DIR, "..", "..", "data", "bills.json"),
            os.path.join(CURRENT_DIR, "..", "data", "bills.json"),
            os.path.join("data", "bills.json")
        ]
        
        self.DATA_FILE = possible_paths[0]
        for path in possible_paths:
            if os.path.exists(path):
                self.DATA_FILE = path
                break

    def load_bills(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Lỗi đọc file bills.json: {e}")
        return []