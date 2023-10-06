# Python imports
from collections import namedtuple
from datetime import datetime
from os import getenv
import enum
from typing import Optional, Sequence

# Library imports
from sqlalchemy import create_engine, URL, text
from sqlalchemy import String, BigInteger, Enum, DateTime, Float, ForeignKey
from sqlalchemy import select, insert
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


__all__ = (
    'Product',
    'ProductDiscount',
    'DiscountCard',
    'Customer',
    'Manager',
    'Order',
    'OrderHistory',
    'OrderProduct',
    'db_init',
    'OrderStatus',
    'find_by_id',
    'create_customer'
)

from settings import Settings

SCHEMA = 'testpelz'


class OrderStatus(enum.Enum):
    CART = enum.auto()
    SETTING = enum.auto()
    PAYING = enum.auto()
    PAY_CHECK = enum.auto()
    WAITING_FOR_TAKE = enum.auto()


class Base(DeclarativeBase):
    __table_args__ = {'schema': SCHEMA}


class Manager(Base):
    __tablename__ = 'Manager'
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=True)


class Customer(Base):
    __tablename__ = 'Customer'
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=True)
    discount_card: Mapped[Optional["DiscountCard"]] = relationship(
        uselist=False, back_populates='customer', cascade='delete, delete-orphan'
    )
    orders_active: Mapped[list['Order']] = relationship(back_populates='customer')
    orders_old: Mapped[list['OrderHistory']] = relationship(back_populates='customer')

    CART_PRODUCT = namedtuple('Cart', (
        'order_id', 'product_id', 'product_name',
        'product_amount', 'product_cost', 'product_in_cart_amount'
    ))

    def get_cart(self, session: Session) -> list[CART_PRODUCT]:
        cart_sql = text(f"""
            SELECT
                o.id AS order_id,
                p.id AS product_id,
                p.name AS product_name,
                p.amount AS product_amount,
                p.cost AS product_cost,
                op.amount AS product_in_cart_amount
            FROM {SCHEMA}.OrderProduct as op
            RIGHT JOIN {SCHEMA}.`Order` AS o ON (op.order_id = o.id)
            LEFT JOIN {SCHEMA}.Product as p ON (op.product_id = p.id);
        """)
        cart = session.execute(cart_sql).all()
        values = [self.CART_PRODUCT(*i) for i in cart]
        return values


class DiscountCard(Base):
    __tablename__ = 'DiscountCard'
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    discount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    customer_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.Customer.id"))
    customer: Mapped['Customer'] = relationship(back_populates="discount_card")


class OrderProduct(Base):
    __tablename__ = 'OrderProduct'
    order_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.Order.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.Product.id"), primary_key=True)
    amount: Mapped[int] = mapped_column(default=1)


class Order(Base):
    __tablename__ = 'Order'
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False)

    customer_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.Customer.id"))
    customer: Mapped['Customer'] = relationship(back_populates="orders_active")

    # def product_amount(self, session: Session, product: 'Product') -> int | None:
    #     cart = select(order_product).where(order_product.)


class OrderHistoryProduct(Base):
    __tablename__ = 'OrderHistoryProduct'
    order_id: Mapped[int] = mapped_column(ForeignKey(f'{SCHEMA}.OrderHistory.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(f'{SCHEMA}.Product.id'), primary_key=True)
    amount: Mapped[int] = mapped_column(default=1)


class OrderHistory(Base):
    __tablename__ = 'OrderHistory'
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    date_completed: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    customer_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.Customer.id"), index=True)
    customer: Mapped['Customer'] = relationship(back_populates="orders_old")

    @staticmethod
    async def list(offset, limit: int = 10, query: str = None) -> Sequence['Product']:
        engine = Settings['sql_engine']
        with Session(engine) as sess:
            stmt = select(Product).offset(offset).limit(limit)
            if query:
                stmt = stmt.filter(Product.name.like(f'%{query}%'))
            return sess.execute(stmt).scalars().all()


class Product(Base):
    __tablename__ = 'Product'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(String(4096))
    amount: Mapped[int] = mapped_column()
    cost: Mapped[int] = mapped_column(nullable=False)

    discount: Mapped['ProductDiscount'] = relationship(back_populates='product')

    @staticmethod
    async def list(offset: int, limit: int, query: str = None) -> Sequence['Product']:
        stmt = select(Product).offset(offset).limit(limit)
        if query is not None:
            stmt = stmt.where(Product.name.like(f'%{query}%'))
        with Session(Settings['sql_engine']) as sess:
            return sess.execute(stmt).scalars().all()


class ProductDiscount(Base):
    __tablename__ = 'ProductDiscount'
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    date_start: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    date_end: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

    product_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.Product.id"), index=True)
    product: Mapped['Product'] = relationship(back_populates="discount")


def db_init():
    host = getenv('DB_HOST')
    if host is None:
        raise RuntimeError("Can't get MySQL host")
    user = getenv('DB_USER')
    if user is None:
        raise RuntimeError("Can't get MySQL user")
    password = getenv('DB_PASSWORD')
    if password is None:
        raise RuntimeError("Can't get MySQL password")
    url = URL.create(
        "mysql+pymysql",
        host=host,
        username=user,
        password=password,
    )
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    Settings['sql_engine'] = engine


def find_by_id(id: int) -> Customer | Manager | None:
    engine = Settings['sql_engine']
    customer = select(Customer).where(Customer.id == id)
    manager = select(Manager).where(Manager.id == id)
    with Session(engine) as session:
        customer = session.execute(customer).scalar_one_or_none()
        if customer:
            return customer
        return session.execute(manager).scalar_one_or_none()


def create_customer(user_id: int) -> Customer:
    engine = Settings['sql_engine']
    customer = insert(Customer).values(id=user_id).returning(Customer)
    with Session(engine, autoflush=True) as session:
        result = session.scalar(customer)
        session.execute(text(f"""
            INSERT INTO {SCHEMA}.`Order` (status, customer_id)
            VALUES ('{OrderStatus.CART.name}', {user_id});
        """))
    return result
