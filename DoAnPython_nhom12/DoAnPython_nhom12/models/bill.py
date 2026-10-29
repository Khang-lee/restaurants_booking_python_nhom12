import json
import os
import uuid
from datetime import datetime

class Bill:
    def __init__(self, table_name, total_amount, payment_method, customer_name="Khách vãng lai", items=None):
        self.id = "BILL-" + str(uuid.uuid4().hex)[:6].upper()
        self.table_name = table_name
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.items = items if items else []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "Đã thanh toán"

    def to_dict(self):
        return {
            "id": self.id,
            "table_name": self.table_name,
            "customer_name": self.customer_name,
            "total_amount": self.total_amount,
            "payment_method": self.payment_method,
            "items": self.items,
            "created_at": self.created_at,
            "status": self.status
        }

def save_bill_to_json(bill_dict):
    """Hàm lưu Bill dạng dict vào file data/bills.json"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Lùi 1 cấp từ thư mục 'models' ra thư mục gốc, rồi vào thư mục 'data'
    file_path = os.path.join(current_dir, "..", "data", "bills.json")
    
    bills = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bills = json.load(f)
        except Exception:
            bills = []
            
    bills.append(bill_dict)
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(bills, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Lỗi khi lưu Bill: {e}")