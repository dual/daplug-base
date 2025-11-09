class RecordingPublisher:
    """Captures SNS publish invocations for assertions."""

    def __init__(self):
        self.calls = []

    def publish(self, **kwargs):
        self.calls.append(kwargs)


class FakeSNSClient:
    """SNS client stub that records payloads and can raise on demand."""

    def __init__(self, should_raise=False):
        self.should_raise = should_raise
        self.published = []

    def publish(self, **kwargs):
        self.published.append(kwargs)
        if self.should_raise:
            raise ValueError("publish boom")


class RecordingLogger:
    """Logger stub capturing log payloads."""

    def __init__(self):
        self.entries = []

    def log(self, **kwargs):
        self.entries.append(kwargs)
