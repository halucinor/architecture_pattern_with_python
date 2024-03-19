import pytest
import datetime

from app.domain import model
from app.domain.model import allocate
from app.adapters.repository import AbstractRepository
from app.service_layer import services, unit_of_work


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([model.Batch(ref, sku, qty, eta)])

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.ref == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "SMALL-FORK", 100, None, uow)
    assert uow.batches.get("batch1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "SMALL-FORK", 100, None, uow)
    result = services.allocate("order1", "SMALL-FORK", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    uow.batches.add(model.Batch("batch1", "SMALL-FORK", 100, eta=None))

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("order1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    uow.batches.add(model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None))

    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True

def test_prefers_current_stock_batches_to_shipments():
    uow = FakeUnitOfWork()
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)

    uow.batches.add(in_stock_batch)
    uow.batches.add(shipment_batch)

    services.allocate("order1", "RETRO-CLOCK", 10, uow)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
