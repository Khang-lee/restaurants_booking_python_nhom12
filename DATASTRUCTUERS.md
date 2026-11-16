# TÀI LIỆU CẤU TRÚC DỮ LIỆU (DATA STRUCTURES)

Dự án sử dụng định dạng **JSON** để lưu trữ dữ liệu dạng tập tin (File-based Storage) và biểu diễn dưới dạng các **Lớp đối tượng (OOP Models)** trong Python.

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

### 1.2. `tables.json` (Sơ đồ & Danh sách bàn)
Lưu trữ trạng thái, sức chứa, tọa độ hiển thị trên Canvas sơ đồ bàn.

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
    "bookings": [],
    "orders": []
  },
  {
    "id": "TVIP1",
    "name": "Bàn VIP 01",
    "area": "PHÒNG VIP",
    "capacity": 8,
    "status": "Đã đặt",
    "x": 100,
    "y": 80,
    "bookings": [
      {
        "customer": "Khang",
        "phone": "0987654321",
        "guests": 4,
        "deposit": 480000,
        "time": "2026-08-26 18:00"
      }
    ],
    "orders": []
  }
]
```

### 1.3. `bookings.json` (Danh sách đơn đặt bàn)
Lưu lịch sử và trạng thái các ca đặt bàn của khách hàng.

```json
[
  {
    "booking_id": "B3A1B",
    "table_id": "Bàn 01",
    "customer_name": "Nguyễn Văn A",
    "customer_phone": "0912345678",
    "booking_date": "2026-08-26",
    "booking_time": "18:00",
    "guest_count": 4,
    "status": "Đã xác nhận",
    "pre_orders": [],
    "deposit_amount": 480000
  }
]
```

*Giá trị thuộc tính `status`: `"Đã xác nhận"`, `"Đã hủy"`, `"Hoàn thành"`.

### 1.4. `bills.json` (Lịch sử hóa đơn thanh toán)
Lưu trữ chi tiết giao dịch hóa đơn sau khi hoàn tất thanh toán.

```json
[
  {
    "id": "BILL-3872DF",
    "table_name": "Bàn VIP 01",
    "customer_name": "Khang",
    "total_amount": 650000,
    "payment_method": "Chuyển khoản (QR)",
    "items": [
      {
        "name": "Lẩu thái hải sản",
        "qty": 1,
        "price": 250000,
        "total": 250000
      },
      {
        "name": "Cơm chiên hải sản",
        "qty": 2,
        "price": 65000,
        "total": 130000
      }
    ],
    "created_at": "2026-08-26 13:00:44",
    "status": "Đã thanh toán"
  }
]
```

### 1.5. `menumonan.json` (Thực đơn món ăn)
Lưu danh mục thực đơn, giá tiền và liên kết hình ảnh minh họa.

```json
[
  {
    "id": "M01",
    "name": "Cơm chiên hải sản",
    "price": 65000,
    "category": "Món chính",
    "image": "https://example.com/images/com_chien.jpg"
  },
  {
    "id": "M02",
    "name": "Lẩu thái hải sản",
    "price": 250000,
    "category": "Lẩu",
    "image": "https://example.com/images/lau_thai.jpg"
  }
]
```

---

## 🧩 2. Mô Hình Lớp Python OOP (`models/`)

### 2.1. Lớp `Table` (`models/table.py`)
- **Thuộc tính:**
  - `id` (str): Mã định danh bàn.
  - `name` (str): Tên hiển thị (VD: "Bàn 01").
  - `area` (str): Khu vực (VD: "TẦNG 1", "PHÒNG VIP").
  - `capacity` (int): Sức chứa tối đa (số người).
  - `status` (str): Trạng thái (`"Trống"`, `"Đã đặt"`, `"Đang phục vụ"`).
  - `x`, `y` (int): Tọa độ hiển thị trên sơ đồ Canvas.
  - `bookings` (list): Danh sách lượt đặt bàn liên quan.
  - `orders` (list): Danh sách món ăn đang gọi.
- **Phương thức:**
  - `to_dict()`: Chuyển đổi đối tượng thành Dictionary để lưu vào JSON.

### 2.2. Lớp `Booking` (`models/booking.py`)
- **Thuộc tính:**
  - `booking_id` (str): Mã đơn đặt bàn.
  - `table_id` (str): Tên/Mã bàn đặt.
  - `customer_name` (str): Tên khách hàng đặt.
  - `customer_phone` (str): Số điện thoại liên hệ.
  - `booking_date` (str): Ngày nhận bàn (`YYYY-MM-DD`).
  - `booking_time` (str): Giờ nhận bàn (`HH:MM`).
  - `guest_count` (int): Số lượng khách tham dự.
  - `deposit_amount` (int): Số tiền cọc thanh toán trước.
  - `status` (str): Trạng thái đơn (`"Đã xác nhận"`, `"Đã hủy"`, `"Hoàn thành"`).
- **Phương thức:**
  - `to_dict()`: Chuyển đối tượng thành Dictionary để ghi xuống `bookings.json`.

### 2.3. Lớp `Bill` (`models/bill.py`)
- **Thuộc tính:**
  - `id` (str): Mã hóa đơn (Tự động tạo `BILL-xxxxxx`).
  - `table_name` (str): Bàn xuất hóa đơn.
  - `customer_name` (str): Tên khách hàng thanh toán.
  - `total_amount` (int): Tổng số tiền thanh toán thực tế (sau khi trừ cọc).
  - `payment_method` (str): Phương thức (`"Tiền mặt"`, `"Chuyển khoản (QR)"`, `"Thẻ ATM/Credit"`).
  - `items` (list): Danh sách chi tiết món ăn và số lượng.
  - `created_at` (str): Thời gian xuất hóa đơn.
  - `status` (str): Trạng thái (`"Đã thanh toán"`).
- **Phương thức:**
  - `to_dict()`: Chuyển đổi thành Dictionary lưu xuống `bills.json`.

### 2.4. Lớp `User` (`models/user.py`)
- **Thuộc tính:**
  - `username` (str): Tên tài khoản.
  - `password` (str): Mật khẩu.
  - `full_name` (str): Họ và tên hiển thị.
  - `role` (str): Phân quyền người dùng (`"Quản lý"` / `"Lễ tân"`).
- **Phương thức:**
  - `to_dict()`: Chuyển đối tượng thành Dictionary lưu xuống `users.json`.