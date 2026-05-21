# ATB Parser

Async web scraper for ATB Market (Ukrainian grocery chain).

## Features

- Parse products by category
- Sync and async modes
- Extract: ID, title, brand, price, image, category, cashback status
- Parallel page fetching (async mode)
- 27 product categories supported

## Installation

```bash
# Clone repository
git clone <repo-url>
cd atb_parser

# Install dependencies (uv)
uv sync

# Or via pip
pip install -r requirements.txt
```

## Usage

### Sync Parser

```python
from parsers import ATBparser

parser = ATBparser()

# Parse category
products = parser.parse_category("economy")

# Interactive category selection
category_slug = parser.choose_category()
products = parser.parse_category(category_slug)

# Search products
results = parser.search_product("milk")
```

### Async Parser

```python
import asyncio
from parsers import AsyncATBparser

async def main():
    parser = AsyncATBparser()
    products = await parser.parse_category("economy")
    print(f"Found {len(products)} products")

asyncio.run(main())
```

## Data Structure

Each product returns as dict:

```python
{
    "id": 12345,
    "title": "Milk 2.5%",
    "brand": "Galychyna",
    "category": "Dairy products",
    "price": 45.90,
    "image_url": "https://...",
    "product_link": "https://www.atbmarket.com/product/...",
    "national_cashback": True
}
```

## Categories

Available categories in `config.json`:

- Economy (`economy`)
- New products (`novetly`)
- 7-day sale (`388-aktsiya-7-dniv`)
- Vegetables and fruits (`287-ovochi-ta-frukti`)
- Groceries (`285-bakaliya`)
- Dairy and eggs (`molocni-produkti-ta-ajca`)
- Alcohol (`292-alkogol-i-tyutyun`)
- Soft drinks (`294-napoi-bezalkogol-ni`)
- Cheese (`siri`)
- Meat (`maso`)
- Confectionery (`299-konditers-ki-virobi`)
- Fish and seafood (`353-riba-i-moreprodukti`)
- Bakery (`325-khlibobulochni-virobi`)
- Frozen products (`322-zamorozheni-produkti`)
- Coffee, tea (`kava-caj`)
- Chips, snacks (`cipsi-sneki`)
- Sausages and deli (`360-kovbasa-i-m-yasni-delikatesi`)
- Baby food (`339-dityache-kharchuvannya`)
- Japanese cuisine (`415-yapons-ka-kukhnya`)
- Ready meals (`502-kulinariya`)
- Kids products (`373-tovari-dlya-ditey`)
- Household chemicals (`308-pobutova-khimiya-ta-neprodovol-chi-tovari`)
- Hygiene and cosmetics (`290-gigiena-i-kosmetika`)
- Home goods (`358-tovari-dlya-domu`)
- Pet supplies (`389-kantselyars-ki-tovari`)
- Tobacco products (`479-tyutyunovi-virobi`)
- Gift cards (`sertifikati-ta-platizni-kartki`)
- Stationery (`389-kantselyars-ki-tovari`)

## Configuration

Settings in `config.json`:

```json
{
  "base_url": "https://www.atbmarket.com/",
  "base_url_catalog": "https://www.atbmarket.com/catalog/load-more-products/",
  "categories": {
    "Економія": "economy",
    ...
  }
}
```

## Dependencies

- `httpx` — HTTP client with async support
- `beautifulsoup4` + `lxml` — HTML parsing
- `fake-useragent` — User-Agent rotation
- `sqlalchemy` + `alembic` — Database (WIP)

## Status

✅ Category parser (sync/async)  
✅ Product search  
⏳ CLI interface  
⏳ Database storage  
⏳ Rate limiting  

## License

MIT
