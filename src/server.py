from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests

# Tải các biến môi trường từ .env file
load_dotenv()

app = Flask(__name__)
config = {
    'verifyToken': os.getenv("VERIFY_TOKEN")
}
print(f"Verify Token: {config['verifyToken']}")

@app.route('/')
def home():
    return render_template("HomePage.html")

@app.route('/webhook', methods=['POST']) 
def webhook_post():
    body = request.get_json()  # Nhận dữ liệu JSON
    print("Received body:", body)  # In ra toàn bộ body nhận được

    if not body or "object" not in body or body["object"] != "page":
        return "Invalid request", 400  # Trả về lỗi 400 nếu body không hợp lệ

    for entry in body["entry"]:
        webhook_event = entry["messaging"][0]
        print("Webhook Event:", webhook_event)  # In ra để kiểm tra webhook_event
        sender_psid = webhook_event["sender"]["id"]
        print("Sender PSID:", sender_psid)

        if "message" in webhook_event:
            handle_message(sender_psid, webhook_event["message"])
        elif "postback" in webhook_event:  # Kiểm tra sự kiện postback
            handle_postback(sender_psid, webhook_event["postback"])
        else:
            print("No message or postback found in the webhook event.")

    return "EVENT_RECEIVED", 200

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
    return render_template("webhook.html")

def handle_message(sender_psid, received_message):
    if "text" in received_message:
        response = {
            "text": f"You sent the message: '{received_message['text']}. Now send me an image!'"
        }
        call_send_api(sender_psid, response)
    else:
        print("No text found in the message")
        # Có thể gửi phản hồi cho người dùng nếu cần

def handle_postback(sender_psid, received_postback):
    # Xử lý sự kiện postback nếu cần
    print("Postback received:", received_postback)

def call_send_api(sender_psid, response):
    request_body = {
        "recipient": {
            "id": sender_psid
        },
        "message": response
    }

    # Gửi yêu cầu HTTP đến Messenger Platform
    res = requests.post(
        "https://graph.facebook.com/v21.0/me/messages", 
        params={"access_token": os.getenv("PAGE_ACCESS_TOKEN")},
        json=request_body
    )

    if res.status_code == 200:
        print('Message sent!')
    else:
        print(f"Unable to send message: {res.status_code} - {res.text}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  
    app.run(host='0.0.0.0', port=port, debug=True)
