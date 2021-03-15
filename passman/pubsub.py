from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor


class InlineExecutor:
    @staticmethod
    def submit(f, *a, **kw):
        f(*a, **kw)

    def shutdown(self, *_a, **_kw):
        pass


DEFAULT_WORKERS = 5


class PubSub:
    def __init__(self, *, max_workers=DEFAULT_WORKERS):
        self.topics = defaultdict(set)
        if max_workers > 0:
            self.executor = ThreadPoolExecutor(max_workers=5)
        else:
            self.executor = InlineExecutor()

    def subscribe(self, topic, f):
        """
        Subscribe the function/method ``f`` to ``topic``.
        """
        assert issubclass(topic, Topic)
        self.topics[topic].add(f)

    def publish(self, msg):
        """
        Publish ``**kwargs`` to ``topic``, calling all functions/methods
        subscribed to ``topic`` with the arguments specified in ``**kwargs``.
        """
        assert isinstance(msg, Topic)
        self.__publish(msg, msg.__class__)

    def __publish(self, msg, cls):
        for f in self.topics[cls]:
            self.executor.submit(f, msg)
        for cls in cls.__bases__:
            if cls is not object:
                self.__publish(msg, cls)

    def shutdown(self, *args, **kws):
        self.executor.shutdown(*args, **kws)


class Topic:
    def __repr__(self):
        return self.__class__.__name__ + "(" + str(self.__dict__) + ")"

    def ___str__(self):
        return str(self.__dict__)


pubsub = PubSub()
