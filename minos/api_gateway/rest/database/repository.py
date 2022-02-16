from sqlalchemy import (
    or_,
)
from sqlalchemy.orm import (
    sessionmaker,
)

from .models import (
    AuthRule,
    AuthRuleDTO,
    AutzRule,
    AutzRuleDTO,
)


class Repository:
    def __init__(self, engine):
        self.engine = engine
        self.s = sessionmaker(bind=engine)
        self.session = self.s()

    def create_auth_rule(self, record: AuthRule):
        self.session.add(record)
        self.session.commit()
        return record.to_serializable_dict()

    def create_autz_rule(self, record: AutzRule):
        self.session.add(record)
        self.session.commit()
        return record.to_serializable_dict()

    def get_auth_rules(self):
        r = self.session.query(AuthRule).all()

        records = list()
        for record in r:
            records.append(AuthRuleDTO(record).__dict__)
        return records

    def get_autz_rules(self):
        r = self.session.query(AutzRule).all()

        records = list()
        for record in r:
            records.append(AutzRuleDTO(record).__dict__)
        return records

    def update_auth_rule(self, id: int, **kwargs):
        self.session.query(AuthRule).filter(AuthRule.id == id).update(kwargs)
        self.session.commit()

    def update_autz_rule(self, id: int, **kwargs):
        self.session.query(AutzRule).filter(AutzRule.id == id).update(kwargs)
        self.session.commit()

    def delete_auth_rule(self, id: int):
        self.session.query(AuthRule).filter(AuthRule.id == id).delete()
        self.session.commit()

    def delete_autz_rule(self, id: int):
        self.session.query(AutzRule).filter(AutzRule.id == id).delete()
        self.session.commit()

    def get_auth_rule_by_service(self, service: str):
        r = self.session.query(AuthRule).filter(or_(AuthRule.service == service, AuthRule.service == "*")).all()

        records = list()
        for record in r:
            records.append(AuthRuleDTO(record))
        return records

    def get_autz_rule_by_service(self, service: str):
        r = self.session.query(AutzRule).filter(or_(AutzRule.service == service, AutzRule.service == "*")).all()

        records = list()
        for record in r:
            records.append(AutzRuleDTO(record))
        return records
