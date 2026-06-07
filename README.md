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

# Install dependencies
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
    parser = AsyncATBparser(rate_limit_delay=0.3)
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

## Database

Project includes SQLAlchemy async ORM with price history tracking.

### Schema

**Product** table:
- `id` (BigInt, PK) — ATB product ID
- `title`, `brand`, `category` — product metadata
- `national_cashback` (Boolean) — cashback eligibility
- `image_url`, `product_link` — media links

**PriceHistory** table:
- `id` (autoincrement PK)
- `product_id` (FK → products.id)
- `price` (Float)
- `updated_at` (DateTime, UTC)

### Configuration

Edit `config.json` to switch database:

```json
{
  "database_type": "sqlite",  // or "postgres"
  "db_host": "localhost",
  "db_port": "5432",
  "db_name": "atb_prices",
  "db_user": "postgres",
  "db_password": "password"
}
```

SQLite: `sqlite+aiosqlite:///./atb_prices.db` (default)  
PostgreSQL: `postgresql+asyncpg://user:pass@host:port/db`

### Usage

```python
from database import init_db, save_products_to_db, get_all_products_with_prices

# Initialize tables
await init_db()

# Save products (UPSERT + price history)
await save_products_to_db(products_list)

# Query with price history
products = await get_all_products_with_prices()
```

## Dependencies

- `httpx` — HTTP client with async support
- `beautifulsoup4` + `lxml` — HTML parsing
- `fake-useragent` — User-Agent rotation
- `sqlalchemy` — Async ORM
- `aiosqlite` — SQLite async driver
- `asyncpg` — PostgreSQL async driver

## CLI Interface

### Commands

#### List categories
```bash
uv run python cli.py categories
```

#### Parse category
```bash
# Basic parsing
uv run python cli.py parse -c economy

# Save to database
uv run python cli.py parse -c economy --save-db

# Custom rate limiting (default: 0.3s)
uv run python cli.py parse -c economy --delay 0.5

# Fast mode (higher risk of blocking)
uv run python cli.py parse -c economy --delay 0.1 --save-db
```

#### Search products
```bash
# Formatted output
uv run python cli.py search -q "молоко"

# JSON output
uv run python cli.py search -q "хліб" --json
```

### Output Example

```
🔍 Парсинг категории: economy

✅ Парсинг завершен за 2.32 сек
📦 Найдено товаров: 187
💰 Средняя цена: 80.10 грн
💸 Мин: 9.90 грн | Макс: 591.90 грн

💾 Сохраняю в базу данных...
✅ Данные сохранены
```

## Features

### Rate Limiting
Configurable delay between requests to avoid blocking:
- **0.1s** - fast, higher risk
- **0.3s** - default, balanced
- **0.5-1.0s** - conservative, for large batches

### Smart Price Tracking
- Only saves price history when price actually changes
- Bulk database operations (2 queries instead of N×2)
- Reduces storage and improves performance

### Database Optimizations
- Bulk product fetch in single query
- Bulk price history fetch with grouping
- UPSERT logic for products
- Price change detection before insert

## Status

✅ Category parser (sync/async)  
✅ Product search  
✅ Database storage (SQLite/PostgreSQL)  
✅ Price history tracking  
✅ CLI interface  
✅ Rate limiting  
✅ Bulk database operations  
✅ Price change detection

## License

MIT
