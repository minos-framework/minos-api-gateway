
from sqlalchemy import (
    TIMESTAMP,
    Column,
    Integer,
    String,
    JSON,
    Sequence,
)
from sqlalchemy.ext.declarative import (
    declarative_base,
)

Base = declarative_base()


class AuthRule(Base):
    __tablename__ = "auth_rules"
    id = Column(Integer, Sequence("item_id_seq"), primary_key=True, nullable=False)
    service = Column(String)
    rule = Column(String)
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

    def to_dict(self):
        return {"id": self.id, "service": self.service, "rule": self.rule,
            "methods": self.methods, "created_at": self.created_at, "updated_at": self.updated_at}

    def to_serializable_dict(self):
        return {"id": self.id, "service": self.service, "rule": self.rule,
            "methods": self.methods, "created_at": str(self.created_at), "updated_at": str(self.updated_at)}
