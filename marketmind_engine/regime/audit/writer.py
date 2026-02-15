import json
from pathlib import Path
from .schema import RegimeTransitionEvent


class RegimeAuditWriter:
    def __init__(self, file_path: Path):
        self._file_path = file_path
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: RegimeTransitionEvent) -> None:
        with self._file_path.open('a', encoding='utf-8') as f:
            json.dump(event.to_dict(), f)
            f.write('\n')
