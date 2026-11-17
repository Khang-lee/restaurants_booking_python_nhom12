Dưới đây là toàn bộ nội dung hoàn chỉnh của file **`README.md`** cho dự án **Quản lý Nhà hàng (Nhóm 12)**, đã được tích hợp đầy đủ thông tin chi tiết về cấu trúc, hướng dẫn cài đặt, tài khoản mẫu, các tính năng chính và **Bảng phân công công việc thành viên**:

---

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
| --- | --- | --- | --- |
| **Quản lý** | `quanly` | `123456` | Thêm/Sửa/Xóa bàn, Kéo thả cố định vị trí bàn, Xóa lịch đặt, Xem báo cáo doanh thu & tỷ lệ lấp đầy bàn. |
| **Lễ tân** | `letan` | `123456` | Xem sơ đồ, Đặt bàn, Gọi món, Thanh toán hóa đơn, Tìm kiếm lịch đặt bàn. |

---

## 📋 5. Các Tính Năng Chính

1. **Sơ đồ bàn trực quan:** Canvas kéo thả bố trí bàn theo khu vực, hiển thị màu theo trạng thái (Xám: Trống, Cam: Đặt trước, Xanh: Đang phục vụ).
2. **Quản lý Đặt bàn & DateEntry:** Tích hợp lịch chọn ngày trực quan (`tkcalendar.DateEntry`), kiểm tra chống trùng lịch, tự động tính cọc tối thiểu (50,000 VNĐ/khách), tự động hủy đơn quá 45 phút nếu khách không đến.
3. **Gọi món & Chuyển bàn:** Chọn món ăn nhanh chóng, chuyển bàn linh hoạt giữa các bàn trống, tự động đồng bộ trạng thái bàn giữa `tables.json` và `bookings.json`.
4. **Thanh toán & Báo cáo:** Thanh toán hóa đơn, trừ tiền cọc tự động, giải phóng bàn và lưu trữ lịch sử giao dịch vào `bills.json`.

---

Dưới đây là bảng phân công công việc đã được cập nhật chuẩn xác dành cho **3 thành viên trong nhóm**, chèn sẵn các dòng trống gọn gàng để bạn có thể điền thông tin:

---

Xin lỗi bạn nhé! Để phần báo cáo, đồ án hoặc tài liệu của bạn thật chi tiết, đầy đủ và xứng đáng với khối lượng công việc lớn mà bạn đã đảm nhận, dưới đây là danh sách toàn bộ các hạng mục công nghệ, kiến trúc và tính năng cốt lõi mà **Lê Nguyên Khang** đã thực hiện trong dự án:

---

Dạ đúng rồi ạ! Để phân công công việc trong báo cáo hoặc tài liệu đồ án của nhóm thật chính xác, rõ ràng và đúng với thực tế phân chia, chúng ta có thể điều chỉnh lại **Bảng Phân Công Công Việc** cho 3 thành viên như sau:

---

## 👥 Bảng Phân Công Công Việc Thành Viên (Nhóm 12)

| STT | Họ và Tên | Vai trò / Nhiệm vụ chính | Các phân hệ & Tính năng chi tiết đảm nhận | Tỷ lệ hoàn thành |
| --- | --- | --- | --- | --- |
| **1** | **Lê Nguyên Khang** *(Nhóm trưởng)* | • Thiết kế kiến trúc tổng thể hệ thống (MVC)<br>

<br>• Xây dựng tầng Logic Backend & Quản lý dữ liệu JSON<br>

<br>• Lập trình thuật toán nghiệp vụ & xử lý ngoại lệ<br>

<br>• Quản lý mã nguồn Git & Tài liệu kỹ thuật | • **Sơ đồ bàn trực quan (`Floorplan` Canvas kéo thả):** Xây dựng giao diện và logic kéo thả bàn theo khu vực, cập nhật trạng thái thời gian thực.<br>

<br>• **Phân hệ Đặt bàn (`Booking`):** Lập trình logic kiểm tra trùng lịch (khoảng cách tối thiểu 30 phút), ràng buộc tiền cọc tối thiểu (50.000 VNĐ/khách), tự động hủy đơn quá 45 phút, tích hợp `tkcalendar.DateEntry`.<br>

<br>• **Tính năng Chuyển bàn & Đồng bộ dữ liệu:** Xây dựng cơ chế chuyển bàn mượt mà, đồng bộ trạng thái giữa `tables.json` và `bookings.json`.<br>

<br>• **Hệ thống Đăng nhập & Phân quyền:** Xây dựng `AuthService` và phân tách quyền Quản lý / Lễ tân. | 100% |
| **2** | **[Nhập tên thành viên 2]** | • Thiết kế giao diện người dùng (UI/UX)<br>

<br>• Lập trình màn hình chức năng thanh toán và quản lý hóa đơn | • **Giao diện Hóa đơn & Thanh toán (`Bill`):** Xây dựng màn hình danh sách hóa đơn, giao diện tính tiền, trừ tiền cọc tự động, xuất hóa đơn và lưu trữ lịch sử vào `bills.json`. | 100% |
| **3** | **[Nhập tên thành viên 3]** | • Thiết kế giao diện báo cáo & trực quan hóa dữ liệu<br>

<br>• Xây dựng module thống kê kinh doanh | • **Giao diện Thống kê & Báo cáo:** Xây dựng giao diện thống kê tỷ lệ sử dụng bàn (tỷ lệ lấp đầy), thống kê doanh thu và số lượng lượt thanh toán theo phương thức. | 100% |
