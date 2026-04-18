import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings()

# async keyword kept for compatibility with streamlit_app.py
async def scrape_all_pages(base_url):
    all_results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    current_page = 1
    max_pages = 20
    
    while current_page <= max_pages:
        url = f"{base_url}?page={current_page}"
        print(f"Scraping Page {current_page}...")
        
        try:
            resp = requests.get(url, headers=headers, timeout=15, verify=False)
            if resp.status_code != 200:
                print(f"Failed to load page {current_page}")
                break
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            products = soup.select(".item_product_main")
            
            if not products:
                print(f"Finished at page {current_page} - no products")
                break
            
            for product in products:
                try:
                    name_el = product.select_one("h3.product-name a")
                    if not name_el: continue
                    name = name_el.text.strip()
                    link = "https://dienmayminhthanh.com" + name_el.get("href")
                    
                    price_el = product.select_one(".special-price .price")
                    if not price_el:
                        price_el = product.select_one(".price")
                    
                    price = price_el.text.strip() if price_el else "0"
                    
                    model = "N/A"
                    match = re.search(r'([A-Z0-9-]{5,})', name)
                    if match:
                        model = match.group(1)

                    all_results.append({
                        "name": name,
                        "model": model,
                        "price": price,
                        "link": link
                    })
                except Exception as ex:
                    continue
            
            current_page += 1
            
        except Exception as e:
            print(f"Lỗi tại trang {current_page}: {e}")
            break
            
    # Lọc trùng lặp bằng link
    unique_results = {item['link']: item for item in all_results}.values()
    return list(unique_results)

if __name__ == "__main__":
    import asyncio
    url = "https://dienmayminhthanh.com/may-lanh"
    data = asyncio.run(scrape_all_pages(url))
    print(f"Mission Success: {len(data)} items found.", data[:2])
