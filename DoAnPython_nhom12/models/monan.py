class MonAn:
    """Lớp dữ liệu OOP biểu diễn món ăn, ghi chú, số lượng tồn và hạn sử dụng."""

    def __init__(
        self,
        dish_id: str,
        name: str,
        price: int,
        category: str = "Món ăn",
        note: str = "",
        evaluate: str = "5.0",
        number: int = 0,
        expiration_date: str = "",
        image: str = "",
    ):
        self.id = str(dish_id).strip()
        self.name = str(name).strip()
        self.price = max(0, int(price))
        self.category = str(category).strip() or "Món ăn"
        self.note = str(note).strip()
        self.evaluate = str(evaluate).strip() or "5.0"
        self.number = max(0, int(number))
        self.expiration_date = str(expiration_date).strip()
        self.image = str(image).strip()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "note": self.note,
            "evaluate": self.evaluate,
            "number": self.number,
            "expiration_date": self.expiration_date,
            "image": self.image,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MonAn":
        try:
            price_val = int(float(data.get("price", 0)))
        except (TypeError, ValueError):
            price_val = 0

        try:
            num_val = int(float(data.get("number", 0)))
        except (TypeError, ValueError):
            num_val = 0

        return cls(
            dish_id=data.get("id", ""),
            name=data.get("name", ""),
            price=price_val,
            category=data.get("category", "Món ăn"),
            note=data.get("note", ""),
            evaluate=data.get("evaluate", "5.0"),
            number=max(0, num_val),
            expiration_date=data.get("expiration_date", ""),
            image=data.get("image", ""),
        )