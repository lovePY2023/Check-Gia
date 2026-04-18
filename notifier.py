import requests

def send_telegram_report(message, bot_token, chat_id):
    """
    Gửi báo cáo qua Telegram Bot.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Gửi báo cáo thành công!")
        else:
            print(f"Lỗi khi gửi Telegram: {response.text}")
    except Exception as e:
        print(f"Lỗi kết nối Telegram: {e}")

if __name__ == "__main__":
    # Test thử (Cần điền token thật để chạy)
    # send_telegram_report("Test message from Scraper Bot", "YOUR_BOT_TOKEN", "YOUR_CHAT_ID")
    pass
