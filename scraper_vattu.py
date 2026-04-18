import requests
from bs4 import BeautifulSoup
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VATTU_FILE = os.path.join(BASE_DIR, "data_vattu.json")

def clean_price_vattu(text):
    if not text: return "0"
    import re
    digits = re.sub(r'\D', '', text)
    if not digits: return "0"
    return int(digits)

def format_price_vattu(val):
    return "{:,}".format(val).replace(',', '.') + " đ"

def scrape_vattu_logic():
    targets = [
        {"name": "Ống đồng Thái Lan", "url": "https://vattudienlanhgiare.net/san-pham/ong-dong-may-lanh-1hp-phi-6-10-thai-lan-cat-met-1674.html"},
        {"name": "Dây điện Cadivi", "url": "https://vattudienlanhgiare.net/san-pham/day-dien-cadivi-c190.html"},
        {"name": "Phụ kiện & Eke", "url": "https://vattudienlanhgiare.net/san-pham/phu-kien-dien-lanh-khac-c324.html"}
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    all_results = []

    for target in targets:
        try:
            resp = requests.get(target['url'], headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 1. Tra cứu theo Variations (Ống đồng)
            vars = soup.select('.item-collection')
            if vars:
                for v in vars:
                    price_val = clean_price_vattu(v.get('data-giaban', '0'))
                    all_results.append({
                        "category": target['name'],
                        "name": v.text.strip(),
                        "price": price_val,
                        "price_fmt": format_price_vattu(price_val)
                    })
            
            # 2. Tra cứu theo Danh sách (Dây điện & Eke)
            prods = soup.select('h4')
            for p in prods:
                name = p.text.strip()
                price_text = ""
                parent = p.find_parent('div')
                if parent:
                    price_el = parent.select_one('[class*="price"]')
                    if price_el: price_text = price_el.text.strip()
                
                if not price_text:
                    next_el = p.find_next(['p', 'div', 'span'])
                    if next_el and 'đ' in next_el.text:
                        price_text = next_el.text.strip()

                if price_text:
                    price_val = clean_price_vattu(price_text)
                    all_results.append({
                        "category": target['name'],
                        "name": name,
                        "price": price_val,
                        "price_fmt": format_price_vattu(price_val)
                    })
        except Exception as e:
            print(f"Lỗi khi quét {target['name']}: {e}")
            continue
        
    if all_results:
        with open(VATTU_FILE, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)
    
    return all_results

if __name__ == "__main__":
    print("Đang quét thử vật tư...")
    data = scrape_vattu_logic()
    print(f"Đã tìm thấy {len(data)} mục vật tư.")
