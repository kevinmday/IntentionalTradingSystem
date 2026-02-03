from marketmind_engine.data.stub import StubDataSource

_ACTIVE_SOURCE = StubDataSource()


def get_data_source():
    return _ACTIVE_SOURCE


def set_data_source(source):
    global _ACTIVE_SOURCE
    _ACTIVE_SOURCE = source
