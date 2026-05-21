from urllib.parse import urljoin
from bs4 import BeautifulSoup
import httpx
import time
from fake_useragent import UserAgent
import json

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
   
async def main(*args, **kwargs) -> None:
    parser = AsyncATBparser()
    category = parser.choose_category()
    
    
    
if __name__ == "__main__":
    asyncio.run(main())