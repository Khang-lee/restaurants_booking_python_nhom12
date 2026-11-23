import json
import os
import shutil
import uuid
from datetime import date, datetime
from models.monan import MonAn


class MonAnService:
    """Dịch vụ CRUD món ăn, cập nhật kho & hạn sử dụng, kiểm tra hết hạn."""

    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, file_path: str | None = None):
        if file_path:
            self.file_path = file_path
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.file_path = os.path.join(base_dir, "data", "menumonan.json")
        self.backup_path = f"{self.file_path}.bak"

    @staticmethod
    def _normalize_text(value: object) -> str:
        return " ".join(str(value or "").strip().split())

    @classmethod
    def _normalize_key(cls, value: object) -> str:
        return cls._normalize_text(value).lower()

    @classmethod
    def _parse_date(cls, date_str: object) -> date | None:
        raw = str(date_str or "").strip()
        if not raw:
            return None
        try:
            return datetime.strptime(raw, cls.DATE_FORMAT).date()
        except ValueError:
            return None

    def _read_json_list(self, path: str) -> list[MonAn] | None:
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, list):
                return None
            return [
                MonAn.from_dict(item)
                for item in raw
                if isinstance(item, dict) and self._normalize_text(item.get("name"))
            ]
        except (json.JSONDecodeError, OSError):
            return None

    def load_dishes(self) -> list[MonAn]:
        dishes = self._read_json_list(self.file_path)
        if dishes is not None:
            return dishes

        backup_dishes = self._read_json_list(self.backup_path)
        return backup_dishes if backup_dishes is not None else []

    def save_dishes(self, dishes: list[MonAn]) -> tuple[bool, str]:
        try:
            parent_dir = os.path.dirname(self.file_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            if os.path.exists(self.file_path):
                shutil.copy2(self.file_path, self.backup_path)

            payload = [d.to_dict() for d in dishes]
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return True, "Lưu dữ liệu món ăn thành công."
        except OSError as exc:
            return False, f"Lỗi ghi file món ăn: {exc}"

    def is_duplicate_name_in_category(
        self, name: str, category: str, exclude_id: str | None = None
    ) -> bool:
        target_name = self._normalize_key(name)
        target_cat = self._normalize_key(category)
        for dish in self.load_dishes():
            if exclude_id and dish.id == exclude_id:
                continue
            if (
                self._normalize_key(dish.name) == target_name
                and self._normalize_key(dish.category) == target_cat
            ):
                return True
        return False

    def create_dish(
        self,
        name: str,
        price: int,
        category: str = "Món ăn",
        note: str = "",
        evaluate: str = "5.0",
        image: str = "",
    ) -> tuple[bool, str]:
        clean_name = self._normalize_text(name)
        clean_cat = self._normalize_text(category) or "Món ăn"

        if not clean_name:
            return False, "Tên món ăn không được để trống."
        if price <= 0:
            return False, "Giá món ăn phải lớn hơn 0."
        if self.is_duplicate_name_in_category(clean_name, clean_cat):
            return False, f"Món '{clean_name}' đã tồn tại trong loại '{clean_cat}'!"

        dishes = self.load_dishes()
        new_dish = MonAn(
            dish_id=f"M-{uuid.uuid4().hex[:5].upper()}",
            name=clean_name,
            price=price,
            category=clean_cat,
            note=str(note or "").strip(),
            evaluate=self._normalize_text(evaluate) or "5.0",
            number=0,
            expiration_date="",
            image=str(image or "").strip(),
        )
        dishes.append(new_dish)

        ok, msg = self.save_dishes(dishes)
        if not ok:
            return False, msg
        return True, f"Đã thêm món '{clean_name}' (SL = 0). Hãy cập nhật số lượng và hạn sử dụng."

    def update_dish(
        self,
        dish_id: str,
        name: str,
        price: int,
        category: str = "Món ăn",
        note: str = "",
        evaluate: str = "5.0",
        image: str = "",
    ) -> tuple[bool, str]:
        clean_name = self._normalize_text(name)
        clean_cat = self._normalize_text(category) or "Món ăn"

        if not clean_name:
            return False, "Tên món ăn không được để trống."
        if price <= 0:
            return False, "Giá món ăn phải lớn hơn 0."
        if self.is_duplicate_name_in_category(clean_name, clean_cat, exclude_id=dish_id):
            return False, f"Món '{clean_name}' đã trùng tên trong loại '{clean_cat}'!"

        dishes = self.load_dishes()
        for dish in dishes:
            if dish.id == dish_id:
                dish.name = clean_name
                dish.price = price
                dish.category = clean_cat
                dish.note = str(note or "").strip()
                dish.evaluate = self._normalize_text(evaluate) or "5.0"
                clean_img = str(image or "").strip()
                if clean_img:
                    dish.image = clean_img
                return self.save_dishes(dishes)
        return False, "Không tìm thấy món ăn để cập nhật."

    def delete_dish(self, dish_id: str) -> tuple[bool, str]:
        dishes = self.load_dishes()
        filtered = [d for d in dishes if d.id != dish_id]
        if len(filtered) == len(dishes):
            return False, "Không tìm thấy món ăn để xóa."
        return self.save_dishes(filtered)

    def update_stock_and_expiry(
        self,
        dish_id: str,
        added_qty: int,
        expiration_date: str,
        replace_mode: bool = False,
    ) -> tuple[bool, str]:
        if added_qty < 0:
            return False, "Số lượng không được âm."

        exp_dt = self._parse_date(expiration_date)
        if exp_dt is None:
            return False, "Hạn sử dụng không đúng định dạng YYYY-MM-DD."

        today = date.today()
        exp_str = exp_dt.strftime(self.DATE_FORMAT)
        dishes = self.load_dishes()

        for dish in dishes:
            if dish.id != dish_id:
                continue

            if exp_dt < today:
                dish.expiration_date = exp_str
                dish.number = 0
                self.save_dishes(dishes)
                return False, f"Món '{dish.name}' đã hết hạn sử dụng nên số lượng được đưa về 0!"

            dish.expiration_date = exp_str
            dish.number = added_qty if replace_mode else max(0, dish.number) + added_qty
            return self.save_dishes(dishes)

        return False, "Không tìm thấy món ăn."

    def deduct_stock(self, dish_id: str, qty: int) -> tuple[bool, str]:
        """Trừ số lượng món trong kho khi phục vụ/thanh toán."""
        if qty <= 0:
            return False, "Số lượng trừ phải lớn hơn 0."

        dishes = self.load_dishes()
        for dish in dishes:
            if dish.id != dish_id:
                continue
            if dish.number < qty:
                return False, f"Món '{dish.name}' chỉ còn {dish.number} phần."
            dish.number -= qty
            return self.save_dishes(dishes)

        return False, "Không tìm thấy món ăn để trừ kho."

    def check_and_expire_dishes(self) -> list[str]:
        today = date.today()
        dishes = self.load_dishes()
        expired_items = []
        changed = False

        for dish in dishes:
            exp_dt = self._parse_date(dish.expiration_date)
            if exp_dt is not None and exp_dt < today and dish.number != 0:
                dish.number = 0
                changed = True
                expired_items.append(f"{dish.name} (HSD: {dish.expiration_date})")

        if changed:
            self.save_dishes(dishes)
        return expired_items