import re
from moments.moment import Moment, Occurrence
from typing import Union


class Snapshot(Moment):
    """A class to capture a moment at specific time."""

    snapshot_id: str
    previous_snapshot_id: str
    timestamp: str

    def __init__(
        self: "Snapshot",
        snapshot_id: str,
        occurrences: list[Occurrence],
        previous_snapshot_id: str,
        timestamp: str,
    ):
        super().__init__(occurrences)
        self.snapshot_id = snapshot_id
        self.previous_snapshot_id = previous_snapshot_id
        self.timestamp = timestamp

    @classmethod
    def parse(cls, obj: Union[str, dict]) -> "Snapshot":
        if isinstance(obj, dict):
            snapshot_id = obj["snapshot_id"]
            previous_snapshot_id = obj.get("previous_snapshot_id", None)
            timestamp = obj.get("timestamp", None)
            occurrences = super()._parse_dict(obj)
        elif isinstance(obj, str):
            lines = str(obj).splitlines()
            for line in lines:
                if line.startswith("#"):
                    # Snapshot Id
                    if match := re.match(r"^#\s+Snapshot\s*[ID|id|Id]:\s+(.+)$", line):
                        snapshot_id = match.group(1)
                    else:
                        snapshot_id = None

                    # Previous Snapshot Id
                    if match := re.match(
                        r"^#\s+Previous\sSnapshot\s*[ID|id|Id]:\s+(.+)$", line
                    ):
                        previous_snapshot_id = match.group(1)
                    else:
                        previous_snapshot_id = None

                    # Timestamp
                    if match := re.match(r"^#\s+Timestamp:\s+(.+)$", line):
                        timestamp = match.group(1)
                    else:
                        timestamp = None
            occurrences = super()._parse_text(obj)
        return cls(
            snapshot_id=snapshot_id,
            occurrences=occurrences,
            previous_snapshot_id=previous_snapshot_id,
            timestamp=timestamp,
        )

    def __str__(self) -> str:
        moment_str = ""
        moment_str += f"# Snapshot ID: {self.snapshot_id}"
        if self.previous_snapshot_id:
            moment_str += f"# Previous Snapshot ID: {self.previous_snapshot_id}"
        if self.timestamp:
            moment_str += f"# Timestamp: {self.timestamp}"
        return moment_str + super().__str__()
