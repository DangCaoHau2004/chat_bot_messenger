import yaml
from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests
from enterDataToGoogleSheet import enterDataToGoogleSheet
import numpy as np
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from modules.phan_loai_cau_hoi import phan_loai_cau_hoi
from modules.xu_ly_tra_loi import tra_loi_tu_van
from tienXuLyDuLieu import tienXuLyDuLieu
sched = BackgroundScheduler()
# Định nghĩa một tác vụ

tienXuLyDuLieu()


@sched.scheduled_job('interval', minutes=5)
def timed_job():
    removeUser()


sched.start()

# Tải các biến môi trường từ .env file
load_dotenv()

app = Flask(__name__)
config = {
    'verifyToken': os.getenv("VERIFY_TOKEN")
}

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
URL_WEB_ORDER = os.getenv("URL_WEB_ORDER")
ADMIN_PSID = os.getenv("ADMIN_PSID")


# Route Home

support_users = {}


@app.route('/')
def home():
    return render_template("HomePage.html")


# route webhook_post


@app.route('/webhook', methods=['POST'])
def webhook_post():
    body = request.get_json()  # Nhận dữ liệu JSON

    if not body or "object" not in body or body["object"] != "page":
        return "Invalid request", 400  # Trả về lỗi 400 nếu body không hợp lệ

    for entry in body["entry"]:
        # chỉ cần lấy giá trị đầu tiên, để lấy psid
        webhook_event = entry["messaging"][0]

        print("Webhook Event:", webhook_event)
        sender_psid = webhook_event["sender"]["id"]
        if sender_psid in support_users:
            if "postback" in webhook_event and "payload" in webhook_event["postback"]:
                payload = webhook_event["postback"]["payload"].lower()
                if payload not in ['order', 'get_started', 'restart_bot']:
                    # Xử lý trường hợp payload không phải là 'order', 'get_started' hoặc 'restart_bot'
                    support_users[sender_psid] = datetime.now()
                    return "Người dùng đang được hỗ trợ", 200
            elif "message" in webhook_event:
                support_users[sender_psid] = datetime.now()
                return "Người dùng đang được hỗ trợ", 200

        print("Sender PSID:", sender_psid)
        if "message" in webhook_event:
            handle_message(sender_psid, webhook_event["message"])
        # nếu postback tồn tại gọi handle_postback
        elif "postback" in webhook_event:
            handle_postback(sender_psid, webhook_event["postback"])
        else:
            print("No message or postback found in the webhook event.")

    return "EVENT_RECEIVED", 200

# route webhook_get


@app.route('/webhook')
def webhook_get():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode and token:
        if mode == "subscribe" and token == config['verifyToken']:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Forbidden", 403

# setup-profile


@app.route('/setup-profile', methods=['POST'])
def setup_profile():
    request_body = {
        "get_started": {"payload": "GET_STARTED"}
    }

    # post
    res = requests.post(
        f"https://graph.facebook.com/v21.0/me/messenger_profile",
        params={"access_token": PAGE_ACCESS_TOKEN},
        json=request_body
    )

    # kiểm tra
    if res.status_code == 200:
        return {"message": "Profile setup successful"}, 200
    else:
        return {"error": res.text}, res.status_code


@app.route('/setup-persitent-menu', methods=['POST'])
def setup_persitent_menu():

    request_body = {
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": "Gọi nhân viên hỗ trợ",
                        "payload": "CARE_HELP"
                    },
                    {
                        "type": "postback",
                        "title": "Khởi động lại bot",
                        "payload": "RESTART_BOT"
                    },
                    {
                        "type": "postback",
                        "title": "Đặt hàng",
                        "payload": "ORDER"
                    },
                    {
                        "type": "postback",
                        "title": "Cách sử dụng bot",
                        "payload": "HOW_TO_USE"
                    }
                ]
            }
        ]
    }

    res = requests.post(
        f"https://graph.facebook.com/v21.0/me/messenger_profile",
        params={"access_token": PAGE_ACCESS_TOKEN},
        json=request_body
    )
    if res.status_code == 200:
        return {"message": "Profile setup successful"}, 200
    else:
        return {"error": res.text}, res.status_code


@app.route('/Order')
def Order():
    psid = request.args.get('psid')
    return render_template("/Order.html", psid=psid)


@app.route("/handle-order", methods=['POST'])
def handleOrder():
    # Lấy các dữ liệu từ form Order.html
    psid = request.form.get('psid')
    name = request.form.get('name')
    sdt = request.form.get('sdt')
    address = request.form.get("address")
    sanPham = np.array(request.form.getlist("sanPham"))
    loaiSanPham = np.array(request.form.getlist("loaiSanPham"))

    # Gửi thông báo xác nhận đơn hàng cho khách
    with open("./src/data/cau_tra_loi/tu_van.yml", "r", encoding="utf-8") as f:
        san_pham = yaml.safe_load(f)
    camon = san_pham["dat_hang"]["cam_on"]
    call_send_api(
        sender_psid=psid,
        response={
            "text": camon
        }
    )

    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    thoiGianDat = datetime.now(
        vietnam_tz).strftime("%Y-%m-%d %H:%M:%S")
    res = requests.get(
        f"https://graph.facebook.com/{
            psid}?fields=first_name,last_name,profile_pic",
        params={"access_token": PAGE_ACCESS_TOKEN}
    )
    user = res.json()
    nameFacebook = f"{user['first_name']} {user['last_name']}"

    sanPham = np.char.add(sanPham, ': ')
    toanBoSP = ', '.join(np.char.add(sanPham, loaiSanPham))

    # Chuẩn bị dữ liệu để ghi vào Google Sheets
    data = [thoiGianDat, nameFacebook, name, sdt, address, toanBoSP]

    try:
        enterDataToGoogleSheet(data=data)
    except Exception as e:
        # Gửi thông báo lỗi nếu ghi vào Google Sheets thất bại
        call_send_api(
            sender_psid=ADMIN_PSID,
            response={"text": f"Lỗi khi đặt đơn hàng của {
                nameFacebook}: {str(e)}"}
        )

    # Gửi thông báo đơn hàng cho admin về thông tin đơn hàng
    call_send_api(
        sender_psid=ADMIN_PSID,
        response={
            "text": (
                f"Tên Facebook: {nameFacebook}\n"
                f"Họ Tên: {name}\n"
                f"SĐT: {sdt}\n"
                f"Địa chỉ: {address}\n"
                f"Sản phẩm: {toanBoSP}\n"
                f"Thời gian đặt: {thoiGianDat}"
            )
        }
    )

    return render_template("thankForOrder.html")


# handle_message


def handle_message(sender_psid, received_message):
    if "text" in received_message:
        result = phan_loai_cau_hoi(
            new_text=received_message["text"], psid=sender_psid)
        for response in result:
            call_send_api(sender_psid=sender_psid, response=response)
    else:
        print("No text found in the message")


# handle_postback


def handle_postback(sender_psid, received_postback):
    payload = received_postback["payload"]
    # xử lý khi người dùng click vào nút bắt đầu
    if payload.lower() == "get_started" or payload.lower() == 'restart_bot':
        # đọc dữ liệu từ tên người dùng
        res = requests.get(
            f"https://graph.facebook.com/{
                sender_psid}?fields=first_name,last_name,profile_pic",
            params={"access_token": PAGE_ACCESS_TOKEN})
        if res.status_code == 200:
            user = res.json()
            name = user["first_name"] + " " + user["last_name"]
            response = {"text": f"Chào {name} đến với shop Thế Giới Vest"}
            call_send_api(sender_psid=sender_psid, response=response)
            if sender_psid in support_users:
                support_users.pop(sender_psid)
        else:
            print("Yêu cầu thất bại:", res.status_code, res.text)
    elif payload.lower() == 'order':
        result = tra_loi_tu_van(du_doan="dat_hang", psid=sender_psid)
        for response in result:
            call_send_api(sender_psid=sender_psid, response=response)
    elif payload.lower() == "care_help":
        response = {"text": "Bạn chờ chút nhé sẽ có nhân viên hỗ trợ bạn ngay!"}
        support_users[sender_psid] = datetime.now()
        print(support_users)
        call_send_api(sender_psid=sender_psid, response=response)
        # lấy tên người dùng
        call_admin(sender_psid=sender_psid)
    elif payload.lower() == "how_to_use":
        with open("./src/data/cau_tra_loi/cach_sd.yml", "r", encoding="utf-8") as f:
            how_to_use = yaml.safe_load(f)
        call_send_api(sender_psid=sender_psid, response=how_to_use)


def call_send_api(sender_psid, response):
    request_body = {
        "recipient": {
            "id": sender_psid
        },
        "message": response
    }

    # Gửi Post đến Messenger Platform
    res = requests.post(
        "https://graph.facebook.com/v21.0/me/messages",
        params={"access_token": PAGE_ACCESS_TOKEN},
        json=request_body
    )

    if res.status_code == 200:
        print('Message sent!')
    else:
        print(f"Unable to send message: {res.status_code} - {res.text}")


def removeUser():
    temp = support_users
    users_to_remove = []
    for user in temp:
        difference = datetime.now() - temp[user]
        if difference.total_seconds() / 60 >= 5.0:
            users_to_remove.append(user)

    for user in users_to_remove:
        support_users.pop(user)
        call_send_api(sender_psid=user, response={
                      "text": "Đã quá 5 phút mà bạn không nhắn lại bọn mình xin phép kết thúc cuộc trò chuyện tại đây nhé, cảm ơn bạn và chúc bạn một ngày tốt lành"})


def call_admin(sender_psid):
    res = requests.get(
        f"https://graph.facebook.com/{
            sender_psid}?fields=first_name,last_name,profile_pic",
        params={"access_token": PAGE_ACCESS_TOKEN})
    if res.status_code == 200:
        user = res.json()
        name = user["first_name"] + " " + user["last_name"]
        # thông báo cho admin
    call_send_api(sender_psid=ADMIN_PSID, response={
        "text": f"{name} cần được hỗ trợ"})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
