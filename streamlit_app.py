import streamlit as st
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="Ứng Dụng Lịch Khám Sức Khỏe", page_icon="🩺")
st.markdown("<style>.stButton button { width: 100%; }</style>", unsafe_allow_html=True)

# Khởi tạo trang mặc định là home nếu chưa có trong session
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Dữ liệu mẫu cho lịch sử khám (dùng để test)
# Trong thực tế, dữ liệu này sẽ được lấy từ backend hoặc cơ sở dữ liệu
sample_appointments = [
    {"date": "2024-10-20", "time": "14:00", "doctor": "Dr. Nguyễn Văn A", "location": "Phòng khám ABC", "service": "Khám tổng quát", "price": "500.000 VND"},
    {"date": "2024-09-15", "time": "09:00", "doctor": "Dr. Trần Thị B", "location": "Bệnh viện XYZ", "service": "Xét nghiệm máu", "price": "300.000 VND"}
]

# Hàm để điều hướng trang
def navigate(page):
    st.session_state.page = page

# Hàm cho trang Đăng Ký
def register_page():
    st.title("Đăng Ký")
    with st.form("register_form"):
        email = st.text_input("Email")
        phone = st.text_input("Số điện thoại")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("Đăng Ký"):
            st.success("Đăng ký thành công! Vui lòng đăng nhập.")
            navigate("login")

# Hàm cho trang Đăng Nhập
def login_page():
    st.title("Đăng Nhập")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("Đăng Nhập"):
            st.success("Đăng nhập thành công!")
            navigate("home")

# Hàm cho trang Trang Chủ
def home_page():
    st.title("Danh Sách Các Dịch Vụ Khám Sức Khỏe")

    # Danh sách các dịch vụ khám (ví dụ)
    services = [
        {"name": "Khám tổng quát", "description": "Khám sức khoẻ tổng quát để đánh giá tình trạng sức khỏe hiện tại."},
        {"name": "Khám chuyên khoa", "description": "Khám và tư vấn từ các chuyên gia về nội khoa, ngoại khoa, tim mạch, v.v."},
        {"name": "Xét nghiệm máu", "description": "Xét nghiệm máu để kiểm tra các chỉ số quan trọng của cơ thể."},
        {"name": "Khám sức khỏe định kỳ", "description": "Khám định kỳ giúp theo dõi và phát hiện sớm các bệnh lý."},
        {"name": "Khám tầm soát ung thư", "description": "Các xét nghiệm tầm soát sớm các loại ung thư phổ biến."}
    ]

    # Hiển thị danh sách dịch vụ dưới dạng thẻ
    num_columns = 2  # Số thẻ mỗi hàng
    cols = st.columns(num_columns)

    for index, service in enumerate(services):
        with cols[index % num_columns]:  # Chia đều các thẻ vào các cột
            st.markdown("### " + service["name"])  # Tên dịch vụ
            st.write(service["description"])        # Mô tả dịch vụ
            if st.button("Đặt lịch", key=f"book_{index}", on_click=lambda: navigate("book_appointment")):
                navigate("book_appointment")

            st.write("---")  # Dòng phân cách giữa các thẻ



# Hàm cho trang Cập Nhật Thông Tin Hồ Sơ
def update_profile_page():
    st.title("Cập Nhật Thông Tin Hồ Sơ")
    with st.form("profile_form"):
        name = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")
        email = st.text_input("Email")
        age = st.number_input("Tuổi", min_value=0)
        gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
        blood_type = st.selectbox("Nhóm máu", ["A", "B", "AB", "O"])
        blood_pressure = st.text_input("Huyết áp")
        height = st.number_input("Chiều cao (cm)", min_value=0)
        weight = st.number_input("Cân nặng (kg)", min_value=0)
        glucose = st.text_input("Đường huyết")

        if st.form_submit_button("Cập Nhật Thông Tin"):
            st.success("Cập nhật thông tin hồ sơ thành công!")
            navigate("home")

# Hàm cho trang Đặt Lịch Khám
API_BASE_URL = "https://provinces.open-api.vn/api/"

def get_provinces():
    response = requests.get(API_BASE_URL + "p/")
    if response.status_code == 200:
        return response.json()
    return []

def get_districts(province_id):
    response = requests.get(f"{API_BASE_URL}p/{province_id}?depth=2")
    if response.status_code == 200:
        return response.json().get("districts", [])
    return []

def get_wards(district_id):
    response = requests.get(f"{API_BASE_URL}d/{district_id}?depth=2")
    if response.status_code == 200:
        return response.json().get("wards", [])
    return []

def generate_time_slots(start, end, interval_minutes=30):
    """Tạo danh sách khung giờ từ 'start' đến 'end' với khoảng cách mỗi lần là interval_minutes phút."""
    times = []
    current = start
    while current <= end:
        times.append(current.strftime("%H:%M"))
        current += timedelta(minutes=interval_minutes)
    return times

def book_appointment_page():
    st.title("Đặt Lịch Khám")
    
    # Khởi tạo các khung giờ từ 7:00 đến 20:00, mỗi khung cách nhau 30 phút
    valid_time_slots = generate_time_slots(datetime.strptime("07:00", "%H:%M"), datetime.strptime("20:00", "%H:%M"), 30)

    # Biểu mẫu đặt lịch khám
    with st.form("appointment_form"):
        date = st.date_input("Ngày khám", datetime.now())
        selected_time = st.selectbox("Thời gian khám", valid_time_slots)  # Hiển thị các khung giờ hợp lệ

        # Tải dữ liệu tỉnh
        provinces = get_provinces()
        provinces_names = [province["name"] for province in provinces]
        selected_province_name = st.selectbox("Tỉnh/Thành phố", provinces_names, key="province")

        # Lấy ID tỉnh
        selected_province_id = next((p["code"] for p in provinces if p["name"] == selected_province_name), None)

        # Khi chọn tỉnh mới, reset lại huyện và xã trong session_state
        if selected_province_id and "selected_province_id" not in st.session_state:
            st.session_state.selected_province_id = selected_province_id

        # Lấy danh sách huyện cho tỉnh đã chọn
        if "selected_province_id" in st.session_state:
            districts = get_districts(st.session_state.selected_province_id)
            districts_names = [district["name"] for district in districts]
            selected_district_name = st.selectbox("Quận/Huyện", districts_names, key="district")

            # Lấy ID huyện
            selected_district_id = next((d["code"] for d in districts if d["name"] == selected_district_name), None)

            # Khi chọn huyện mới, reset lại xã trong session_state
            if selected_district_id and "selected_district_id" not in st.session_state:
                st.session_state.selected_district_id = selected_district_id

            # Lấy danh sách xã/phường cho huyện đã chọn
            if "selected_district_id" in st.session_state:
                wards = get_wards(st.session_state.selected_district_id)
                wards_names = [ward["name"] for ward in wards]
                selected_ward_name = st.selectbox("Phường/Xã", wards_names, key="ward")
        
        # Thông tin chi tiết địa chỉ
        detail_address = st.text_input("Địa chỉ cụ thể")
        service = st.selectbox("Dịch vụ khám", ["Khám tổng quát", "Khám chuyên khoa", "Xét nghiệm"])
        
        # Xử lý khi đặt lịch
        if st.form_submit_button("Đặt Lịch"):
            full_address = f"{detail_address}, {selected_ward_name}, {selected_district_name}, {selected_province_name}"
            st.success(f"Đặt lịch khám thành công vào {date} lúc {selected_time} tại {full_address} cho dịch vụ {service}.")


# Hàm cho trang Xem Lịch Sử Khám
def appointment_history_page():
    st.title("Lịch Sử Khám")
    if not sample_appointments:
        st.write("Bạn chưa có lịch sử khám.")
    else:
        for appointment in sample_appointments:
            st.subheader(f"Ngày: {appointment['date']} - Giờ: {appointment['time']}")
            st.write(f"Bác sĩ: {appointment['doctor']}")
            st.write(f"Địa điểm: {appointment['location']}")
            st.write(f"Dịch vụ: {appointment['service']}")
            st.write(f"Giá tiền: {appointment['price']}")
            st.write("---")

# Xác định route và điều hướng đến trang tương ứng
if st.session_state.page == 'register':
    register_page()
elif st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'book_appointment':
    book_appointment_page()
elif st.session_state.page == 'update_profile':
    update_profile_page()
elif st.session_state.page == 'appointment_history':
    appointment_history_page()
else:
    home_page()

# Sidebar điều hướng
st.sidebar.button("Trang Chủ", on_click=lambda: navigate("home"))
st.sidebar.button("Đăng Ký", on_click=lambda: navigate("register"))
st.sidebar.button("Đăng Nhập", on_click=lambda: navigate("login"))
st.sidebar.button("Đặt Lịch Khám", on_click=lambda: navigate("book_appointment"))
st.sidebar.button("Cập Nhật Hồ Sơ", on_click=lambda: navigate("update_profile"))
st.sidebar.button("Lịch Sử Khám", on_click=lambda: navigate("appointment_history"))
