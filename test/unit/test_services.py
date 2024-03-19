import pytest
import datetime

from app.domain import model
from app.domain.model import allocate
from app.adapters.repository import AbstractRepository
from app.service_layer import services


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([model.Batch(ref, sku, qty, eta)])

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)


def test_returns_allocation():
    repo = FakeRepository.for_batch("batch1", "SMALL-FORK", 100, eta=None)

    result = services.allocate("order1", "SMALL-FORK", 10, repo, FakeSession())

    assert result == "batch1"


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "SMALL-FORK", 100, None, repo, session)
    result = services.allocate("order1", "SMALL-FORK", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "NONEXISTENTSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("order1", "NONEXISTENTSKU", 10, repo, session)


def test_commits():
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


# 도메인 계층 테스트
def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)

    line = model.OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_warehouse_batches_to_shipments():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, None, repo, session)
    services.add_batch("shipment-batch", "RETRO-CLOCK", 100, tomorrow, repo, session)

    services.allocate("order1", "RETRO-CLOCK", 10, repo, session)

    in_stock_batch = repo.get("in-stock-batch")
    shipment_batch = repo.get("shipment-batch")
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
