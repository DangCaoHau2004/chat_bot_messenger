from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests
load_dotenv()

app = Flask(__name__)
config = {
    'verifyToken': os.getenv("VERIFY_TOKEN")
}
print(config["verifyToken"])

@app.route('/')
def home():
    return render_template("HomePage.html")

@app.route('/webhook', methods=['POST']) 
def webhook_post():
    body = request.form
    if body["object"] == "page":
        for entry in body["entry"]:
            webhook_event = entry["messaging"][0]
            print(webhook_event)
            sender_psid = webhook_event["sender"]["id"]
            print("Sender PSID:",sender_psid)
            if webhook_event["message"]:
                handle_message(sender_psid, webhook_event["message"])
            else:
                handle_postback(sender_psid, webhook_event["postback"])
        return "EVENT_RECEIVED", 200
    else:
        return "Not Found", 404

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
    if received_message["text"]:
        response = {
            "text": f"You sent the message: '{received_message['text']}. Now send me an image!'"
        }
    call_send_api(sender_psid,response)
def handle_postback(sender_psid, received_postback):
    pass
def call_send_api(sender_psid, response):
    request_body = {
        "recipient": {
            "id": sender_psid
        },
        "message": response
    }

    # Gửi yêu cầu HTTP đến Messenger Platform
    res = requests.post(
        "https://graph.facebook.com/v2.6/me/messages",
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
