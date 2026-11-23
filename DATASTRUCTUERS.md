```markdown
# TÀI LIỆU CẤU TRÚC DỮ LIỆU (DATA STRUCTURES)

Dự án sử dụng định dạng **JSON** để lưu trữ dữ liệu dạng tập tin (File-based Storage) trong thư mục `data/` và biểu diễn dưới dạng các **Lớp đối tượng (OOP Models)** trong thư mục `models/`, đồng bộ với quản lý thực đơn, tồn kho, hạn sử dụng, đồng bộ API và luồng gọi món — thanh toán.

---

## 📂 1. Cấu Trúc Các File Dữ Liệu JSON (`data/`)

### 1.1. `users.json` (Tài khoản người dùng)

Lưu trữ thông tin tài khoản đăng nhập và phân quyền hệ thống.

```json
[
  {
    "username": "quanly",
    "password": "123",
    "full_name": "Quản Lý Hệ Thống",
    "role": "Quản lý"
  },
  {
    "username": "letan",
    "password": "123",
    "full_name": "Lê Văn Tân",
    "role": "Lễ tân"
  }
]

```

---

### 1.2. `tables.json` (Sơ đồ & Danh sách bàn)

Lưu trữ trạng thái, sức chứa, thời gian bắt đầu phục vụ (`start_time`), danh sách lịch đặt liên quan (`bookings`), danh sách món gọi tạm thời (`orders`), và tọa độ hiển thị trên sơ đồ bàn.

```json
[
  {
    "id": "T01",
    "name": "Bàn 01",
    "area": "TẦNG 1",
    "capacity": 4,
    "status": "Trống",
    "x": 60,
    "y": 60,
    "start_time": null,
    "bookings": [],
    "orders": []
  },
  {
    "id": "TVIP1",
    "name": "Bàn VIP 01",
    "area": "PHÒNG VIP",
    "capacity": 8,
    "status": "Đang phục vụ",
    "x": 100,
    "y": 80,
    "start_time": "2026-11-17 17:00:00",
    "bookings": [],
    "orders": [
      {
        "id": "M02",
        "name": "Lẩu thái hải sản",
        "price": 250000,
        "qty": 1,
        "total": 250000
      }
    ]
  }
]

```

* Giá trị thuộc tính `status`: `"Trống"`, `"Đã đặt"`, `"Đang phục vụ"`.
* Mỗi phần tử trong `orders` gồm: `id` (mã món), `name` (tên món), `price` (đơn giá), `qty` (số lượng gọi), `total` (thành tiền = `price * qty`).

---

### 1.3. `bookings.json` (Danh sách đơn đặt bàn)

Lưu lịch sử và trạng thái các ca đặt bàn của khách hàng, tích hợp ngày tháng định dạng `YYYY-MM-DD` (hỗ trợ chọn qua `DateEntry`), kiểm tra khoảng cách thời gian giữa các lịch đặt trên cùng bàn và ràng buộc tiền cọc tối thiểu (50,000 VNĐ / khách).

```json
[
  {
    "booking_id": "B3A1B",
    "table_id": "Bàn 01",
    "customer_name": "Nguyễn Văn A",
    "customer_phone": "0912345678",
    "booking_date": "2026-11-17",
    "booking_time": "18:00",
    "guest_count": 4,
    "status": "Đã xác nhận",
    "pre_orders": [],
    "deposit_amount": 200000
  }
]

```

* Giá trị thuộc tính `status`: `"Đã xác nhận"`, `"Đã hủy"`, `"Đã hoàn thành"`, `"Đang phục vụ"`.

---

### 1.4. `bills.json` (Lịch sử hóa đơn thanh toán)

Lưu trữ chi tiết giao dịch hóa đơn sau khi hoàn tất thanh toán và giải phóng bàn.

```json
[
  {
    "id": "BILL-3872DF",
    "table_name": "Bàn VIP 01",
    "customer_name": "Khang",
    "total_amount": 250000,
    "payment_method": "Chuyển khoản (QR)",
    "items": [
      {
        "name": "Lẩu thái hải sản",
        "qty": 1,
        "price": 250000,
        "total": 250000
      }
    ],
    "created_at": "2026-11-17 18:30:44",
    "status": "Đã thanh toán"
  }
]

```

---

### 1.5. `menumonan.json` (Thực đơn & Kho món ăn)

Lưu danh mục thực đơn, giá bán, đánh giá, ghi chú, liên kết hình ảnh minh họa (hỗ trợ đường dẫn file cục bộ hoặc URL web), số lượng tồn kho phục vụ (`number`) và hạn sử dụng (`expiration_date`). Khi thanh toán hóa đơn, số lượng `number` của các món đã gọi được trừ tương ứng; khi hết hạn sử dụng hoặc về `0`, món chuyển sang trạng thái hết món (`number = 0`).

```json
[
  {
    "id": "M01",
    "name": "Cơm chiên hải sản",
    "price": 65000,
    "category": "Món ăn",
    "evaluate": "5.0",
    "number": 15,
    "expiration_date": "2026-11-30",
    "note": "",
    "image": ""
  },
  {
    "id": "M02",
    "name": "Lẩu thái hải sản",
    "price": 250000,
    "category": "Lẩu",
    "evaluate": "4.8",
    "number": 0,
    "expiration_date": "2026-11-25",
    "note": "Hết hàng tạm thời",
    "image": ""
  }
]

```

---

### 1.6. Bảng Tóm Tắt Đối Chiếu Các File Dữ Liệu

| File JSON | Thực thể chính | Khóa định danh | File sao lưu / liên quan |
| --- | --- | --- | --- |
| `users.json` | Tài khoản & phân quyền | `username` | `models/user.py` |
| `tables.json` | Bàn & trạng thái phục vụ | `id` / `name` | `models/table.py` |
| `bookings.json` | Lịch đặt bàn & tiền cọc | `booking_id` | `models/booking.py` |
| `bills.json` | Hóa đơn thanh toán | `id` (`BILL-...`) | `models/bill.py` |
| `menumonan.json` | Món ăn, tồn kho & hạn SD | `id` / `name` | `models/monan.py`, `menumonan.json.bak` |

---

## 🧩 2. Mô Hình Lớp Python OOP (`models/`)

### 2.1. Lớp `Table` (`models/table.py`)

* **Thuộc tính:**
* `id` (`str`): Mã định danh bàn.
* `name` (`str`): Tên hiển thị (VD: `"Bàn 01"`).
* `area` (`str`): Khu vực (VD: `"TẦNG 1"`, `"PHÒNG VIP"`).
* `capacity` (`int`): Sức chứa tối đa (số người).
* `status` (`str`): Trạng thái (`"Trống"`, `"Đã đặt"`, `"Đang phục vụ"`).
* `x`, `y` (`int`): Tọa độ hiển thị trên sơ đồ bàn.
* `start_time` (`str | None`): Thời gian bắt đầu phục vụ thực tế tại bàn (`YYYY-MM-DD HH:MM:SS`).
* `bookings` (`list`): Danh sách lượt đặt bàn liên quan.
* `orders` (`list`): Danh sách món ăn đang gọi.


* **Phương thức:**
* `to_dict()`: Chuyển đổi đối tượng thành `dict` để lưu vào `tables.json`.



---

### 2.2. Lớp `Booking` (`models/booking.py`)

* **Thuộc tính:**
* `booking_id` (`str`): Mã đơn đặt bàn tự động tạo (`Bxxxxx`).
* `table_id` (`str`): Tên/Mã bàn đặt.
* `customer_name` (`str`): Tên khách hàng đặt.
* `customer_phone` (`str`): Số điện thoại liên hệ.
* `booking_date` (`str`): Ngày nhận bàn định dạng `YYYY-MM-DD` (hỗ trợ chọn qua `DateEntry`).
* `booking_time` (`str`): Giờ nhận bàn (`HH:MM`).
* `guest_count` (`int`): Số lượng khách tham dự.
* `deposit_amount` (`int | float`): Số tiền cọc thanh toán trước (tối thiểu 50,000 VNĐ/khách).
* `status` (`str`): Trạng thái đơn (`"Đã xác nhận"`, `"Đã hủy"`, `"Đã hoàn thành"`, `"Đang phục vụ"`).
* `pre_orders` (`list`): Danh sách món ăn đặt trước (nếu có).


* **Phương thức:**
* `to_dict()`: Chuyển đối tượng thành `dict` để ghi xuống `bookings.json`.



---

### 2.3. Lớp `Bill` (`models/bill.py`)

* **Thuộc tính:**
* `id` (`str`): Mã hóa đơn (Tự động tạo `BILL-xxxxxx`).
* `table_name` (`str`): Bàn xuất hóa đơn.
* `customer_name` (`str`): Tên khách hàng thanh toán.
* `total_amount` (`int | float`): Tổng số tiền thanh toán thực tế.
* `payment_method` (`str`): Phương thức (`"Tiền mặt"`, `"Chuyển khoản (QR)"`, `"Thẻ ATM/Credit"`).
* `items` (`list`): Danh sách chi tiết món ăn, số lượng và thành tiền.
* `created_at` (`str`): Thời gian xuất hóa đơn (`YYYY-MM-DD HH:MM:SS`).
* `status` (`str`): Trạng thái (`"Đã thanh toán"`).


* **Phương thức:**
* `to_dict()`: Chuyển đổi thành `dict` lưu xuống `bills.json`.



---

### 2.4. Lớp `User` (`models/user.py`)

* **Thuộc tính:**
* `username` (`str`): Tên tài khoản.
* `password` (`str`): Mật khẩu.
* `full_name` (`str`): Họ và tên hiển thị.
* `role` (`str`): Phân quyền người dùng (`"Quản lý"` / `"Lễ tân"`).


* **Phương thức:**
* `to_dict()`: Chuyển đối tượng thành `dict` lưu xuống `users.json`.



---

### 2.5. Lớp `MonAn` (`models/monan.py`) *(Phần bổ sung)*

Biểu diễn thực thể món ăn dùng chung cho quản lý thực đơn, quản lý kho tồn kho và kiểm tra hạn sử dụng.

* **Thuộc tính:**
* `id` (`str`): Mã định danh món ăn (VD: `"M01"`).
* `name` (`str`): Tên món ăn.
* `price` (`int`): Đơn giá bán (VNĐ).
* `category` (`str`): Loại món (VD: `"Món ăn"`, `"Đồ uống"`, `"Lẩu"`, `"Khác"`).
* `evaluate` (`str | float`): Điểm đánh giá món (mặc định `"5.0"`).
* `number` (`int`): Số lượng tồn kho có thể phục vụ (mặc định `0` khi tạo mới; tự động giảm khi thanh toán; về `0` nếu hết hạn sử dụng).
* `expiration_date` (`str`): Hạn sử dụng định dạng `YYYY-MM-DD` (hoặc rỗng/`"-"` nếu chưa thiết lập).
* `note` (`str`): Ghi chú món ăn hoặc nguồn đồng bộ API.
* `image` (`str`): Đường dẫn file ảnh cục bộ hoặc URL hình ảnh món.


* **Phương thức:**
* `to_dict()`: Chuyển đổi đối tượng thành `dict` để lưu xuống `menumonan.json`.
* `from_dict(data)` *(classmethod)*: Khởi tạo đối tượng `MonAn` an toàn từ `dict` đọc trong JSON.



---

## 🔗 3. Mối Quan Hệ & Ràng Buộc Dữ Liệu Xuyên Suốt Hệ Thống

* **Liên kết Bàn — Đặt bàn — Hóa đơn:** `bookings.json` tham chiếu bàn qua `table_id` (khớp `name` hoặc `id` trong `tables.json`); khi xác nhận khách đến, cả đơn đặt và bàn chuyển sang `"Đang phục vụ"`; khi thanh toán, món gọi trong `orders` được ghi vào `bills.json`, xóa khỏi `tables.json` và chuyển đơn đặt `"Đang phục vụ"` sang `"Đã hoàn thành"`.
* **Liên kết Thực đơn — Kho — Order:** `menumonan.json` là nguồn số lượng phục vụ (`number`) và hạn sử dụng (`expiration_date`). Khi thanh toán, `number` giảm theo `qty` đã gọi trên hóa đơn (không âm); khi `number <= 0` hoặc quá hạn sử dụng, món bị coi là hết món và không cho thêm vào hóa đơn cho đến khi kho nhập thêm số lượng mới.
* **Ràng buộc đặt bàn:** Ngày đặt (`booking_date`) chuẩn hóa `YYYY-MM-DD` từ `DateEntry`, kiểm tra tránh trùng/quá sát khung giờ với các lịch chưa hủy/chưa hoàn thành trên cùng bàn, và yêu cầu `deposit_amount >= 50000 * guest_count`.