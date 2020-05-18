from typing import List, Callable


class EventArgs:
    def __int__(self):
        pass


class Event:
    def __init__(self):
        self.subscribers: List[Callable[[object, EventArgs], None]] = []

    def subscribe(self, f: Callable[[object, EventArgs], None]):
        self.subscribers.append(f)

    def trigger(self, obj: object, args: EventArgs):
        for f in self.subscribers:
            f(obj, args)
