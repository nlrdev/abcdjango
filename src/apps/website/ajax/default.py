from core.util import Callable


class DefaultAjax(Callable):
    @staticmethod
    def index(view: object) -> dict:
        return {
            "index": "index",
        }

