from datetime import date
from app.domain import model
from app.domain.model import OrderLine
from app.adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(ref: str, sku: str, qty: int, eta: date | None,
              repo: AbstractRepository, session):
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(order_id: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    if not is_valid_sku(sku, repo.list()):
        raise InvalidSku(f"Invalid sku {sku}")
    line = OrderLine(order_id, sku, qty)
    batchref = model.allocate(line, repo.list())

    session.commit()
    return batchref
