from core.util import Callable


class DefaultContext(Callable):
    @staticmethod
    def index[dict](view: object):
        return {
            "default": "default",
        }
