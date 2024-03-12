from sqlalchemy.orm import mapper, relationship
from sqlalchemy import MetaData, Column, Table, Integer, String, ForeignKey,Date
from sqlalchemy.orm import registry

from furniture import model

metadata = MetaData()
mapper_registry = registry()

order_lines = Table(
    'order_lines', mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("ref", String(255))
)

batches = Table(
    "batches",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    mapper_registry.map_imperatively(model.OrderLine, order_lines)
    mapper_registry.map_imperatively(model.Batch, batches)
