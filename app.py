from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)
BOT_TOKEN = '7230039306:AAH56vqDoFdic9SBZOx2F5e9SPc6v1R-EgU'
SUBSCRIBERS_FILE = 'subscribers.json'

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_subscriber(chat_id):
    subscribers = load_subscribers()
    if chat_id not in subscribers:
        print(f"New subscriber found: {chat_id}")
        subscribers.append(chat_id)
        with open(SUBSCRIBERS_FILE, 'w') as f:
            json.dump(subscribers, f)

def send_to_all(msg_type, content_url, caption=None):
    subscribers = load_subscribers()
    for chat_id in subscribers:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{msg_type}"
        data = {'chat_id': chat_id}
        if msg_type == "sendMessage":
            data['text'] = content_url
        elif msg_type == "sendPhoto":
            data['photo'] = content_url
            if caption:
                data['caption'] = caption
        elif msg_type == "sendVideo":
            data['video'] = content_url
            if caption:
                data['caption'] = caption
        elif msg_type == "sendDocument":
            data['document'] = content_url
            if caption:
                data['caption'] = caption

        try:
            requests.post(url, data=data)
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        if text == '/start':
            save_subscriber(chat_id)
            welcome_message = "أهلاً بك في البوت! سيتم إعلامك بكل جديد."
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {'chat_id': chat_id, 'text': welcome_message}
            try:
                requests.post(url, data=data)
            except Exception as e:
                print(f"Failed to send welcome message to {chat_id}: {e}")
    return jsonify({"ok": True})

@app.route('/broadcast', methods=['POST'])
def broadcast():
    data = request.json
    msg_type = data.get("type")
    content_url = data.get("url")
    caption = data.get("caption")
    send_to_all(msg_type, content_url, caption)
    return jsonify({"status": "sent"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
