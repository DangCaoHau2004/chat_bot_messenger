from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
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
 
if __name__ == "__main__":
    app.run(debug=True)
