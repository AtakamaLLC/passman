import os
import queue
import threading

from .pubsub import pubsub
from .events import ErrorEvent, WriteEvent


class QueueWriter(threading.Thread):
    class Quit:
        pass

    def __init__(self):
        super().__init__()
        self.q = queue.Queue()

    def write(self, path, data):
        self.q.put((path, data))

    def run(self):
        ent = self.q.get()
        while ent is not self.Quit:
            self.process(ent)
            ent = self.q.get()

    def __del__(self):
        """Never rely on this."""
        if hasattr(self, "q"):
            self.stop()

    def stop(self):
        self.q.put(self.Quit)

    @staticmethod
    def process(ent):
        path, data = ent
        try:
            with open(path + ".tmp", "w") as fh:
                fh.write(data)
            os.replace(path + ".tmp", path)
            msg = "Saved %s" % path
            pubsub.publish(WriteEvent(msg, path))
        except Exception as e:
            msg = "Unable to write to %s: %s" % (path, repr(e))
            pubsub.publish(ErrorEvent(msg, path))
