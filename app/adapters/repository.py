import abc
from app.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, entity):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, entity_id):
        raise NotImplementedError

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, entity):
        self.session.add(entity)

    def get(self, batch_id):
        return self.session.query(model.Batch).filter_by(ref=batch_id).one()

    def list(self):
        return self.session.query(model.Batch).all()
