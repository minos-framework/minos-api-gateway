from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Column,
    Integer,
    Sequence,
    String,
)
from sqlalchemy.ext.declarative import (
    declarative_base,
)

Base = declarative_base()


class AuthRule(Base):
    __tablename__ = "auth_rules"
    id = Column(Integer, Sequence("item_id_seq"), nullable=False)
    service = Column(String, primary_key=True, nullable=False)
    rule = Column(String, primary_key=True, nullable=False)
    methods = Column(JSON)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    def __repr__(self):
        return (
            "<AuthRule(id='{}', service='{}', rule='{}',"
            "methods={}, created_at={}, updated_at={})>".format(  # pragma: no cover
                self.id, self.service, self.rule, self.methods, self.created_at, self.updated_at
            )
        )

    def to_serializable_dict(self):
        return {
            "id": self.id,
            "service": self.service,
            "rule": self.rule,
            "methods": self.methods,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


class AuthRuleDTO:
    id: int
    service: str
    rule: str
    methods: list
    created_at: str
    updated_at: str

    def __init__(self, model: AuthRule):
        self.id = model.id
        self.service = model.service
        self.rule = model.rule
        self.methods = model.methods
        self.created_at = str(model.created_at)
        self.updated_at = str(model.updated_at)
