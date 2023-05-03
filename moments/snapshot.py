import re
from moments.moment import Moment, Occurrence
from typing import Union


class Snapshot:
    """A class to capture a moment at specific time."""

    id: str
    previous_snapshot_id: str
    timestamp: str

    # pylint: disable=redefined-builtin
    def __init__(
        self: "Snapshot",
        id: str,
        moment: Moment,
        previous_snapshot_id: str,
        timestamp: str,
    ):
        self.id = id
        self.moment = moment
        self.previous_snapshot_id = previous_snapshot_id
        self.timestamp = timestamp

    @classmethod
    def parse(cls, obj: Union[str, dict]) -> "Snapshot":
        if isinstance(obj, dict):
            id = obj["id"]
            previous_snapshot_id = obj.get("previous_snapshot_id", None)
            timestamp = obj.get("timestamp", None)
            moment = Moment.parse(obj["moment"])
        elif isinstance(obj, str):
            lines = str(obj).splitlines()
            moment_text = ""
            for line in lines:
                if line.startswith("#"):
                    # Snapshot Id
                    if match := re.match(r"^#\s+Snapshot\s*[ID|id|Id]:\s+(.+)$", line):
                        id = match.group(1)
                    else:
                        id = None

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
                else:
                    moment_text += line + "\n"
            moment = Moment.parse(moment_text)
        return cls(
            id=id,
            moment=moment,
            previous_snapshot_id=previous_snapshot_id,
            timestamp=timestamp,
        )

    def __str__(self) -> str:
        to_str = ""
        to_str += f"# Snapshot ID: {self.id}"
        if self.previous_snapshot_id:
            to_str += f"# Previous Snapshot ID: {self.previous_snapshot_id}"
        if self.timestamp:
            to_str += f"# Timestamp: {self.timestamp}"
        return to_str + str(self.moment)
