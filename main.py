import schedule
import time
import asyncio
from scraper import scrape_data
from storage import compare_and_report
from notifier import send_telegram_report

# Cấu hình
TARGET_URL = "https://example.com" # Thay bằng link bạn muốn theo dõi
TELEGRAM_TOKEN = "ĐIỀN_TOKEN_BOT_CỦA_BẠN"
TELEGRAM_CHAT_ID = "ĐIỀN_CHAT_ID_CỦA_BẠN"

async def job():
    print(f"--- Bắt đầu quy trình lấy dữ liệu lúc {time.strftime('%H:%M:%S')} ---")
    
    # 1. Cào dữ liệu
    new_data = await scrape_data(TARGET_URL)
    
    if not new_data:
        print("Không lấy được dữ liệu.")
        return

    # 2. So sánh với dữ liệu cũ
    changes = compare_and_report(new_data)
    
    # 3. Tạo nội dung báo cáo
    if changes:
        report_msg = f"<b>🔔 BÁO CÁO CẬP NHẬT HÀNG NGÀY</b>\n\n"
        report_msg += f"Phát hiện {len(changes)} thay đổi mới:\n"
        for i, item in enumerate(changes[:10], 1): # Lấy tối đa 10 tin mới nhất để gửi
            report_msg += f"{i}. {item}\n"
        
        if len(changes) > 10:
            report_msg += f"... và {len(changes)-10} mục khác."
    else:
        report_msg = "<b>✅ BÁO CÁO HÀNG NGÀY</b>\n\nKhông có thay đổi mới nào được phát hiện."

    # 4. Gửi thông báo
    # Lưu ý: Bạn cần cấu hình đúng Token và Chat ID ở trên
    send_telegram_report(report_msg, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    print("--- Hoàn thành quy trình ---")

def run_async_job():
    asyncio.run(job())

# Lập lịch chạy lúc 08:00 mỗi ngày
schedule.every().day.at("08:00").do(run_async_job)

# Nếu muốn test ngay lập tức lúc chạy file, bỏ comment dòng dưới:
# run_async_job()

print("Hệ thống đang chạy ngầm... Đang chờ đến 08:00 hàng ngày.")
while True:
    schedule.run_pending()
    time.sleep(60) # Kiểm tra mỗi phút một lần
