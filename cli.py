"""Command-line interface for ATB Market parser."""
import click
import asyncio
from parsers import AsyncATBparser
from database import init_db, save_products_to_db
import time
import json 

@click.group()
def cli():
    """ATB Market parser CLI"""
    pass

@cli.command()
@click.option('--category', '-c', required=True, help='Category slug (e.g., economy)')
@click.option('--save-db', is_flag=True, help='Save to database')
@click.option('--delay', '-d', type=float, default=0.3, help='Delay between requests in seconds (default: 0.3)')
def parse(category, save_db, delay):
    """Parse products from a specific category"""
    async def _parse():
        parser = AsyncATBparser(rate_limit_delay=delay)

        category_slug = parser.search_category(category)
        if not category_slug:
            click.echo(f"❌ Ошибка: Категория '{category}' не найдена!")
            return

        if save_db:
            await init_db()

        click.echo(f"🔍 Парсинг категории: {category_slug}")
        start_time = time.time()

        products = await parser.parse_category(category_slug)

        elapsed = time.time() - start_time
        click.echo(f"\n✅ Парсинг завершен за {elapsed:.2f} сек")
        click.echo(f"📦 Найдено товаров: {len(products)}")

        if products:
            prices = [p['price'] for p in products]
            click.echo(f"💰 Средняя цена: {sum(prices)/len(prices):.2f} грн")
            click.echo(f"💸 Мин: {min(prices):.2f} грн | Макс: {max(prices):.2f} грн")

        if save_db and products:
            click.echo("\n💾 Сохраняю в базу данных...")
            await save_products_to_db(products)
            click.echo("✅ Данные сохранены")

    asyncio.run(_parse())
        
@cli.command()
@click.option('--query', '-q', required=True, help='Search query (e.g Milk)')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def search(query, output_json):
    """Search for products by name"""
    def _search():
        parser = AsyncATBparser()
        result = parser.roug_search_product(query)

        if output_json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result and 'results' in result and 'item_groups' in result['results']:
                click.echo(f"\nЗнайдено товарів: {result['total']}\n")
                for group in result['results']['item_groups']:
                    cat = group['category']
                    click.echo(f"📦 {cat['name']} ({cat['count']} товарів)")
                    for item in group['items']:
                        price_str = f"{item['price']} {item['currency']}"
                        if 'oldprice' in item:
                            price_str = f"{item['oldprice']} → {price_str}"
                        click.echo(f"  • {item['name']}")
                        click.echo(f"    {price_str} | {item['brand']}")
                    click.echo()

    _search()

@cli.command()
def categories():
    """List all available categories"""
    parser = AsyncATBparser()
    click.echo("\nДоступные категории:\n")
    for cat_name, cat_slug in parser.categories.items():
        click.echo(f"  {cat_name:30} → {cat_slug}")
if __name__ == "__main__":
    cli()