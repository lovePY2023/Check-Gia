import asyncio
from playwright.async_api import async_playwright
import re
import random

async def scrape_all_pages(base_url):
    all_results = []
    
    # Danh sách User-Agents thực tế để ngụy trang
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    ]

    async with async_playwright() as p:
        # Sử dụng ngẫu nhiên một User-Agent
        user_agent = random.choice(USER_AGENTS)
        
        browser = await p.chromium.launch(headless=True)
        # Tạo context với User-Agent và kích thước màn hình như người thật
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1366, 'height': 768}
        )
        page = await context.new_page()
        
        current_page = 1
        max_pages = 20
        
        while current_page <= max_pages:
            url = f"{base_url}?page={current_page}"
            print(f"Human-like browsing Page {current_page}...")
            
            try:
                # Truy cập web
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Giả lập thao tác cuộn chuột (Scroll) như người đang xem hàng
                await page.mouse.wheel(0, random.randint(300, 700))
                
                # Nghỉ ngẫy nhiên từ 2.5 đến 4.5 giây (Tránh bị soi tần suất cố định)
                await asyncio.sleep(random.uniform(2.5, 4.5))
                
                products = await page.locator(".item_product_main").all()
                
                if not products:
                    print(f"Finished at page {current_page}")
                    break
                
                for product in products:
                    try:
                        name_el = product.locator("h3.product-name a")
                        name = await name_el.inner_text()
                        link = "https://dienmayminhthanh.com" + await name_el.get_attribute("href")
                        
                        price_el = product.locator(".special-price .price")
                        if await price_el.count() == 0:
                            price_el = product.locator(".price")
                        
                        price = await price_el.inner_text()
                        
                        model = "N/A"
                        match = re.search(r'([A-Z0-9-]{5,})', name)
                        if match:
                            model = match.group(1)

                        all_results.append({
                            "name": name.strip(),
                            "model": model.strip(),
                            "price": price.strip(),
                            "link": link
                        })
                    except:
                        continue
                
                current_page += 1
                
            except Exception as e:
                print(f"Warning at page {current_page}: {e}")
                break
                
        await browser.close()
        
    unique_results = {item['link']: item for item in all_results}.values()
    return list(unique_results)

if __name__ == "__main__":
    url = "https://dienmayminhthanh.com/may-lanh"
    data = asyncio.run(scrape_all_pages(url))
    print(f"Mission Success: {len(data)} items found.")
