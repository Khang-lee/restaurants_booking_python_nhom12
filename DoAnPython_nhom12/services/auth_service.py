import json
import os

class AuthService:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
        # Xác định đường dẫn file users.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.user_file = os.path.join(current_dir, "..", "data", "users.json")
        if not os.path.exists(self.user_file):
            self.user_file = os.path.join(current_dir, "data", "users.json")
        if not os.path.exists(self.user_file):
            self.user_file = "data/users.json"

    def login(self, username, password):
        """Hàm xử lý đăng nhập được gọi từ LoginDialog"""
        if not os.path.exists(self.user_file):
            return False, "Không tìm thấy tệp dữ liệu người dùng!"

        try:
            with open(self.user_file, "r", encoding="utf-8") as f:
                users = json.load(f)
                
            for user in users:
                if user.get("username") == username and user.get("password") == password:
                    return True, user # Trả về trạng thái thành công và thông tin user
                    
            return False, "Tài khoản hoặc mật khẩu không chính xác!"
        except Exception as e:
            return False, f"Lỗi hệ thống: {str(e)}"