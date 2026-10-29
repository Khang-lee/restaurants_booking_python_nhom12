class AuthService:

    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_user = None

    def login(self, username, password):
        users = self.data_manager.get_users()

        for user in users:
            if (
                user.get("username") == username
                and user.get("password") == password
            ):
                # Chuẩn hóa role mã hóa tiếng Anh để xử lý code
                role_raw = str(user.get("role", "")).lower()
                if "quản lý" in role_raw or "quanly" in role_raw:
                    user["role_code"] = "quanly"
                else:
                    user["role_code"] = "letan"

                self.current_user = user
                full_name = user.get("full_name", username)
                return True, f"Đăng nhập thành công! Chào mừng {full_name}."

        return False, "Tài khoản hoặc mật khẩu không chính xác!"

    def logout(self):
        self.current_user = None

    def get_current_user(self):
        return self.current_user