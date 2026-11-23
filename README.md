# HỆ THỐNG QUẢN LÝ ĐẶT BÀN NHÀ HÀNG (NHÓM 12)

Ứng dụng quản lý đặt bàn, sơ đồ mặt bằng, thực đơn — kho món ăn và lịch sử hóa đơn cho nhà hàng, được xây dựng bằng Python Tkinter theo mô hình kiến trúc đa tầng (MVC / Modular UI).

---

## 📌 1. Cấu Trúc Thư Mục Dự Án

```text
DoAnPython_nhom12/
│
├── DoAnPython_nhom12.py          # File khởi chạy ứng dụng chính (Main Entry)
├── floorplan_data.json            # File cấu hình sơ đồ bàn dự phòng
├── README.md                      # Hướng dẫn sử dụng & cài đặt
├── DATA_STRUCTURES.md             # Tài liệu mô tả cấu trúc dữ liệu
│
├── assets/                        # Chứa tài nguyên hình ảnh, biểu tượng (icon)
│   └── TTB(1).ico
│
├── controllers/                   # Điều phối nghiệp vụ giao diện
│   ├── order_controller.py        # Điều phối gọi món, tồn kho, chuyển bàn, thanh toán
│   └── menu_mon_controller.py     # Điều phối Menu món ăn, Kho món ăn & đồng bộ API
│
├── data/                          # Thư mục lưu trữ dữ liệu JSON
│   ├── users.json                 # Danh sách tài khoản & phân quyền
│   ├── tables.json                # Danh sách bàn & vị trí sơ đồ
│   ├── bookings.json              # Danh sách lịch đặt bàn
│   ├── bills.json                 # Lịch sử hóa đơn thanh toán
│   ├── menumonan.json             # Danh mục thực đơn, tồn kho & hạn sử dụng
│   └── menumonan.json.bak         # File sao lưu khi cập nhật tồn kho
│
├── models/                        # Các lớp dữ liệu OOP (Data Models)
│   ├── user.py                    # Lớp User (Người dùng)
│   ├── table.py                   # Lớp Table (Bàn ăn)
│   ├── booking.py                 # Lớp Booking (Đơn đặt bàn)
│   ├── bill.py                    # Lớp Bill (Hóa đơn)
│   └── monan.py                   # Lớp MonAn (Món ăn, tồn kho & hạn sử dụng)
│
├── services/                      # Các dịch vụ xử lý logic & đọc/ghi dữ liệu
│   ├── auth_service.py            # Dịch vụ xác thực đăng nhập
│   ├── booking_service.py         # Dịch vụ nghiệp vụ đặt bàn
│   ├── order_service.py           # Dịch vụ tải/xử lý dữ liệu gọi món
│   ├── monan_service.py           # Dịch vụ quản lý món ăn, tồn kho & hạn sử dụng
│   ├── menu_service.py            # Dịch vụ đồng bộ thực đơn từ API ngoài
│   └── data_manager.py            # Dịch vụ quản lý đọc/ghi JSON
│
└── ui/                            # Giao diện người dùng (User Interface)
    ├── dialogs/                   # Hộp thoại pop-up
    │   ├── login_dialog.py        # Hộp thoại đăng nhập
    │   └── transfer_table_dialog.py # Hộp thoại chuyển/gộp bàn
    │
    └── views/                     # Các màn hình view chính
        ├── main_view.py           # Khung giao diện chính (Sidebar + Container)
        ├── floorplan_view.py      # Màn hình Sơ đồ bàn (Canvas Drag & Drop)
        ├── booking_list_view.py   # Màn hình Danh sách đặt bàn & Tìm kiếm
        ├── billlistview.py        # Màn hình Quản lý hóa đơn & Báo cáo
        ├── order_menu_view.py     # Màn hình Gọi món / Nhận món / Thanh toán
        ├── menu_mon_view.py       # Màn hình Menu món ăn & Kho món ăn
        └── table_actions.py       # Menu thao tác bàn (Hủy, Chuyển, Gộp)

```

---

## 🛠️ 2. Yêu Cầu Môi Trường & Cài Đặt

### Môi trường khuyến nghị:

* **Python 3.8+** (Khuyên dùng Python 3.10 trở lên)
* Hệ điều hành: Windows / macOS / Linux

### Các thư viện phụ thuộc (Dependencies):

Mở **Terminal / Command Prompt (CMD)** và chạy lệnh cài đặt:

```bash
pip install pillow tkcalendar

```

---

## 🚀 3. Các Bước Thực Hiện Để Chạy Chương Trình

### Cách 1: Chạy trực tiếp từ CMD / Terminal

1. Mở cửa sổ **Command Prompt (CMD)**.
2. Di chuyển vào thư mục chứa dự án: `cd C:\Đường_Dẫn_Đến\DoAnPython_nhom12\DoAnPython_nhom12`
3. Chạy lệnh thực thi file chính: `python DoAnPython_nhom12.py` *(Hoặc `py DoAnPython_nhom12.py` nếu sử dụng Launcher)*

### Cách 2: Chạy trong VS Code / PyCharm / Visual Studio

1. Mở thư mục `DoAnPython_nhom12` bằng IDE.
2. Chọn môi trường Python Interpreter (đã cài `pillow` và `tkcalendar`).
3. Nhấn `Run` hoặc ấn phím `F5` tại file `DoAnPython_nhom12.py`.

---

## 🔐 4. Thông Tin Tài Khoản Đăng Nhập Mẫu

Hệ thống hỗ trợ phân quyền người dùng giữa **Quản lý** và **Lễ tân**:

* **Quản lý** (`quanly` / `123456`): Thêm/Sửa/Xóa bàn, Kéo thả cố định vị trí bàn, Xóa lịch đặt, Xem báo cáo doanh thu & tỷ lệ lấp đầy bàn.
* **Lễ tân** (`letan` / `123456`): Xem sơ đồ, Đặt bàn, Gọi món, Thanh toán hóa đơn, Tìm kiếm lịch đặt bàn.

---

## 📁 5. Mô Tả Cấu Trúc Dữ Liệu & Ràng Buộc Hệ Thống (`data/`)

### 5.1. Cấu trúc tệp `tables.json` (Quản lý Bàn ăn & Sơ đồ)

Mỗi bản ghi đại diện cho một bàn vật lý trong nhà hàng, lưu tọa độ hiển thị và danh sách món ăn đang gọi tạm tính:

```json
{
  "id": "T-A1B2C3",
  "name": "Bàn 01",
  "Khu vực": "Sảnh Chính",
  "capacity": 4,
  "status": "Trống",
  "x": 60,
  "y": 80,
  "orders": [
    {
      "id": "M01",
      "name": "Lẩu Thái Hải Sản",
      "price": 250000,
      "qty": 1,
      "total": 250000
    }
  ],
  "start_time": "2026-11-17 12:30:00"
}

```

* **Các trạng thái bàn (`status`)**:
* `"Trống"` (Màu xám): Bàn chưa có khách và không có lịch đặt active.
* `"Đã đặt"` (Màu cam): Bàn có lịch đặt trước trong ngày.
* `"Đang phục vụ"` (Màu xanh): Bàn đang có khách ngồi ăn hoặc gọi món.



### 5.2. Cấu trúc tệp `bookings.json` (Quản lý Đơn Đặt Bàn)

Lưu trữ thông tin khách hàng đặt trước để hệ thống tiến hành kiểm tra trùng lịch và nhắc nhở thời gian thực:

```json
{
  "booking_id": "B7F8A1",
  "table_id": "Bàn 01",
  "customer_name": "Nguyễn Văn A",
  "customer_phone": "0909123456",
  "booking_date": "2026-11-17",
  "booking_time": "18:30",
  "guest_count": 4,
  "status": "Đã xác nhận",
  "deposit_amount": 200000,
  "pre_orders": []
}

```

* **Trạng thái đơn (`status`)**: `"Đã xác nhận"`, `"Đang phục vụ"`, `"Đã hoàn thành"`, `"Đã hủy"`.

### 5.3. Cấu trúc tệp `menumonan.json` (Quản lý Thực Đơn, Kho & Hạn Sử Dụng)

Lưu danh sách món ăn, giá bán, số lượng tồn kho phục vụ (`number`), hạn sử dụng (`expiration_date`) và hình ảnh (file cục bộ hoặc URL web):

```json
{
  "id": "M01",
  "name": "Lẩu Thái Hải Sản",
  "price": 250000,
  "category": "Lẩu",
  "evaluate": "5.0",
  "number": 10,
  "expiration_date": "2026-11-30",
  "note": "",
  "image": ""
}

```

---

## ⚙️ 6. Các Quy Tắc Ràng Buộc Nghiệp Vụ, Kỹ Thuật & Trạng Thái Hoàn Thiện

### 6.1. Quy tắc Đặt bàn & Chống trùng lặp thời gian (`BookingController`)

* **[Đã làm] Khoảng cách ca bàn (Buffer Time)**: Mỗi ca bàn tiêu chuẩn kéo dài **2 tiếng (120 phút)**, bắt buộc cách nhau tối thiểu **30 phút** trên cùng một bàn trong ngày; các lịch `"Đã hoàn thành"` hoặc `"Đã hủy"` được bỏ qua khi kiểm tra.
* **[Đã làm] Quy định Tiền cọc tối thiểu**: Tính tự động theo công thức $\text{Tiền cọc tối thiểu} = \text{Số lượng khách (guest\_count)} \times 50,000 \text{ VNĐ}$ và kiểm tra chặn lưu nếu thấp hơn mức tối thiểu.
* **[Đã làm] Cơ chế tự động hủy đơn (`Auto-Cancellation`)**: Quét các đơn `"Đã xác nhận"` quá giờ hẹn trên **45 phút** mà khách chưa đến để tự động chuyển sang `"Đã hủy"`.

### 6.2. Quy tắc Đồng bộ Trạng thái Bàn, Gọi Món & Kho (`OrderController`, `OrderMenuView`, `MenuMonView`, `MenuMonController`)

* **[Đã làm] Chuyển trạng thái khi mở bàn**: Khi mở bàn đang `"Trống"` hoặc `"Đã đặt"` để gọi món, trạng thái tự động chuyển sang `"Đang phục vụ"` và ghi nhận `start_time` nếu chưa có.
* **[Đã làm] Lưu tạm & giải phóng bàn**: Thao tác gọi món, tăng/giảm/xóa món cập nhật trên `current_order`, đồng bộ lên `tables.json` khi thoát hoặc thanh toán (`checkout`); khi không còn món và không còn lịch đặt active thì bàn trả về `"Trống"`.
* **[Đã làm] Hiển thị đầy đủ tên món & số lượng phục vụ trên Order**: Trên thẻ món hiển thị tên món đầy đủ cùng số lượng còn lại (`SL: ...` / `Còn ...`) hoặc `[HẾT MÓN]`; khi hết món sẽ đổi giao diện mờ/xám, vô hiệu hóa nút `+` và không cho nhấn thêm món.
* **[Đã làm] Trừ tồn kho khi thanh toán & cập nhật lại khi kho nhập thêm**: Khi thanh toán (`checkout`), hệ thống tự động trừ `qty` của các món đã gọi trong `menumonan.json` (tạo file `.bak` dự phòng); khi kho (`MenuMonView`) nhập/cộng thêm số lượng mới, số lượng phục vụ được cập nhật lại trên hệ thống.
* **[Đã làm] Cảnh báo & chọn nhanh món hết số lượng tại Kho**: Tại tab **Kho món ăn**, hệ thống hiển thị thông báo các món hết số lượng (`SL <= 0`), tô nổi bật dòng hết hàng và cung cấp nút chọn nhanh `+ <Tên món>` để nhập thêm số lượng.
* **[Đã làm] Tách Controller & UI**: Đã tách logic nghiệp vụ cho khu vực Order (`OrderController`) và khu vực Menu/Kho (`MenuMonController`) tách biệt với giao diện Tkinter (`OrderMenuView`, `MenuMonView`).