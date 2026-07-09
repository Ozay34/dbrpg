class EventBus:
    def __init__(self):
        self._listeners = []

    def subscribe(self, callback):
        self._listeners.append(callback)

    def unsubscribe(self, callback):
        self._listeners.remove(callback)

    def once(self, callback):
        def wrapper():
            callback()
            self._listeners.remove(callback)
        self._listeners.append(wrapper)

    def publish(self, *args, **kwargs):
        for callback in self._listeners:
            callback(*args, **kwargs)
