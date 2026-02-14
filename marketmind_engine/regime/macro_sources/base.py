from typing import Protocol, Dict


class MacroInputSource(Protocol):
    """
    Deterministic macro input provider.
    """

    def collect(self) -> Dict:
        ...

    @property
    def source_type(self) -> str:
        ...
