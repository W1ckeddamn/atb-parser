"""Main script for testing ATB parser functionality."""
from parsers import AsyncATBparser
from database import init_db, save_products_to_db
import time
import asyncio


async def main():
    """Example usage of parser and database functions."""
    await init_db()

    parser = AsyncATBparser()

    category_slug = parser.search_category("еконо")
    print(category_slug)


if __name__ == "__main__":
    asyncio.run(main())