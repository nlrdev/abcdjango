from core.util import Callable


class DefaultAjax(Callable):
    @staticmethod
    def index[dict](request: dict):
        return {
            "index": "index",
        }

