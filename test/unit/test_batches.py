from app.domain.model import Batch, OrderLine
from datetime import date, timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_bach_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch = Batch("batch-001", "SMALL-TABLE", qty=1, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    assert batch.can_allocate(line) == False


def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch("batch-001", "SMALL-TABLE", qty=2, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 1)

    assert batch.can_allocate(line) == True


def test_can_allocate_if_available_equal_to_required():
    batch = Batch("batch-001", "SMALL-TABLE", qty=1, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 1)

    assert batch.can_allocate(line) == True

def test_can_only_deallocate_allocated_lines():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    unallocated = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.deallocate(unallocated)

    assert batch.available_quantity == 20

def test_allocation_is_idempotent():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18