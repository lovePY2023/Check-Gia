import streamlit as st
import json
import os
import asyncio
import re
from scraper import scrape_all_pages
from storage import compare_data
from scraper_vattu import scrape_vattu_logic

# Page config
st.set_page_config(page_title="Minh Thành Intel - Máy lạnh & Vật tư", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_store.json")
VATTU_FILE = os.path.join(BASE_DIR, "data_vattu.json")

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def parse_price(val):
    if not val: return 0
    if isinstance(val, int): return val
    return int(re.sub(r'\D', '', str(val))) or 0

def format_vnd(val):
    return "{:,}".format(val).replace(',', '.') + " đ"

# --- Main App ---
st.title("📊 Minh Thành Market Intel")

# Sidebar Actions
with st.sidebar:
    st.header("Thao tác")
    if st.button("🔍 Quét MÁY LẠNH", use_container_width=True):
        with st.spinner("Đang quét toàn kho máy lạnh..."):
            url = "https://dienmayminhthanh.com/may-lanh"
            try:
                # Playwright in Streamlit needs to be installed
                # In Streamlit Cloud, you might need to run playwright install
                new_data = asyncio.run(scrape_all_pages(url))
                report = compare_data(new_data)
                st.success("Quét thành công!")
                if report.get('price_changes'):
                    st.warning("Có thay đổi giá!")
                    for c in report['price_changes']:
                        st.write(f"- {c['name']}: {c['old_price']} -> {c['new_price']}")
                else:
                    st.info("Dữ liệu không đổi.")
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if st.button("🛠 Quét VẬT TƯ", use_container_width=True):
        with st.spinner("Đang quét giá ống đồng & dây điện..."):
            try:
                data = scrape_vattu_logic()
                st.success(f"Quét thành công {len(data)} mục!")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")

# Data Loading
data_machine = load_json(DATA_FILE)
data_vattu = load_json(VATTU_FILE)

tab1, tab2, tab3 = st.tabs(["📦 MÁY LẠNH", "🛠 VẬT TƯ", "🧮 TÍNH GIÁ"])

with tab1:
    st.subheader(f"Danh sách máy lạnh ({len(data_machine)})")
    if data_machine:
        # Display as a table or dataframe
        st.table(data_machine)
    else:
        st.info("Chưa có dữ liệu máy lạnh. Hãy nhấn 'Quét MÁY LẠNH' ở sidebar.")

with tab2:
    st.subheader(f"Danh sách vật tư ({len(data_vattu)})")
    if data_vattu:
        st.table(data_vattu)
    else:
        st.info("Chưa có dữ liệu vật tư. Hãy nhấn 'Quét VẬT TƯ' ở sidebar.")

with tab3:
    st.subheader("🧮 BẢNG DỰ TOÁN BÁO GIÁ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chọn máy
        machine_options = {f"{item['name']} ({item['price']})": item for item in data_machine}
        selected_machine_name = st.selectbox("1. Chọn Máy Lạnh:", ["-- Chọn máy --"] + list(machine_options.keys()))
        
        # Ống đồng
        vattu_ong = [item for item in data_vattu if 'Ống đồng' in item.get('category', '')]
        ong_options = {f"{item['name']} ({item['price_fmt']})": item['price'] for item in vattu_ong}
        selected_ong_name = st.selectbox("2. Loại ống đồng:", list(ong_options.keys()))
        qty_ong = st.number_input("Số mét ống:", min_value=0.0, value=1.0, step=0.5)
        
    with col2:
        # Dây điện
        vattu_day = [item for item in data_vattu if 'Dây' in item.get('category', '')]
        day_options = {f"{item['name']} ({item['price_fmt']})": item['price'] for item in vattu_day}
        selected_day_name = st.selectbox("3. Loại dây điện:", list(day_options.keys()))
        qty_day = st.number_input("Số mét dây:", min_value=0.0, value=5.0, step=1.0)
        
        # Khác
        eke_price = st.number_input("4. Giá Eke/Giá đỡ (đàn đồng):", value=120000)
        cb_price = st.number_input("5. Giá CB/Aptomat:", value=80000)

    # Calculation logic
    machine_price = 0
    if selected_machine_name != "-- Chọn máy --":
        machine_price = parse_price(machine_options[selected_machine_name]['price'])
    
    ong_unit_price = ong_options.get(selected_ong_name, 0)
    day_unit_price = day_options.get(selected_day_name, 0)
    
    total_vattu = (ong_unit_price * qty_ong) + (day_unit_price * qty_day) + eke_price + cb_price
    total_all = machine_price + total_vattu
    
    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Tiền Máy", format_vnd(machine_price))
        st.metric("Tiền Vật Tư", format_vnd(int(total_vattu)))
    with res_col2:
        st.metric("TỔNG CỘNG", format_vnd(int(total_all)))

st.caption("Lưu ý: Dữ liệu được lấy từ kho dữ liệu quét mới nhất.")
