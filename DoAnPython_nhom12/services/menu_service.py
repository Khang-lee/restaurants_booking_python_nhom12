import json
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


class ExternalMenuService:
    """
    Lấy dữ liệu món ăn đa dạng loại từ TheMealDB (https://www.themealdb.com),
    làm sạch - chuẩn hóa loại món và lưu vào external_menu.json (+ .bak dự phòng).
    """

    BASE_API_URL = "https://www.themealdb.com/api/json/v1/1"
    FILTER_URL = f"{BASE_API_URL}/filter.php?c={{category}}"
    SEARCH_LETTER_URL = f"{BASE_API_URL}/search.php?f={{letter}}"

    CATEGORY_SOURCES = [
        ("Beef", "Món chính"),
        ("Chicken", "Món chính"),
        ("Seafood", "Món chính"),
        ("Pasta", "Món chính"),
        ("Pork", "Món chính"),
        ("Miscellaneous", "Lẩu"),
        ("Vegetarian", "Khai vị"),
        ("Starter", "Khai vị"),
        ("Side", "Khai vị"),
        ("Dessert", "Tráng miệng"),
    ]
    EXTRA_LETTERS = ["c", "s", "p", "b", "t", "m", "v"]

    CATEGORY_MAP = {
        "beef": "Món chính",
        "chicken": "Món chính",
        "seafood": "Món chính",
        "pasta": "Món chính",
        "pork": "Món chính",
        "lamb": "Món chính",
        "goat": "Món chính",
        "breakfast": "Món ăn",
        "miscellaneous": "Lẩu",
        "soup": "Lẩu",
        "stew": "Lẩu",
        "vegetarian": "Khai vị",
        "vegan": "Khai vị",
        "starter": "Khai vị",
        "side": "Khai vị",
        "dessert": "Tráng miệng",
        "drink": "Đồ uống",
        "beverage": "Đồ uống",
    }

    def __init__(self, data_dir: str | None = None, api_url: str | None = None):
        if data_dir:
            self.data_dir = data_dir
        else:
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(project_dir, "data")

        self.api_url = (api_url or self.FILTER_URL).strip()
        self.output_file = os.path.join(self.data_dir, "external_menu.json")
        self.backup_file = f"{self.output_file}.bak"

    @staticmethod
    def _clean_text(value: object) -> str:
        return " ".join(str(value or "").strip().split())

    def _map_category(self, raw_category: object, mapped_cat: str, name: str, idx: int) -> str:
        raw_low = self._clean_text(raw_category).lower()
        name_low = self._clean_text(name).lower()

        if any(k in raw_low or k in name_low for k in ("drink", "tea", "coffee", "juice", "soda", "milk")):
            return "Đồ uống"
        if any(k in raw_low or k in name_low for k in ("soup", "stew", "hotpot", "broth")):
            return "Lẩu"
        if any(k in raw_low or k in name_low for k in ("dessert", "cake", "pie", "pudding", "sweet", "ice cream")):
            return "Tráng miệng"
        if any(k in raw_low or k in name_low for k in ("salad", "starter", "side", "vegetarian", "vegan")):
            return "Khai vị"
        if raw_low in self.CATEGORY_MAP:
            return self.CATEGORY_MAP[raw_low]
        if mapped_cat:
            return mapped_cat

        fallback = ["Món chính", "Lẩu", "Khai vị", "Tráng miệng", "Đồ uống", "Món ăn"]
        return fallback[(idx - 1) % len(fallback)]

    def _fetch_meals(self, endpoint: str, timeout: int) -> list[dict]:
        req = urllib.request.Request(
            endpoint,
            headers={
                "User-Agent": "Mozilla/5.0 (RestaurantApp-Nhom12)",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw_text = resp.read().decode("utf-8", errors="replace")

        data = json.loads(raw_text)
        meals = data.get("meals") if isinstance(data, dict) else None
        return [m for m in meals if isinstance(m, dict)] if isinstance(meals, list) else []

    def _build_endpoints(self, target_url: str) -> list[tuple[str, str]]:
        if "{category}" in target_url:
            return [
                (app_cat, target_url.format(category=urllib.parse.quote(api_cat)))
                for api_cat, app_cat in self.CATEGORY_SOURCES
            ]
        if "{letter}" in target_url:
            return [
                ("", target_url.format(letter=ch))
                for ch in self.EXTRA_LETTERS
            ]
        if "themealdb.com" in target_url:
            endpoints = [("", target_url)]
            for api_cat, app_cat in self.CATEGORY_SOURCES:
                endpoints.append((app_cat, self.FILTER_URL.format(category=urllib.parse.quote(api_cat))))
            return endpoints
        return [("", target_url)]

    def fetch_and_save_menu(
        self,
        url: str | None = None,
        timeout: int = 10,
        limit: int = 12,
        default_price: int = 75000,
    ) -> dict:
        target_url = (url or self.api_url).strip()
        if not target_url.startswith(("http://", "https://")):
            return {
                "ok": False,
                "message": "URL API không hợp lệ.",
                "items": [],
                "file_path": self.output_file,
            }

        max_limit = max(1, int(limit or 12))
        safe_price = max(10000, int(default_price or 75000))
        endpoints = self._build_endpoints(target_url)

        # Lấy xen kẽ theo vòng tròn từ từng nguồn để đảm bảo có đủ nhiều loại món
        per_endpoint_batches = []
        last_error = None
        for app_cat, ep_url in endpoints:
            try:
                meals = self._fetch_meals(ep_url, timeout=timeout)
                if meals:
                    per_endpoint_batches.append((app_cat, meals))
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = f"Lỗi gọi API ({ep_url}): {exc}"

        if not per_endpoint_batches:
            return {
                "ok": False,
                "message": last_error or "Không lấy được dữ liệu món ăn từ TheMealDB.",
                "items": [],
                "file_path": self.output_file,
            }

        items = []
        seen_names = set()
        seen_ids = set()
        max_batch_len = max(len(m) for _, m in per_endpoint_batches)

        for row_idx in range(max_batch_len):
            for app_cat, meals in per_endpoint_batches:
                if len(items) >= max_limit:
                    break
                if row_idx >= len(meals):
                    continue

                meal = meals[row_idx]
                name = self._clean_text(meal.get("strMeal"))
                if not name or name.lower() in seen_names:
                    continue
                seen_names.add(name.lower())

                idx = len(items) + 1
                raw_id = self._clean_text(meal.get("idMeal")) or str(idx)
                dish_id = f"API-{raw_id}"
                while dish_id in seen_ids:
                    dish_id = f"API-{raw_id}-{idx}"
                seen_ids.add(dish_id)

                category = self._map_category(meal.get("strCategory"), app_cat, name, idx)
                image = self._clean_text(meal.get("strMealThumb"))

                items.append(
                    {
                        "id": dish_id,
                        "name": name,
                        "price": safe_price + (idx - 1) * 5000,
                        "category": category,
                        "note": f"TheMealDB ({category})",
                        "evaluate": "4.5",
                        "number": 0,
                        "expiration_date": "",
                        "image": image,
                    }
                )
            if len(items) >= max_limit:
                break

        try:
            os.makedirs(self.data_dir, exist_ok=True)
            if os.path.exists(self.output_file):
                shutil.copy2(self.output_file, self.backup_file)

            document = {
                "source": "TheMealDB",
                "api_url": target_url,
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(items),
                "items": items,
            }
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False, indent=2)

            return {
                "ok": True,
                "message": f"Đã lấy {len(items)} món đa dạng loại từ TheMealDB vào '{os.path.basename(self.output_file)}'.",
                "items": items,
                "file_path": self.output_file,
            }
        except OSError as exc:
            return {
                "ok": False,
                "message": f"Lỗi lưu file JSON: {exc}",
                "items": [],
                "file_path": self.output_file,
            }

    def load_saved_menu(self) -> list[dict]:
        for path in (self.output_file, self.backup_file):
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and isinstance(data.get("items"), list):
                    return [item for item in data["items"] if isinstance(item, dict)]
            except (json.JSONDecodeError, OSError):
                continue
        return []