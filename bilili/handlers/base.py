from typing import List

noop = lambda *args, **kwargs: None


class Handler:
    """事件处理器"""

    def __init__(self, events: List[str] = []):
        """初始化事件处理器

        Args:
            events (List[str], optional): 事件名称. Defaults to [].
        """
        self.events = events
        for event in self.events:
            setattr(self, event, noop)

    def on(self, event: str):
        """事件添加装饰器

        Args:
            event (str): 事件名称

        Returns:
            function: 在发生 event 后的触发事件，会自动注册在 handler 上
        """
        assert event in self.events

        def on_event(func):

            setattr(self, event, func)

        return on_event
