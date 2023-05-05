import re
from moments.moment import Moment
from typing import Union
from copy import deepcopy
import yaml


class Snapshot:
    """A class to capture a moment at specific time."""

    id: str
    previous_snapshot_id: str
    timestamp: str
    annotation: dict

    # pylint: disable=redefined-builtin
    def __init__(
        self: "Snapshot",
        id: str,
        moment: Moment,
        previous_snapshot_id: str,
        timestamp: str,
        annotations: dict,
    ):
        self.id = id
        self.moment = moment
        self.previous_snapshot_id = previous_snapshot_id
        self.timestamp = timestamp
        self.annotations = annotations

    @classmethod
    def parse(cls, obj: Union[str, dict]) -> "Snapshot":
        if isinstance(obj, dict):
            id = obj["id"]
            previous_snapshot_id = obj.get("previous_snapshot_id", None)
            timestamp = obj.get("timestamp", None)
            moment = Moment.parse(obj["moment"])
            annotations = obj.get("annotations", None)
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

                    # Annotations
                    if match := re.match(r"^#\s+Annotations:\s+```(.+?)```$", line):
                        annotations = yaml.safe_load(match.group(1))
                    else:
                        annotations = None
            moment = Moment.parse(moment_text)
        return cls(
            id=id,
            moment=moment,
            previous_snapshot_id=previous_snapshot_id,
            timestamp=timestamp,
            annotations=annotations,
        )

    def __str__(self) -> str:
        to_str = ""
        to_str += f"# Snapshot ID: {self.id}\n"
        if self.previous_snapshot_id:
            to_str += f"# Previous Snapshot ID: {self.previous_snapshot_id}\n"
        if self.timestamp:
            to_str += f"# Timestamp: {self.timestamp}\n"
        if self.annotations:
            to_str += f"# Annotations: ```{yaml.dump(self.annotation, default_flow_style=False).strip()}```\n"
        return to_str + str(self.moment)

    def to_dict(self) -> dict:
        return deepcopy(
            {
                "id": self.id,
                "previous_snapshot_id": self.previous_snapshot_id,
                "timestamp": self.timestamp,
                "annotations": self.annotations,
                "moment": self.moment.to_dict(),
            }
        )
