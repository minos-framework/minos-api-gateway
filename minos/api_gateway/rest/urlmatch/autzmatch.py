from ..database.models import (
    AutzRuleDTO,
)
from .urlmatch import (
    UrlMatch,
)


class AutzMatch(UrlMatch):
    @staticmethod
    def match(url: str, role: int, method: str, records: list[AutzRuleDTO]) -> bool:
        for record in records:
            if AutzMatch.urlmatch(record.rule, url):
                if record.roles is None:  # pragma: no cover
                    return True
                else:
                    if role in record.roles or "*" in record.roles:
                        return True

        return False
