import re
import yaml
from abc import ABCMeta, abstractmethod
from typing import Any, Type, Union, Tuple
from copy import deepcopy

# Define the main Occurrence class
class Occurrence(metaclass=ABCMeta):
    """Super class for one single happening that the agent sees in the moment."""

    def __init__(self: "Occurrence", content: Any):
        self.content = content

    def __repr__(self: "Occurrence"):
        return f"<{self.__class__.__name__} content={self.content}>"

    @staticmethod
    @abstractmethod
    def parse(line: str) -> "Occurrence":
        pass

    def __str__(self: "Occurrence") -> str:
        raise NotImplementedError()

    @classmethod
    def subtypes(cls: Type):
        return [cls.__name__ for cls in cls.__subclasses__()]

    def to_dict(self: "Occurrence") -> dict:
        return deepcopy(self.__dict__)


class Thought(Occurrence):
    """A thought that the agent has. Great to represent "let's think step by step"."""

    def __init__(self: "Thought", thought: str):
        super().__init__(thought if thought else "")

    @staticmethod
    def parse(line: str) -> "Thought":
        if match := re.match(r"^Thought:\s+\"(.+)\"$", line):
            return Thought(thought=match.group(1))
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        return f'Thought: "{self.content}"'


class Instructions(Occurrence):
    """Instructions by the agent developer to this agent to play their role. That the agent must abide by."""

    def __init__(self: "Instructions", instructions: str):
        super().__init__(instructions if instructions else "")

    @staticmethod
    def parse(line: str) -> "Instructions":
        if match := re.match(r"^Instructions:\s+\"(.+)\"$", line):
            return Instructions(instructions=match.group(1))
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        return f'Instructions: "{self.content}"'


class Begin(Occurrence):
    """A begin message that ends system information."""

    def __init__(self: "Begin"):
        super().__init__("")

    @staticmethod
    def parse(line: str) -> "Begin":
        if line.startswith("Begin."):
            return Begin()
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        return "Begin.\n\n"


class Motivation(Occurrence):
    """The motivations or goals of the agent."""

    def __init__(self: "Motivation", motivation: str):
        super().__init__(motivation if motivation else "")

    @staticmethod
    def parse(line: str) -> "Motivation":
        if match := re.match(r"^Motivation:\s+\"(.+)\"$", line):
            return Motivation(motivation=match.group(1))
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        return f'Motivation: "{self.content}"'


class Observation(Occurrence):
    """The observation an agent makes about the world or the users."""

    def __init__(self: "Observation", observation: str):
        super().__init__(observation if observation else "")

    @staticmethod
    def parse(line: str) -> "Observation":
        if match := re.match(r"^Observation:\s+\"(.+)\"$", line):
            return Observation(observation=match.group(1))
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        return f'Observation: "{self.content}"\n'


class Context(Occurrence):
    """An additional context that may be injected through code. It's a yaml representation of a dict."""

    def __init__(self: "Context", context: str):
        super().__init__(context if context else "")

    @staticmethod
    def parse(line: str) -> "Context":
        if match := re.match(r"^Context:\s+```(.+?)```$", line):
            yaml_content = yaml.safe_load(match.group(1))
            return Context(context=yaml_content)
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Context: ```{yaml_content}```"


class Self(Occurrence):
    """What the agent says, including the optional emotion they have."""

    def __init__(self: "Self", emotion: str, says: str):
        super().__init__(
            {"emotion": emotion if emotion else "", "says": says if says else ""}
        )

    @staticmethod
    def parse(line: str) -> "Self":
        if match := re.match(r"^Self:\s+(\((.*)\)\s+)?\"(.+)\"$", line):
            return Self(emotion=match.group(2), says=match.group(3))
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        emotion, says = self.content["emotion"], self.content["says"]
        emotion_str = f"({emotion} " if emotion else ""
        return f'Self: {emotion_str}"{says}"'


class Participant(Occurrence):
    """
    What the participant (e.g. one or more users or other agents) say. Attributes:
    name - the known name of the user or generic class.
    identifier - the known identifier of the user, else 'unidentified' or 'unknonwn';
    emotion - the optional emotion they are expressing.
    says - what they are saying
    """

    def __init__(
        self: "Participant", name: str, identifier: str, emotion: str, says: str
    ):
        super().__init__(
            {
                "name": name if name else "",
                "identifier": identifier if identifier else "",
                "emotion": emotion if emotion else "",
                "says": says if says else "",
            }
        )

    @staticmethod
    def parse(line: str) -> "Participant":
        if match := re.match(
            r"^(.+)\s+\((\d+|unidentified|unknown)\):\s+(\((.*)\)\s+)?\"(.+)\"$",
            line,
        ):
            return Participant(
                name=match.group(1),
                identifier=match.group(2),
                emotion=match.group(4),
                says=match.group(5),
            )
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        name, identifier, emotion, says = (
            self.content["name"],
            self.content["identifier"],
            self.content["emotion"],
            self.content["says"],
        )
        emotion_str = f"({emotion} " if emotion else ""
        return f'{name} ({identifier}): {emotion_str}"{says}"'


class Identification(Occurrence):
    """
    Noting that the agent now identifies the person.
    Includes old name and id, and new name and id. May include the kind=human/agent
    """

    def __init__(
        self: "Identification",
        old_name: str,
        old_id: str,
        new_name: str,
        new_id: str,
        kind: str,
    ):
        super().__init__(
            {
                "old_name": old_name if old_name else "",
                "old_id": old_id if old_id else "",
                "new_name": new_name if new_name else "",
                "new_id": new_id if new_id else "",
                "kind": kind if kind else "",
            }
        )

    @staticmethod
    def parse(line: str) -> "Identification":
        if match := re.match(
            r"^Identification:\s+(.+)\s+\((\s+|unidentified)\)\s+is\s+now\s+(.+)\s+\((\s+)\)\s+\[(.+)\].$",
            line,
        ):
            return Identification(
                old_name=match.group(1),
                old_id=match.group(2),
                new_name=match.group(3),
                new_id=match.group(4),
                kind=match.group(5),
            )
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        old_name, old_id, new_name, new_id, kind = (
            self.content["old_name"],
            self.content["old_id"],
            self.content["new_name"],
            self.content["new_id"],
            self.content["kind"],
        )
        return f"Identification: {old_name} ({old_id}) is now {new_name} ({new_id}) [{kind}]."


class Waiting(Occurrence):
    """
    Set of key value pairs the agent is waiting on. Will resume if "Resuming" is injected.
    """

    def __init__(self: "Waiting", waiting_on: dict):
        super().__init__(waiting_on if waiting_on else "")

    @staticmethod
    def parse(line: str) -> "Waiting":
        if match := re.match(r"^Waiting:\s+```(.+?)```$", line):
            yaml_content = yaml.safe_load(match.group(1))
            return Waiting(waiting_on=yaml_content)
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Waiting: ```{yaml_content}```"


class Resuming(Occurrence):
    """
    Forced injection of resuming e.g. Not needed if participant says something or context is injected.
    Set of key value pairs the agent is resuming on. Expected after wait.
    """

    def __init__(self: "Resuming", resuming_on: dict):
        super().__init__(resuming_on if resuming_on else "")

    @staticmethod
    def parse(line: str) -> "Resuming":
        if match := re.match(r"^Resuming:\s+```(.+?)```$", line):
            yaml_content = yaml.safe_load(match.group(1))
            return Resuming(resuming_on=yaml_content)
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Resuming: ```{yaml_content}```"


class Working(Occurrence):
    """Agent is busy - working on some long task. Including a description of what the agent is working on."""

    def __init__(self: "Working", working_on: dict):
        super().__init__(working_on if working_on else "")

    @staticmethod
    def parse(line: str) -> "Working":
        if match := re.match(r"^Working:\s+```(.+?)```$", line):
            yaml_content = yaml.safe_load(match.group(1))
            return Working(working_on=yaml_content)
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Working: ```{yaml_content}```"


class Action(Occurrence):
    """Action that the agent needs to request from underlying system. e.g. a dict representation of a python function call including payload object."""

    def __init__(self: "Action", action: dict):
        super().__init__(action if action else "")

    @staticmethod
    def parse(line: str) -> "Action":
        if match := re.match(r"^Action:\s+```(.+?)```$", line):
            yaml_content = yaml.safe_load(match.group(1))
            return Action(action=yaml_content)
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Action: ```{yaml_content}```"


class Example(Occurrence):
    """An example conversation including title"""

    def __init__(self: "Example", title: str, example: str):
        super().__init__(
            {"title": title if title else "", "example": example if example else ""}
        )

    @staticmethod
    def parse(line: str) -> "Example":
        if match := re.match(r"^Example:\s+(.+)\s+-\s+'''(.+)'''$", line):
            return Example(title=match.group(1), example=match.group(2))
        raise MomentParseException(f"Unable to parse:\n\t{line})")

    def __str__(self) -> str:
        title, example = (self.content["title"], self.content["example"])
        return f"Example: {title} - '''{example}'''"


class MomentParseException(Exception):
    pass


class Moment:
    """A class specifically designed for agents to capture and structure their observations of events and interactions in real life or online environments."""

    id: str
    occurrences: list[Occurrence]

    # pylint: disable=redefined-builtin
    def __init__(self, id: str, occurrences: list[Occurrence]):
        self.id = id
        self.occurrences = occurrences

    @classmethod
    def parse(cls, obj: Union[str, dict]) -> "Moment":
        id: str
        occurrences: list[Occurrence]
        if isinstance(obj, str):
            id, occurrences = cls._parse_text(obj)
        elif isinstance(obj, dict):
            id, occurrences = cls._parse_dict(obj)
        return cls(id=id, occurrences=occurrences)

    @classmethod
    def _parse_dict(cls, moment: dict) -> Tuple[str, list[Occurrence]]:
        id = moment["id"]
        occurrences: list[Occurrence] = []
        for occurrence in moment["occurrences"]:
            kind = occurrence.pop("kind", None)
            match kind:
                case "Instructions":
                    occurrences.append(Instructions(**occurrence))
                case "Example":
                    occurrences.append(Example(**occurrence))
                case "Begin":
                    occurrences.append(Begin())
                case "Thought":
                    occurrences.append(Thought(**occurrence))
                case "Motivation":
                    occurrences.append(Motivation(**occurrence))
                case "Observation":
                    occurrences.append(Observation(**occurrence))
                case "Self":
                    occurrences.append(Self(**occurrence))
                case "Participant":
                    occurrences.append(Participant(**occurrence))
                case "Identification":
                    occurrences.append(Identification(**occurrence))
                case "Context":
                    occurrences.append(Context(**occurrence))
                case "Action":
                    occurrences.append(Action(**occurrence))
                case "Waiting":
                    occurrences.append(Waiting(**occurrence))
                case "Resuming":
                    occurrences.append(Resuming(**occurrence))
                case "Working":
                    occurrences.append(Working(**occurrence))

        return id, occurrences

    @classmethod
    def _parse_text(cls, text: str) -> Tuple[str, list[Occurrence]]:
        id: str
        occurrences: list[Occurrence] = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                # Moment Id
                if match := re.match(r"^#\s+Moment\s*[ID|id|Id]:\s+(.+)$", line):
                    id = str(match.group(1))

            occurrence_class: Type[Occurrence]
            occurrence_classes: list[Type[Occurrence]] = [
                Instructions,
                Example,
                Begin,
                Thought,
                Motivation,
                Observation,
                Self,
                Participant,
                Identification,
                Context,
                Action,
                Waiting,
                Resuming,
                Working,
            ]
            for occurrence_class in occurrence_classes:
                parsed_occurrence = occurrence_class.parse(line)
                if parsed_occurrence:
                    occurrences.append(parsed_occurrence)
                    break
            else:
                if line.strip() != "":
                    raise ValueError(f"Invalid MDL syntax in line: {line}")

        return id, occurrences

    def __str__(self) -> str:
        moment_str = ""
        for occurrence in self.occurrences:
            moment_str += str(occurrence) + "\n"
        return moment_str

    def to_dict(self) -> dict:
        return deepcopy(
            {
                "id": self.id,
                "occurrences": [
                    occurrence.to_dict() for occurrence in self.occurrences
                ],
            }
        )
