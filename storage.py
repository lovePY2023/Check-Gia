import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_store.json")

def get_previous_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_new_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def compare_data(new_data):
    old_data = {item['link']: item for item in get_previous_data()}
    report = {
        "price_changes": [],
        "new_items": [],
        "removed_items": []
    }
    
    current_links = set()
    for item in new_data:
        link = item['link']
        current_links.add(link)
        
        if link in old_data:
            old_price_str = old_data[link]['price'].replace('.', '').replace('₫', '').strip()
            new_price_str = item['price'].replace('.', '').replace('₫', '').strip()
            
            try:
                old_p = int(old_price_str)
                new_p = int(new_price_str)
                if new_p != old_p:
                    report["price_changes"].append({
                        "name": item['name'],
                        "old_price": old_data[link]['price'],
                        "new_price": item['price'],
                        "diff": new_p - old_p
                    })
            except:
                pass
        else:
            report["new_items"].append(item)
            
    # Lưu dữ liệu mới nhất
    save_new_data(new_data)
    return report
