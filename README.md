# Price Tracker Dashboard

Hệ thống theo dõi giá máy lạnh và vật tư từ các trang web điện máy.

## Tính năng
- Quét giá máy lạnh tự động bằng Playwright.
- Quét giá vật tư (ống đồng, dây điện) bằng BeautifulSoup.
- So sánh giá và báo cáo thay đổi.
- Công cụ tính toán báo giá (Calculator) tích hợp.
- Lưu trữ bền vững qua Supabase.

## Cách chạy cục bộ
1. Cài đặt thư viện: `pip install -r requirements.txt`
2. Cài đặt browser: `playwright install chromium`
3. Chạy app: `streamlit run streamlit_app.py`

## Triển khai (Deployment)
- App được tối ưu hóa cho **Streamlit Cloud**.
- Cần cấu hình `SUPABASE_URL` và `SUPABASE_KEY` trong Secrets nếu muốn lưu trữ vĩnh viễn.
