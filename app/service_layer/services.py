from app.domain import model
from app.domain.model import OrderLine
from app.adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    if not is_valid_sku(line.sku, repo.list()):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, repo.list())
    session.commit()
    return batchref
