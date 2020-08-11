noop = lambda *args, **kwargs: None


class Handler():
    def __init__(self, events=[]):
        self.events = events
        for event in self.events:
            setattr(self, event, noop)

    def on(self, event, **params):
        assert event in self.events

        def on_event(func):
            def new_func(*args, **kwargs):
                return func(*args, **kwargs, **params)
            setattr(self, event, new_func)
        return on_event
