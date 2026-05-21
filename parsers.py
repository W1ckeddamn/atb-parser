from urllib.parse import urljoin
from bs4 import BeautifulSoup
import httpx
import time
from fake_useragent import UserAgent
import json
import asyncio     

def load_config(config_path: str = "config.json") -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации {config_path} не найден!")
        return {
            "base_url": "https://www.atbmarket.com/",
            "base_url_catalog": "https://www.atbmarket.com/catalog/load-more-products/",
            "categories": {
                    "Економія": "economy",
                    "Новинки": "novetly",
                    "Акція 7 днів": "388-aktsiya-7-dniv",
                    "Овочі та фрукти": "287-ovochi-ta-frukti",
                    "Бакалія": "285-bakaliya",
                    "Молочні продукти та яйця": "molocni-produkti-ta-ajca",
                    "Алкоголь": "292-alkogol-i-tyutyun",
                    "Напої безалкогольні": "294-napoi-bezalkogol-ni",
                    "Сири": "siri",
                    "М'ясо": "maso",
                    "Кондитерські вироби": "299-konditers-ki-virobi",
                    "Риба і морепродукти": "353-riba-i-moreprodukti",
                    "Хлібобулочні вироби": "325-khlibobulochni-virobi",
                    "Заморожені продукти": "322-zamorozheni-produkti",
                    "Кава, чай": "kava-caj",
                    "Чипси, снеки.": "cipsi-sneki",
                    "Ковбаса і м'ясні делікатеси": "360-kovbasa-i-m-yasni-delikatesi",
                    "Дитяче харчування": "339-dityache-kharchuvannya",
                    "Японська кухня": "415-yapons-ka-kukhnya",
                    "Кулінарія": "502-kulinariya",
                    "Товари для дітей": "373-tovari-dlya-ditey",
                    "Побутова хімія та непродовольчі товари": "308-pobutova-khimiya-ta-neprodovol-chi-tovari",
                    "Гігієна і косметика": "290-gigiena-i-kosmetika",
                    "Товари для дому": "358-tovari-dlya-domu",
                    "Товари для тварин": "389-kantselyars-ki-tovari",
                    "Тютюнові вироби": "479-tyutyunovi-virobi",
                    "Сертифікати та платіжні картки": "sertifikati-ta-platizni-kartki",
                    "Канцелярські товари": "389-kantselyars-ki-tovari"
            }
        }

CONFIG = load_config()

class ATBparser:
    def __init__(self):
        self.base_url: str = CONFIG["base_url"]
        self.base_url_catalog: str = CONFIG["base_url_catalog"]
        self.categories: dict[str, str] = CONFIG["categories"]
        self.ua = UserAgent(browsers=['chrome', 'edge', 'firefox'])
    
    def _get_headers(self) -> dict:
        """Генерирует свежие заголовки со случайным живым User-Agent"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.atbmarket.com/",
        }
        
    def choose_category(self):
        print("Choose category:")
        for i, (name, _) in enumerate(self.categories.items(), start=1):
            print(f"{i}. {name}")
            
        category_index: int = int(input("Enter category number: "))
        category_name: str = list(self.categories.keys())[category_index - 1]
        category_slug: str = self.categories[category_name]
        return category_slug
    
    
    def parse_atb_markup(self, html_markup: str) -> list[dict]:
        soup = BeautifulSoup(html_markup, "lxml")
        products_list = []
        
        cards = soup.find_all("article", class_="catalog-item")
        
        for card in cards:
            try:
                cart_btn = card.find("div", class_="b-addToCart")
                if not cart_btn:
                    continue
                    
                product_id = int(cart_btn.get("data-itemid"))
                brand = cart_btn.get("data-brand")
                category = cart_btn.get("data-category")
                
                title_tag = card.find("div", class_="catalog-item__title")
                title = title_tag.get_text(strip=True) if title_tag else "Без названия"
                link_tag = title_tag.find("a")
                href = link_tag.get("href")
                
                national_cashback = card.find('span', attrs={"data-tippy-content": "Національний Кешбек"})
                
                img_tag = card.find("img", class_="catalog-item__img")
                image_url = img_tag.get("src") if img_tag else None
                
                price_tag = card.find("data", class_="product-price__top")
                price = float(price_tag.get("value")) if price_tag else 0.0
                
                product_data = {
                    "id": product_id,
                    "title": title,
                    "brand": brand,
                    "national_cashback": national_cashback is not None,
                    "category": category,
                    "price": price, 
                    "image_url": image_url,
                    "product_link": urljoin(self.base_url, href)
                }
                
                products_list.append(product_data)
                
            except Exception as e:
                
                print(f"Ошибка при парсинге карточки товара: {e}")
                continue
                
        return products_list
            
    def search_product(self, query: str):        
        with httpx.Client() as client:
            url = f"https://api.multisearch.io/"
            params = {
                "id": "11280",
                "key": "63a6d0a760fd2d0562c4061b78e64754",
                "lang": "uk",
                "location": "498",
                "m": "1779284677057",
                "q": "idb9je",
                "query": query,
                "s": "mini",
                "uid": "de33cf30-d4ad-4486-ae87-1cbd6237ed58"
            }
            r = client.get(url, headers=self._get_headers(), params=params)
            
            return r.json()
        
    def parse_category(self, category_slug: str, start_page: int = 1) -> list[dict]:
        with httpx.Client() as client:
            all_products = []                                                   
            url = urljoin(self.base_url_catalog, category_slug)
            
            current_page = start_page
            r = client.get(url, headers=self._get_headers(), params={"page": current_page})
            
            response = r.json()
            markup = response["markup"]
            page_count = response["page_count"]
            
            all_products.extend(self.parse_atb_markup(markup))
            
            while current_page < page_count:
                current_page += 1
                r = client.get(url, headers=self._get_headers(), params={"page": current_page})      
                response = r.json()      
                markup = response["markup"]
                all_products.extend(self.parse_atb_markup(markup))
                
            return all_products

class AsyncATBparser(ATBparser):
    def __init__(self):
        super().__init__()
    
    async def fetch_page(self, client: httpx.AsyncClient, url: str, page: int) -> tuple[int, list[dict]]:
        try:
            headers = self._get_headers()
            r = await client.get(url, headers=headers, params={"page": page})
            response = r.json()
            markup = response.get("markup", "")
            page_count = response.get("page_count", 1)
            
            products = self.parse_atb_markup(markup)
            return page_count, products
        except Exception as e:
            print(f"Ошибка при скачивании страницы {page}: {e}")
            return 1, []
            
    async def parse_category(self, category_slug: str, page: int = 1) -> list[dict[str, str]]:
        all_products = []
        url = urljoin(self.base_url_catalog, category_slug)
        async with httpx.AsyncClient() as client:
            
            page_count, first_page_products = await self.fetch_page(client, url, page=1)
            all_products.extend(first_page_products)
            
            if page_count > 1:

                tasks = []
                for page in range(2, page_count + 1):
                    tasks.append(self.fetch_page(client, url, page))
                
                results = await asyncio.gather(*tasks)
                
                for _, page_products in results:
                    all_products.extend(page_products)
                    
        return all_products
