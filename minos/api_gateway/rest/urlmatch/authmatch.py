from ..database.models import (
    AuthRuleDTO,
)
from .urlmatch import (
    UrlMatch,
)


class AuthMatch(UrlMatch):
    @staticmethod
    def match(url: str, method: str, records: list[AuthRuleDTO]) -> bool:
        for record in records:
            if AuthMatch.urlmatch(record.rule, url):
                if record.methods is None:  # pragma: no cover
                    return True
                else:
                    if method in record.methods or "*" in record.methods:
                        return True
        return False
