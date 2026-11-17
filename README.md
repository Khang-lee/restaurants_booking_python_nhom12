# HỆ THỐNG QUẢN LÝ ĐẶT BÀN NHÀ HÀNG (NHÓM 12)

Ứng dụng quản lý đặt bàn, sơ đồ mặt bằng, thực đơn và lịch sử hóa đơn cho nhà hàng, được xây dựng bằng Python Tkinter theo mô hình kiến trúc đa tầng (MVC/Modular UI).

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
├── data/                          # Thư mục lưu trữ dữ liệu JSON
│   ├── users.json                 # Danh sách tài khoản & phân quyền
│   ├── tables.json                # Danh sách bàn & vị trí sơ đồ
│   ├── bookings.json              # Danh sách lịch đặt bàn
│   ├── bills.json                 # Lịch sử hóa đơn thanh toán
│   └── menumonan.json             # Danh mục thực đơn & món ăn
│
├── models/                        # Các lớp dữ liệu OOP (Data Models)
│   ├── user.py                    # Lớp User (Người dùng)
│   ├── table.py                   # Lớp Table (Bàn ăn)
│   ├── booking.py                 # Lớp Booking (Đơn đặt bàn)
│   └── bill.py                    # Lớp Bill (Hóa đơn)
│
├── services/                      # Các dịch vụ xử lý logic & đọc/ghi dữ liệu
│   ├── auth_service.py            # Dịch vụ xác thực đăng nhập
│   ├── booking_service.py         # Dịch vụ nghiệp vụ đặt bàn
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
        ├── order_menu_view.py     # Hộp thoại Đặt bàn / Nhận món / Thanh toán
        └── table_actions.py       # Menu thao tác bàn (Hủy, Chuyển, Gộp)
```

---

## 🛠️ 2. Yêu Cầu Môi Trường & Cài Đặt

### Môi trường khuyến nghị:
- **Python 3.8+** (Khuyên dùng Python 3.10 trở lên)
- Hệ điều hành: Windows / macOS / Linux

### Các thư viện phụ thuộc (Dependencies):
Mở **Terminal / Command Prompt (CMD)** và chạy lệnh cài đặt:

```bash
pip install pillow tkcalendar
```

---

## 🚀 3. Các Bước Thực Hiện Để Chạy Chương Trình

### Cách 1: Chạy trực tiếp từ CMD / Terminal
1. Mở cửa sổ **Command Prompt (CMD)**.
2. Di chuyển vào thư mục chứa dự án:
   ```cmd
   cd C:\Đường_Dẫn_Đến\DoAnPython_nhom12\DoAnPython_nhom12
   ```
3. Chạy lệnh thực thi file chính:
   ```cmd
   python DoAnPython_nhom12.py
   ```
   *(Hoặc `py DoAnPython_nhom12.py` nếu sử dụng Launcher)*

### Cách 2: Chạy trong VS Code / PyCharm / Visual Studio
1. Mở thư mục `DoAnPython_nhom12` bằng IDE.
2. Chọn môi trường Python Interpreter (đã cài `pillow` và `tkcalendar`).
3. Nhấn `Run` hoặc ấn phím `F5` tại file `DoAnPython_nhom12.py`.

---

## 🔐 4. Thông Tin Tài Khoản Đăng Nhập Mẫu

Hệ thống hỗ trợ phân quyền người dùng giữa **Quản lý** và **Lễ tân**:

| Vai trò (Role) | Tên đăng nhập (Username) | Mật khẩu (Password) | Quyền hạn nổi bật |
| :--- | :--- | :--- | :--- |
| **Quản lý** | `quanly` | `123456` | Thêm/Sửa/Xóa bàn, Kéo thả cố định vị trí bàn, Xóa lịch đặt, Xem báo cáo doanh thu & tỷ lệ lấp đầy bàn. |
| **Lễ tân** | `letan` | `123456` | Xem sơ đồ, Đặt bàn, Gọi món, Thanh toán hóa đơn, Tìm kiếm lịch đặt bàn. |

---

## 📋 5. Các Tính Năng Chính
1. **Sơ đồ bàn trực quan:** Canvas kéo thả bố trí bàn theo khu vực, hiển thị màu theo trạng thái (Xám: Trống, Cam: Đã đặt, Xanh: Đang phục vụ).
2. **Quản lý Đặt bàn:** Kiểm tra chống trùng lịch (< 2 tiếng), tự động tính cọc (120,000 VNĐ/khách), tìm kiếm theo SĐT hoặc Ngày.
3. **Gọi món & Xuất Bill:** Chọn món ăn có tải ảnh từ URL, tính tiền trừ cọc tự động, ghi nhận lịch sử vào `bills.json`.
4. **Nhắc lịch & Báo cáo:** Tự động thông báo khách sắp đến trong 30 phút, thống kê doanh thu, số lượt thanh toán theo hình thức và tỷ lệ lấp đầy bàn.

## 👥 6. Bảng Phân Công Công Việc Thành ViênSTTHọ và TênVai trò / Nhiệm vụ chínhCác phân hệ đảm nhậnTỷ lệ hoàn thành1Nguyễn Ngọc Lan Tường (Nhóm trưởng)• Thiết kế kiến trúc hệ thống (MVC)• Xây dựng Logic Backend & Xử lý tệp JSON• Tích hợp cơ chế bảo mật và phân quyền• Quản lý Đặt bàn (Booking)• Chuyển bàn trực tiếp & Đồng bộ JSON• Hệ thống Đăng nhập (Auth)100%2Thành viên 2 (Thay tên)• Thiết kế giao diện người dùng (UI/UX)• Lập trình các màn hình danh sách & bảng dữ liệu• Kiểm thử và xử lý ngoại lệ giao diện• Sơ đồ bàn trực quan (Floorplan)• Gọi món & Quản lý thực đơn (Order)• Quản lý Hóa đơn & Thanh toán (Bill)100%
