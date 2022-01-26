from .urlmatch import UrlMatch


class AuthMatch(UrlMatch):
    @staticmethod
    def match(url: str, method: str, endpoints) -> bool:
        for endpoint in endpoints:
            if AuthMatch.urlmatch(endpoint.url, url):
                if endpoint.methods is None:
                    return True
                else:
                    if method in endpoint.methods:
                        return True
        return False
