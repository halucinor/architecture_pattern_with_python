from datetime import date
from app.domain import model
from app.domain.model import OrderLine
from app.adapters.repository import AbstractRepository
from app.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(ref: str, sku: str, qty: int, eta: date | None,
              uow: unit_of_work.AbstractUnitOfWork
              ):
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()


def allocate(order_id: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        if not is_valid_sku(sku, uow.batches.list()):
            raise InvalidSku(f"Invalid sku {sku}")

        line = OrderLine(order_id, sku, qty)
        batchref = model.allocate(line, uow.batches.list())
        uow.commit()

    return batchref

# def reallocate(line: OrderLine, uow: unit_of_work.AbstractUnitOfWork):
#     with uow:
#         batches = uow.batches.get(sku=line.sku)
