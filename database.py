"""Database models and operations for ATB product price tracking."""
import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy import ForeignKey, BigInteger, Float, String, DateTime, Boolean, select, and_, or_, func
from parsers import CONFIG
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

db_type = CONFIG.get("database_type", "sqlite").lower()

if db_type == "postgres":
    user = CONFIG.get("db_user")
    password = CONFIG.get("db_password")
    host = CONFIG.get("db_host")
    port = CONFIG.get("db_port")
    db_name = CONFIG.get("db_name")
    DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
else:
    DATABASE_URL = "sqlite+aiosqlite:///./atb_prices.db"
    
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass

class Product(Base):
    """Product model - stores product metadata without prices."""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    national_cashback: Mapped[bool] = mapped_column(Boolean, default=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    product_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    prices: Mapped[list["PriceHistory"]] = relationship(back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    """Price history model - tracks price changes over time."""
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    price: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    product: Mapped["Product"] = relationship(back_populates="prices")
    
async def init_db():
    """Create database tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_all_products():
    """Fetch all products without price history."""
    async with async_session() as session:
        query = select(Product)

        result = await session.execute(query)

        products = result.scalars().all()

        for p in products:
            print(f"Товар: {p.title}, Цена: {p.price}")

        return products

async def get_all_products_with_prices():
    """Fetch all products with their complete price history."""
    async with async_session() as session:
        query = select(Product).options(selectinload(Product.prices))

        result = await session.execute(query)
        products = result.scalars().all()

        for p in products:
            print(f"Товар: {p.title}")
            for price_entry in p.prices:
                print(f"  - Цена на дату {price_entry.updated_at}: {price_entry.price} грн")

        return products

async def save_products_to_db(products_list: list[dict]):
    """UPSERT products and append new price history entries."""
    if not products_list:
        return

    async with async_session() as session:
        # Bulk fetch all existing products
        product_ids = [p["id"] for p in products_list]
        existing_query = select(Product).where(Product.id.in_(product_ids))
        existing_result = await session.execute(existing_query)
        existing_map = {p.id: p for p in existing_result.scalars()}

        # Bulk fetch last prices for all products
        last_prices_query = (
            select(PriceHistory)
            .where(PriceHistory.product_id.in_(product_ids))
            .order_by(PriceHistory.product_id, PriceHistory.updated_at.desc())
        )
        last_prices_result = await session.execute(last_prices_query)
        all_prices = last_prices_result.scalars().all()

        # Group by product_id and take first (most recent) for each
        last_prices_map = {}
        for price in all_prices:
            if price.product_id not in last_prices_map:
                last_prices_map[price.product_id] = price

        for data in products_list:
            existing_product = existing_map.get(data["id"])

            if existing_product:
                existing_product.title = data["title"]
                existing_product.brand = data["brand"]
                existing_product.category = data["category"]
                existing_product.national_cashback = data["national_cashback"]
                existing_product.image_url = data["image_url"]
                existing_product.product_link = data["product_link"]
            else:
                existing_product = Product(
                    id=data["id"],
                    title=data["title"],
                    brand=data["brand"],
                    category=data["category"],
                    national_cashback=data["national_cashback"],
                    image_url=data["image_url"],
                    product_link=data["product_link"]
                )
                session.add(existing_product)

            # Check if price changed from last entry
            last_price = last_prices_map.get(data["id"])

            # Only add price history if price changed or first time
            if not last_price or last_price.price != data["price"]:
                new_price = PriceHistory(
                    product_id=data["id"],
                    price=data["price"]
                )
                session.add(new_price)

        await session.commit()
    logger.info(f"[БД] Успешно обработано товаров: {len(products_list)}")