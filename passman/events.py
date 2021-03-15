from .pubsub import Topic


class SimpleMsg(Topic):
    def __init__(self, msg):
        self.msg = msg

class PathEvent(SimpleMsg):
    def __init__(self, msg, path):
        super().__init__(msg)
        self.path = path

class ErrorEvent(PathEvent):
    pass

class WriteEvent(PathEvent):
    pass
