from sqlalchemy.orm import (
    sessionmaker,
)

from .models import (
    AuthRule,
    AuthRuleDTO,
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

    def get_all(self):
        r = self.session.query(AuthRule).all()

        records = list()
        for record in r:
            records.append(AuthRuleDTO(record).__dict__)
        return records

    def get(self, id: int):
        r = self.session.query(AuthRule).filter(AuthRule.id == id).first()
        return AuthRuleDTO(r).__dict__

    def update(self, id: int, **kwargs):
        self.session.query(AuthRule).filter(AuthRule.id == id).filter(AuthRule.id == id).update(kwargs)
        self.session.commit()

    def delete(self, id: int):
        self.session.query(AuthRule).filter(AuthRule.id == id).delete()
        self.session.commit()
