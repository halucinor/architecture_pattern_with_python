import pytest
from sqlalchemy import text
from app.domain import model
from app.service_layer import unit_of_work


def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        text('INSERT INTO batches (ref, sku, _purchased_quantity, eta)'
             'VALUES (:ref, :sku, :qty, :eta)'),
        dict(ref=ref, sku=sku, qty=qty, eta=eta)
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(
        text('SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku'),
        dict(orderid=orderid, sku=sku)
    )

    [[batchref]] = session.execute(
        text('SELECT b.ref FROM allocations AS a JOIN batches AS b ON batch_id=b.id '
             'WHERE a.orderline_id = :orderlineid'),
        dict(orderlineid=orderlineid)
    )
    return batchref


def test_uow_can_retrive_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch1', 'SMALL-FORK', 100, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        batch = uow.batches.get('batch1')
        line = model.OrderLine('o1', 'SMALL-FORK', 10)
        batch.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, 'o1', 'SMALL-FORK')
    assert batchref == 'batch1'


def test_rolls_back_uncommitted_work_by_default(session_factory):
    session = session_factory()
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, 'batch1', 'SMALL-FORK', 100, None)

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, 'batch2', 'SMALL-FORK', 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []
