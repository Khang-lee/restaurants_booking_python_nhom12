class User:
    def __init__(self, username, password, full_name, role):
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role  # Lễ tân hoặc Quản lý

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "role": self.role
        }