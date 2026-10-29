class Table:
    def __init__(self, id, name, area, capacity=4, status="Trống", x=0, y=0):
        self.id = id
        self.name = name
        self.area = area
        self.capacity = capacity
        self.status = status  # Trống, Đã đặt, Đang phục vụ
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "area": self.area,
            "capacity": self.capacity,
            "status": self.status,
            "x": self.x,
            "y": self.y
        }