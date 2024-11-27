from core.util import Callable


class DefaultContext(Callable):
    @staticmethod
    def index[dict](request: dict):
        return {
            "default": "default",
        }
