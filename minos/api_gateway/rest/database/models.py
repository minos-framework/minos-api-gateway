
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


class Endpoint(Base):
    __tablename__ = "endpoints"
    id = Column(Integer, Sequence("item_id_seq"), primary_key=True, nullable=False)
    endpoint = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    def __repr__(self):
        return (
            "<Authentication(uuid='{}', auth_type='{}',"
            "auth_uuid={}, created_at={}, updated_at={})>".format(  # pragma: no cover
                self.uuid, self.auth_type, self.auth_uuid, self.created_at, self.updated_at
            )
        )


class AuthorizedEdpoint(Base):
    __tablename__ = "authorized_endpoints"
    id = Column(Integer, Sequence("item_id_seq"), primary_key=True, nullable=False)
    methods = Column(JSON)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    def __repr__(self):
        return (
            "<Authentication(uuid='{}', auth_type='{}',"
            "auth_uuid={}, created_at={}, updated_at={})>".format(  # pragma: no cover
                self.uuid, self.auth_type, self.auth_uuid, self.created_at, self.updated_at
            )
        )
