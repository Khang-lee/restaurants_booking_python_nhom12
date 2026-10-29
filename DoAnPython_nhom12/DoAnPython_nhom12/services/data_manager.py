import json
import os


class DataManager:

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.tables_file = os.path.join(data_dir, "tables.json")
        self.bookings_file = os.path.join(data_dir, "bookings.json")
        self.customers_file = os.path.join(data_dir, "customers.json")
        self.users_file = os.path.join(data_dir, "users.json")
        self.invoices_file = os.path.join(data_dir, "invoices.json")

    def _read_json(self, file_path):
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, file_path, data):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # Đọc dữ liệu
    def load_tables(self):
        return self._read_json(self.tables_file)

    def load_bookings(self):
        return self._read_json(self.bookings_file)

    def load_customers(self):
        return self._read_json(self.customers_file)

    def load_users(self):
        return self._read_json(self.users_file)

    def get_users(self):
        return self.load_users()  # Bổ sung để AuthService gọi trực tiếp

    def load_invoices(self):
        return self._read_json(self.invoices_file)

    # Ghi dữ liệu
    def save_tables(self, data):
        self._write_json(self.tables_file, data)

    def save_bookings(self, data):
        self._write_json(self.bookings_file, data)

    def save_customers(self, data):
        self._write_json(self.customers_file, data)

    def save_users(self, data):
        self._write_json(self.users_file, data)

    def save_invoices(self, data):
        self._write_json(self.invoices_file, data)