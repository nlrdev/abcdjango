from core.util import Callable


class DefaultAjax(Callable):
    @staticmethod
    def index[dict](view: object):
        return {
            "index": "index",
        }

