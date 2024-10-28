import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy thông tin từ biến môi trường
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CLIENT_EMAIL = os.getenv("GOOGLE_CLIENT_EMAIL")
GOOGLE_PRIVATE_KEY = os.getenv("GOOGLE_PRIVATE_KEY").replace(
    "\\n", "\n")  # thay thế "\n" để đảm bảo định dạng đúng
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_PRIVATE_KEY_ID = os.getenv("GOOGLE_PRIVATE_KEY_ID")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# Định nghĩa các scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Tạo thông tin xác thực từ thông tin môi trường
credentials_info = {
    "type": "service_account",
    "project_id": GOOGLE_PROJECT_ID,
    "private_key_id": GOOGLE_PRIVATE_KEY_ID,
    "private_key": GOOGLE_PRIVATE_KEY,
    "client_email": GOOGLE_CLIENT_EMAIL,
    "client_id": GOOGLE_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{GOOGLE_CLIENT_EMAIL}"
}

# Tạo đối tượng Credentials từ thông tin xác thực
creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)

# Tạo một client gspread với thông tin xác thực
client = gspread.authorize(creds)

# ID của Google Sheet
sheet = client.open_by_key(SPREADSHEET_ID)

# Đọc giá trị từ hàng đầu tiên
values_list = sheet.sheet1.row_values(1)
print(values_list)
