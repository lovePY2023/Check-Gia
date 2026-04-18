from flask import Flask, render_template_string, jsonify
import json
import os
import asyncio
from scraper import scrape_all_pages
from storage import compare_data
from scraper_vattu import scrape_vattu_logic

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_store.json")
VATTU_FILE = os.path.join(BASE_DIR, "data_vattu.json")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Minh Thành Intel - Máy lạnh & Vật tư</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #2563eb; --secondary: #10b981; --bg: #f8fafc; --text: #1e293b; }
        body { font-family: 'Inter', sans-serif; background-color: var(--bg); margin: 0; padding: 15px; color: var(--text); }
        .container { max-width: 1400px; margin: auto; background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        
        .header { display: flex; flex-direction: column; gap: 15px; margin-bottom: 25px; border-bottom: 2px solid #f1f5f9; padding-bottom: 20px; }
        @media(min-width: 768px) { .header { flex-direction: row; justify-content: space-between; align-items: center; } }
        h1 { font-size: 22px; font-weight: 800; color: #0f172a; margin: 0; display: flex; align-items: center; gap: 10px; }
        
        .action-btns { display: flex; gap: 10px; flex-wrap: wrap; }
        .btn-scan { border: none; padding: 10px 20px; border-radius: 10px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.3s; }
        .btn-machine { background: #0f172a; color: white; }
        .btn-vattu { background: var(--secondary); color: white; }
        .btn-scan:hover { opacity: 0.8; transform: translateY(-2px); }

        .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        .nav-tab { cursor: pointer; padding: 8px 16px; border-radius: 8px; font-weight: 600; color: #64748b; }
        .nav-tab.active { background: var(--primary); color: white; }

        .report-box { display: none; background: #fffbeb; border: 2px solid #fde68a; border-radius: 12px; padding: 15px; margin-bottom: 20px; }
        
        .table-wrapper { overflow-x: auto; border-radius: 12px; border: 1px solid #e2e8f0; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8fafc; padding: 12px; text-align: left; font-size: 12px; font-weight: 700; color: #64748b; }
        td { padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
        
        .price { color: #dc2626; font-weight: 800; }
        .vattu-row { background: #f0fdf4; }
        .loading-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 99; justify-content: center; align-items: center; color: white; flex-direction: column; }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loader">
        <i class="fas fa-spinner fa-3x fa-spin"></i>
        <h2 id="loaderText">Đang quét dữ liệu...</h2>
    </div>

    <div class="container">
        <div class="header">
            <h1><i class="fas fa-chart-line"></i> Minh Thành Market Intel</h1>
            <div class="action-btns">
                <button class="btn-scan btn-machine" onclick="startScan('machine')"><i class="fas fa-snowflake"></i> MÁY LẠNH</button>
                <button class="btn-scan btn-vattu" onclick="startScan('vattu')"><i class="fas fa-tools"></i> VẬT TƯ</button>
            </div>
        </div>

        <div id="reportBox" class="report-box">
             <h4 style="margin:0 0 10px 0;"><i class="fas fa-bell"></i> THÔNG BÁO MỚI QUÉT</h4>
             <div id="reportContent"></div>
        </div>

        <div class="nav-tabs">
            <div class="nav-tab active" onclick="switchTab('machine', this)">📦 MÁY LẠNH ({{ data|length }})</div>
            <div class="nav-tab" onclick="switchTab('vattu', this)">🛠 VẬT TƯ ({{ vattu|length }})</div>
            <div class="nav-tab" onclick="switchTab('calc', this)" style="background: #6d28d9; color: white;">🧮 TÍNH GIÁ</div>
        </div>
        
        <!-- Tab Máy Lạnh -->
        <div id="tab-machine" class="content-tab">
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>STT</th><th>Sản phẩm</th><th>Model</th><th>Giá</th><th>Web</th></tr></thead>
                    <tbody>
                        {% for item in data %}
                        <tr><td>{{ loop.index }}</td><td style="font-weight:600;">{{ item.name }}</td><td>{{ item.model }}</td><td class="price">{{ item.price }}</td><td><a href="{{ item.link }}" target="_blank">Link</a></td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Tab Vật Tư -->
        <div id="tab-vattu" class="content-tab" style="display:none;">
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>Danh mục</th><th>Tên vật tư</th><th>Giá chi tiết</th></tr></thead>
                    <tbody>
                        {% for item in vattu %}
                        <tr class="vattu-row">
                            <td style="color:#059669; font-weight:700; font-size:12px;">{{ item.category }}</td>
                            <td style="font-weight:600;">{{ item.name }}</td>
                            <td class="price">{{ item.price_fmt }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Tab Tính Giá (Dự Toán) -->
        <div id="tab-calc" class="content-tab" style="display:none;">
            <div style="background: #fdf4ff; padding: 20px; border-radius: 12px; border: 1px solid #f5d0fe;">
                <h3 style="margin-top:0; color:#701a75;"><i class="fas fa-calculator"></i> BẢNG DỰ TOÁN BÁO GIÁ</h3>
                
                <div style="display:grid; grid-template-columns: 1fr; gap:15px;">
                    <div>
                        <label><b>1. Chọn Máy Lạnh:</b></label>
                        <select id="calc-machine" style="width:100%; padding:10px; border-radius:8px; margin-top:5px;" onchange="calculate()">
                            <option value="0" data-price="0">-- Chọn máy --</option>
                            {% for item in data %}
                            <option value="{{ item.model }}" data-price="{{ item.price }}">{{ item.name }} ({{ item.price }})</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                        <div>
                            <label><b>2. Ống đồng (mét):</b></label>
                            <input type="number" id="qty-ong" value="1" min="1" style="width:100%; padding:10px; border-radius:8px; margin-top:5px;" oninput="calculate()">
                        </div>
                        <div>
                            <label><b>Giá ống/mét:</b></label>
                            <select id="price-ong" style="width:100%; padding:10px; border-radius:8px; margin-top:5px;" onchange="calculate()">
                                {% for item in vattu if 'Ống đồng' in item.category %}
                                <option value="{{ item.price }}">{{ item.name }} ({{ item.price_fmt }})</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                        <div>
                            <label><b>3. Dây điện (mét):</b></label>
                            <input type="number" id="qty-day" value="5" min="0" style="width:100%; padding:10px; border-radius:8px; margin-top:5px;" oninput="calculate()">
                        </div>
                        <div>
                            <label><b>Loại dây:</b></label>
                            <select id="price-day" style="width:100%; padding:10px; border-radius:8px; margin-top:5px;" onchange="calculate()">
                                {% for item in vattu if 'Dây' in item.category %}
                                <option value="{{ item.price }}">{{ item.name }} ({{ item.price_fmt }})</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                         <div>
                            <label><b>4. Eke/Giá đỡ:</b></label>
                            <select id="price-eke" style="width:100%; padding:10px; border-radius:8px; margin-top:5px;" onchange="calculate()">
                                <option value="0">Không dùng</option>
                                {% for item in vattu if 'Eke' in item.category or 'Giá' in item.name %}
                                <option value="{{ item.price }}">{{ item.name }} ({{ item.price_fmt }})</option>
                                {% endfor %}
                                <option value="120000">Eke thường (120k)</option>
                                <option value="180000">Eke Inox (180k)</option>
                            </select>
                        </div>
                        <div>
                            <label><b>5. CB/Aptomat:</b></label>
                            <input type="number" id="price-cb" value="80000" style="width:100%; padding:10px; border-radius:8px; margin-top:5px;" oninput="calculate()">
                        </div>
                    </div>
                </div>

                <div style="margin-top:25px; background:white; padding:20px; border-radius:12px; border:2px solid #701a75;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span>Tiền Máy:</span> <b id="res-machine">0đ</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                        <span>Vật tư (Ống + Dây + Eke + CB):</span> <b id="res-vattu">0đ</b>
                    </div>
                    <hr>
                    <div style="display:flex; justify-content:space-between; font-size:20px; color:#701a75;">
                        <b>TỔNG CỘNG:</b> <b id="res-total">0đ</b>
                    </div>
                </div>
                <p style="font-size:12px; color:#6b7280; margin-top:10px;">* Lưu ý: Giá vật tư lấy từ dữ liệu quét mới nhất. Các giá CB/Eke có thể sửa tay.</p>
            </div>
        </div>
    </div>

    <script>
        function parsePrice(str) {
            if(!str) return 0;
            return parseInt(str.toString().replace(/[^0-9]/g, '')) || 0;
        }

        function formatVND(val) {
            return val.toLocaleString('vi-VN') + ' đ';
        }

        function calculate() {
            const machinePrice = parsePrice(document.getElementById('calc-machine').selectedOptions[0].getAttribute('data-price'));
            
            const ongPrice = parsePrice(document.getElementById('price-ong').value);
            const ongQty = parseFloat(document.getElementById('qty-ong').value) || 0;
            
            const dayPrice = parsePrice(document.getElementById('price-day').value);
            const dayQty = parseFloat(document.getElementById('qty-day').value) || 0;
            
            const ekePrice = parsePrice(document.getElementById('price-eke').value);
            const cbPrice = parsePrice(document.getElementById('price-cb').value);
            
            const totalVattu = (ongPrice * ongQty) + (dayPrice * dayQty) + ekePrice + cbPrice;
            const totalAll = machinePrice + totalVattu;
            
            document.getElementById('res-machine').innerText = formatVND(machinePrice);
            document.getElementById('res-vattu').innerText = formatVND(totalVattu);
            document.getElementById('res-total').innerText = formatVND(totalAll);
        }
        async function startScan(type) {
            document.getElementById('loader').style.display = 'flex';
            document.getElementById('loaderText').innerText = type === 'machine' ? 'Đang quét toàn kho máy lạnh...' : 'Đang quét giá ống đồng & dây điện...';
            try {
                const endpoint = type === 'machine' ? '/run-scan' : '/run-scan-vattu';
                const response = await fetch(endpoint);
                const result = await response.json();
                if(type === 'vattu') location.reload();
                else showReport(result);
            } catch (e) { alert('Hệ thống bận, vui lòng thử lại: ' + e); }
            finally { document.getElementById('loader').style.display = 'none'; }
        }

        function showReport(result) {
            const box = document.getElementById('reportBox');
            box.style.display = 'block';
            let html = 'Dữ liệu không đổi.';
            if (result.price_changes && result.price_changes.length > 0) {
                html = '<b>Thay đổi giá:</b><br>' + result.price_changes.map(c => `- ${c.name}: ${c.old_price} -> ${c.new_price}`).join('<br>');
            }
            document.getElementById('reportContent').innerHTML = html;
        }

        function switchTab(type, el) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            document.querySelectorAll('.content-tab').forEach(c => c.style.display = 'none');
            document.getElementById('tab-' + type).style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: data = json.load(f)
        except: pass
    
    vattu = []
    if os.path.exists(VATTU_FILE):
        try:
            with open(VATTU_FILE, "r", encoding="utf-8") as f: vattu = json.load(f)
        except: pass
        
    return render_template_string(HTML_TEMPLATE, data=data, vattu=vattu)

@app.route('/run-scan')
def run_scan():
    url = "https://dienmayminhthanh.com/may-lanh"
    new_data = asyncio.run(scrape_all_pages(url))
    report = compare_data(new_data)
    return jsonify(report)

@app.route('/run-scan-vattu')
def run_scan_vattu():
    data = scrape_vattu_logic()
    return jsonify({"status": "success", "count": len(data)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
