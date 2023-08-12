from datetime import date, timedelta
import pytest

from furniture.model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


@pytest.fixture
def batch():
    def _get(sku, batch_qty, eta=date.today()):
        return Batch("batch-001", sku, batch_qty, eta=eta)

    return _get


@pytest.fixture
def order_line():
    def _get(sku, line_qty):
        return OrderLine('order-123', sku, line_qty)

    return _get


def test_allocation_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "small-table", qty=20, eta=date.today())
    line = OrderLine('order-ref', 'small-table', 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required(batch, order_line):
    large_batch = batch("ELEGANT-LAMP", 20)
    small_line = order_line("ELEGANT-LAMP", 2)

    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required(batch, order_line):
    small_batch = batch("ELEGANT-LAMP", 10)
    large_line = order_line("ELEGANT-LAMP", 20)

    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_requried(batch, order_line):
    batch = batch("ELEGANT-LAMP", 2)
    line = order_line("ELEGANT-LAMP", 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match(batch, order_line):
    batch = batch("ELEGANT-LAMP", 2)
    line = order_line("RED-CHAIR", 1)

    assert batch.can_allocate(line) is False


def test_allocation_is_idempotent(batch, order_line):
    batch = batch("SOME-DESK", 20)
    line = order_line("SOME-DESK", 2)

    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18


def test_prefers_current_stock_batches_to_shipments(batch, order_line):
    in_stock_batch = batch("RETRO-DESK", 100, eta=None)
    shipment_batch = batch("RETRO-DESK", 100, eta=tomorrow)
    line = order_line("RETRO-DESK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [earliest, medium, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])
