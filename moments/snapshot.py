import re
from moments.moment import Moment
from pathlib import Path
from typing import Union, Optional, Dict, Any
from copy import deepcopy
import yaml
from parsimonious.grammar import Grammar

p = Path(__file__).with_name("snapshots_grammar.peg")
with p.open("r", encoding="utf-8") as f:
    GRAMMAR = Grammar(f.read())


def walk(node, snapshot_dict: dict):
    if node.expr_name == "MomentId":
        moment_id = ""
        for child in node.children:
            if child.expr_name == "uuid":
                moment_id = child.text
        snapshot_dict["moment_id"] = moment_id
    elif node.expr_name == "SnapshotId":
        snapshot_id = ""
        for child in node.children:
            if child.expr_name == "uuid":
                snapshot_id = child.text
        snapshot_dict["snapshot_id"] = snapshot_id
    elif node.expr_name == "PreviousSnapshotId":
        previous_snapshot_id = ""
        for child in node.children:
            if child.expr_name == "uuid":
                previous_snapshot_id = child.text
        snapshot_dict["previous_snapshot_id"] = previous_snapshot_id
    elif node.expr_name == "Timestamp":
        timestamp = ""
        for child in node.children:
            if child.expr_name == "iso8601_timestamp":
                timestamp = child.text
        snapshot_dict["timestamp"] = timestamp
    elif node.expr_name == "Annotations":
        annotations = ""
        for child in node.children:
            if child.expr_name == "ct_content":
                annotations = child.text
        snapshot_dict["annotations"] = annotations
    elif node.expr_name == "MomentLine":
        if "moment" not in snapshot_dict:
            snapshot_dict["moment"] = []
        for child in node.children:
            snapshot_dict["moment"].append(child.text)
    elif node.expr_name.strip():
        for child in node.children:
            walk(child, snapshot_dict)


class Snapshot:
    """A class to capture a moment at specific time."""

    moment_id: str
    snapshot_id: str
    previous_snapshot_id: Optional[str]
    timestamp: str
    annotation: dict

    # pylint: disable=redefined-builtin
    def __init__(
        self: "Snapshot",
        moment_id: str,
        snapshot_id: str,
        moment: Moment,
        previous_snapshot_id: Optional[str],
        timestamp: str,
        annotations: dict,
    ):
        self.moment_id = moment_id
        self.snapshot_id = snapshot_id
        self.moment = moment
        self.previous_snapshot_id = previous_snapshot_id
        self.timestamp = timestamp
        self.annotations = annotations

    @classmethod
    def parse(cls, obj: Union[str, dict]) -> "Snapshot":
        if isinstance(obj, dict):
            moment_id = obj["moment_id"]
            snapshot_id = obj["snapshot_id"]
            previous_snapshot_id = obj.get("previous_snapshot_id", None)
            timestamp = obj.get("timestamp", None)
            moment = Moment.parse(obj["moment"])
            annotations = obj.get("annotations", None)
        elif isinstance(obj, str):
            snapshot_dict: Dict[str, Any] = {}
            parsed = GRAMMAR.parse(obj)
            walk(parsed, snapshot_dict)
            moment_id = snapshot_dict["moment_id"]
            snapshot_id = snapshot_dict["snapshot_id"]
            previous_snapshot_id = snapshot_dict.get("previous_snapshot_id", None)
            timestamp = snapshot_dict["timestamp"]
            if "annotations" in snapshot_dict:
                annotations = yaml.safe_load(snapshot_dict["annotations"])
            moment = Moment.parse("".join(snapshot_dict["moment"]))
        return cls(
            moment_id=moment_id,
            snapshot_id=snapshot_id,
            moment=moment,
            previous_snapshot_id=previous_snapshot_id,
            timestamp=timestamp,
            annotations=annotations,
        )

    def __str__(self) -> str:
        to_str = ""
        to_str += f"# Moment ID: {self.moment_id}\n"
        to_str += f"# Snapshot ID: {self.snapshot_id}\n"
        if self.previous_snapshot_id:
            to_str += f"# Previous Snapshot ID: {self.previous_snapshot_id}\n"
        to_str += f"# Timestamp: {self.timestamp}\n"
        if self.annotations:
            to_str += f"# Annotations: ```\n{yaml.dump(self.annotations, default_flow_style=False).strip()}\n```\n"
        return to_str + str(self.moment)

    def to_dict(self) -> dict:
        return deepcopy(
            {
                "moment_id": self.moment_id,
                "snapshot_id": self.snapshot_id,
                "previous_snapshot_id": self.previous_snapshot_id,
                "timestamp": self.timestamp,
                "annotations": self.annotations,
                "moment": self.moment.to_dict(),
            }
        )
