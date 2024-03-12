from model import Batch, OrderLine, allocate, OutOfStock
from datetime import date, timedelta
import pytest
def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=date.today())

    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=date.today())
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=date.today() + timedelta(days=30))
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=date.today() + timedelta(days=90))

    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "RETRO-CLOCK", 100, eta=date.today())

    line = OrderLine("oref", "RETRO-CLOCK", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.ref

def test_raises_out_of_stock_exception_if_cannot_allocate():
    today = date.today()
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])