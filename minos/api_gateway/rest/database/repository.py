from sqlalchemy.orm import (
    sessionmaker,
)
from .models import (
    AuthRule,
)


class Repository:
    def __init__(self, engine):
        self.engine = engine
        self.s = sessionmaker(bind=engine)
        self.session = self.s()

    def create(self, record: AuthRule):
        self.session.add(record)
        self.session.commit()
        return record.to_serializable_dict()

    def get(self, id: int):
        r = self.session.query(AuthRule).filter(AuthRule.id == id).first()
        return repr(r)
