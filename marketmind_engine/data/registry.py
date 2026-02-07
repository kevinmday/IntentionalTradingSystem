from marketmind_engine.data.stub import StubDataProvider

_ACTIVE_PROVIDER = StubDataProvider()


def get_provider():
    return _ACTIVE_PROVIDER


def set_provider(provider):
    global _ACTIVE_PROVIDER
    _ACTIVE_PROVIDER = provider