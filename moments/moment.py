import re
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import yaml
from parsimonious.grammar import Grammar

p = Path(__file__).with_name("grammar.peg")
with p.open("r", encoding="utf-8") as f:
    GRAMMAR = Grammar(f.read())


# Define the main Occurrence class
class Occurrence(metaclass=ABCMeta):
    """Super class for one single happening that the agent sees in the moment."""

    def __init__(self: "Occurrence", content: Any):
        self.content = content

    def __repr__(self: "Occurrence"):
        return f"<{self.__class__.__name__} content={self.content}>"

    def __str__(self: "Occurrence") -> str:
        raise NotImplementedError()

    @classmethod
    def subtypes(cls: Type):
        return [cls.__name__ for cls in cls.__subclasses__()]

    def to_dict(self: "Occurrence") -> dict:
        occurrence = deepcopy(self.__dict__)
        occurrence["kind"] = self.__class__.__name__
        return occurrence


class Instructions(Occurrence):
    """Instructions by the agent developer to this agent to play their role. That the agent must abide by."""

    def __init__(self: "Instructions", instructions: str):
        super().__init__(instructions if instructions else "")

    def __str__(self) -> str:
        return f'Instructions: """{self.content}"""'


class Example(Occurrence):
    """An example conversation including title"""

    def __init__(self: "Example", title: str, example: str):
        super().__init__(
            {"title": title if title else "", "example": example if example else ""}
        )

    def __str__(self) -> str:
        title, example = (self.content["title"], self.content["example"])
        return f"Example: {title} - '''{example}'''"


class Begin(Occurrence):
    """A begin message that ends system information."""

    def __init__(self: "Begin"):
        super().__init__("")

    def __str__(self) -> str:
        return "Begin."


class Context(Occurrence):
    """An additional context that may be injected through code. It's a yaml representation of a dict."""

    def __init__(self: "Context", context: Dict[Any, Any]):
        super().__init__(context if context else {})

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Context: ```{yaml_content}```"


class Self(Occurrence):
    """What the agent says, including the optional emotion they have."""

    def __init__(self: "Self", emotion: str, says: str):
        super().__init__(
            {"emotion": emotion if emotion else "", "says": says if says else ""}
        )

    def __str__(self) -> str:
        emotion, says = self.content["emotion"], self.content["says"]
        emotion_str = f"({emotion}) " if emotion else ""
        says = says.replace('"', '\\"')
        says_str = f'"""{says}"""' if "\n" in says else f'"{says}"'
        return f"Self: {emotion_str}{says_str}"


class Participant(Occurrence):
    """
    What the participant (e.g. one or more users or other agents) say. Attributes:
    name - the known name of the user or generic class.
    identifier - the known identifier of the user, else 'unidentified' or 'unknonwn';
    emotion - the optional emotion they are expressing.
    says - what they are saying
    """

    def __init__(self: "Participant", name: str, emotion: str, says: str):
        super().__init__(
            {
                "name": name if name else "",
                "emotion": emotion if emotion else "",
                "says": says if says else "",
            }
        )

    def __str__(self) -> str:
        name, emotion, says = (
            self.content["name"],
            self.content["emotion"],
            self.content["says"],
        )
        emotion_str = f"({emotion}) " if emotion else ""
        says = says.replace('"', '\\"')
        says_str = f'"""{says}"""' if "\n" in says else f'"{says}"'
        return f"{name}: {emotion_str}{says_str}"


class Motivation(Occurrence):
    """The motivations or goals of the agent."""

    def __init__(self: "Motivation", motivation: str):
        super().__init__(motivation if motivation else "")

    def __str__(self) -> str:
        return f"Motivation: {self.content}"


class Observation(Occurrence):
    """The observation an agent makes about the world or the users."""

    def __init__(self: "Observation", observation: str):
        super().__init__(observation if observation else "")

    def __str__(self) -> str:
        return f"Observation: {self.content}\n"


class Thought(Occurrence):
    """A thought that the agent has. Great to represent "let's think step by step"."""

    def __init__(self: "Thought", thought: str):
        super().__init__(thought if thought else "")

    def __str__(self) -> str:
        return f'Thought: """{self.content}"""'


class Identification(Occurrence):
    """
    Noting that the agent now identifies the person.
    Includes old name and id, and new name and id. May include the kind=human/agent
    """

    def __init__(self: "Identification", kind: str, name: str):
        super().__init__({"kind": kind if kind else "", "name": name if name else ""})

    def __str__(self) -> str:
        kind, name = (self.content["kind"], self.content["name"])
        return f'Identification: {kind} is called "{name}".'


class Waiting(Occurrence):
    """
    Set of key value pairs the agent is waiting on. Will resume if "Resuming" is injected.
    """

    def __init__(self: "Waiting", waiting_on: dict):
        super().__init__(waiting_on if waiting_on else "")

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

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Resuming: ```{yaml_content}```"


class Working(Occurrence):
    """Agent is busy - working on some long task. Including a description of what the agent is working on."""

    def __init__(self: "Working", working_on: dict):
        super().__init__(working_on if working_on else "")

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Working: ```{yaml_content}```"


class Action(Occurrence):
    """Action that the agent needs to request from underlying system. e.g. a dict representation of a python function call including payload object."""

    def __init__(self: "Action", action: dict):
        super().__init__(action if action else "")

    def __str__(self) -> str:
        yaml_content = yaml.dump(self.content, default_flow_style=False).strip()
        return f"Action: ```{yaml_content}```"


class Rejected(Occurrence):
    """The text rejected in the RLHF process."""

    def __init__(self: "Rejected", emotion: str, says: str):
        super().__init__(
            {"emotion": emotion if emotion else "", "says": says if says else ""}
        )

    def __str__(self) -> str:
        emotion, says = self.content["emotion"], self.content["says"]
        emotion_str = f"({emotion}) " if emotion else ""
        says = says.replace('"', '\\"')
        says_str = f'"""{says}"""' if "\n" in says else f'"{says}"'
        return f"Rejected: {emotion_str}{says_str}"


class CritiqueRequest(Occurrence):
    """The critique request to an RLAIF agent."""

    def __init__(self: "CritiqueRequest", critique_request: str):
        super().__init__(critique_request if critique_request else "")

    def __str__(self) -> str:
        return f"Critique Request: {self.content}"


class Critique(Occurrence):
    """The critique by an RLAIF agent."""

    def __init__(self: "Critique", critique: str):
        super().__init__(critique if critique else "")

    def __str__(self) -> str:
        return f"Critique: {self.content}"


class RevisionRequest(Occurrence):
    """The revision request to an RLAIF agent."""

    def __init__(self: "RevisionRequest", revision_request: str):
        super().__init__(revision_request if revision_request else "")

    def __str__(self) -> str:
        return f"Revision Request: {self.content}"


class Revision(Occurrence):
    """The revision by an RLAIF agent."""

    def __init__(self: "Revision", emotion: str, says: str):
        super().__init__(
            {"emotion": emotion if emotion else "", "says": says if says else ""}
        )

    def __str__(self) -> str:
        emotion, says = self.content["emotion"], self.content["says"]
        emotion_str = f"({emotion}) " if emotion else ""
        says = says.replace('"', '\\"')
        says_str = f'"""{says}"""' if "\n" in says else f'"{says}"'
        return f"Revision: {emotion_str}{says_str}"


class MomentParseException(Exception):
    pass


def walk(node, occurrences: List[Occurrence]):
    if node.expr_name == "Instructions":
        instructions = ""
        for child in node.children:
            if child.expr_name == "string":
                instructions = child.text
        occurrences.append(Instructions(instructions))
    elif node.expr_name == "Example":
        title = ""
        example = ""
        for child in node.children:
            if child.expr_name == "title":
                title = child.text
            elif child.expr_name == "tqs_content":
                example = child.text
        occurrences.append(Example(title, example))
    elif node.expr_name == "Begin":
        occurrences.append(Begin())
    elif node.expr_name == "Context":
        yaml_content = {}
        for child in node.children:
            if child.expr_name == "ct_content":
                yaml_content = yaml.safe_load(child.text)
        occurrences.append(Context(yaml_content))
    elif node.expr_name == "Self":
        emotion = ""
        says = ""
        for child in node.children:
            if child.expr_name == "says_string":
                says_node = child
                for says_child in says_node.children:
                    if says_child.expr_name == "q_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "q_content":
                                says = content_child.text
                    elif says_child.expr_name == "tq_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "tq_content":
                                says = content_child.text
            elif child.text.strip():
                other_node = child
                for other_child in other_node.children:
                    if other_child.expr_name == "emotion":
                        emotion_node = other_child
                        for emotion_child in emotion_node.children:
                            if emotion_child.expr_name == "emotion_content":
                                emotion = emotion_child.text
        occurrences.append(Self(emotion, says))
    elif node.expr_name == "Rejected":
        emotion = ""
        says = ""
        for child in node.children:
            if child.expr_name == "says_string":
                says_node = child
                for says_child in says_node.children:
                    if says_child.expr_name == "q_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "q_content":
                                says = content_child.text
                    elif says_child.expr_name == "tq_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "tq_content":
                                says = content_child.text
            elif child.text.strip():
                other_node = child
                for other_child in other_node.children:
                    if other_child.expr_name == "emotion":
                        emotion_node = other_child
                        for emotion_child in emotion_node.children:
                            if emotion_child.expr_name == "emotion_content":
                                emotion = emotion_child.text
        occurrences.append(Rejected(emotion, says=says))
    elif node.expr_name == "Thought":
        says = ""
        for child in node.children:
            if child.expr_name == "says_string":
                says_node = child
                for says_child in says_node.children:
                    if says_child.expr_name == "q_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "q_content":
                                says = content_child.text
                    elif says_child.expr_name == "tq_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "tq_content":
                                says = content_child.text
        occurrences.append(Thought(thought=says))
    elif node.expr_name == "Motivation":
        motivation = ""
        for child in node.children:
            if child.expr_name == "string":
                motivation = child.text
        occurrences.append(Motivation(motivation))
    elif node.expr_name == "Observation":
        observation = ""
        for child in node.children:
            if child.expr_name == "string":
                observation = child.text
        occurrences.append(Observation(observation))
    elif node.expr_name == "Waiting":
        yaml_content = {}
        for child in node.children:
            if child.expr_name == "ct_content":
                yaml_content = yaml.safe_load(child.text)
        occurrences.append(Waiting(waiting_on=yaml_content))
    elif node.expr_name == "Resuming":
        yaml_content = {}
        for child in node.children:
            if child.expr_name == "ct_content":
                yaml_content = yaml.safe_load(child.text)
        occurrences.append(Resuming(resuming_on=yaml_content))
    elif node.expr_name == "Working":
        yaml_content = {}
        for child in node.children:
            if child.expr_name == "ct_content":
                yaml_content = yaml.safe_load(child.text)
        occurrences.append(Working(working_on=yaml_content))
    elif node.expr_name == "Action":
        yaml_content = {}
        for child in node.children:
            if child.expr_name == "ct_content":
                yaml_content = yaml.safe_load(child.text)
        occurrences.append(Action(action=yaml_content))
    elif node.expr_name == "CritiqueRequest":
        string = ""
        for child in node.children:
            if child.expr_name == "string":
                string = child.text
        occurrences.append(CritiqueRequest(critique_request=string))
    elif node.expr_name == "Critique":
        string = ""
        for child in node.children:
            if child.expr_name == "string":
                string = child.text
        occurrences.append(Critique(critique=string))
    elif node.expr_name == "RevisionRequest":
        string = ""
        for child in node.children:
            if child.expr_name == "string":
                string = child.text
        occurrences.append(RevisionRequest(revision_request=string))
    elif node.expr_name == "Revision":
        emotion = ""
        says = ""
        for child in node.children:
            if child.expr_name == "says_string":
                says_node = child
                for says_child in says_node.children:
                    if says_child.expr_name == "q_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "q_content":
                                says = content_child.text
                    elif says_child.expr_name == "tq_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "tq_content":
                                says = content_child.text
            elif child.text.strip():
                other_node = child
                for other_child in other_node.children:
                    if other_child.expr_name == "emotion":
                        emotion_node = other_child
                        for emotion_child in emotion_node.children:
                            if emotion_child.expr_name == "emotion_content":
                                emotion = emotion_child.text
        occurrences.append(Revision(emotion, says))
    elif node.expr_name == "Participant":
        participant = ""
        identifier = ""
        emotion = ""
        says = ""
        for child in node.children:
            if child.expr_name == "participant":
                participant = child.text
            elif child.expr_name == "says_string":
                says_node = child
                for says_child in says_node.children:
                    if says_child.expr_name == "q_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "q_content":
                                says = content_child.text
                    elif says_child.expr_name == "tq_string":
                        for content_child in says_child.children:
                            if content_child.expr_name == "tq_content":
                                says = content_child.text
            elif child.text.strip():
                other_node = child
                for other_child in other_node.children:
                    if other_child.expr_name == "emotion":
                        emotion_node = other_child
                        for emotion_child in emotion_node.children:
                            if emotion_child.expr_name == "emotion_content":
                                emotion = emotion_child.text
        occurrences.append(Participant(participant, emotion, says))
    elif node.expr_name == "Identification":
        participant = ""
        name = ""
        for child in node.children:
            if child.expr_name == "participant":
                participant = child.text
            elif child.expr_name == "name":
                name_node = child
                for name_child in name_node.children:
                    if name_child.expr_name == "name_content":
                        name = name_child.text
        occurrences.append(Identification(participant, name))
    elif node.expr_name.strip():
        assert node.expr_name in ["Occurrence", "Occurrences"]
        for child in node.children:
            walk(child, occurrences)


class Moment:
    """A class specifically designed for agents to capture and structure their observations of events and interactions in real life or online environments."""

    id: str
    occurrences: List[Occurrence]

    # pylint: disable=redefined-builtin
    def __init__(self, id: str, occurrences: List[Occurrence]):
        self.id = id
        self.occurrences = occurrences

    @classmethod
    def parse(cls, obj: Union[str, dict]) -> "Moment":
        id: str
        occurrences: List[Occurrence]
        if isinstance(obj, str):
            id, occurrences = cls._parse_text(obj)
        elif isinstance(obj, dict):
            id, occurrences = cls._parse_dict(obj)
        return cls(id=id, occurrences=occurrences)

    @classmethod
    def _parse_dict(cls, moment: dict) -> Tuple[str, List[Occurrence]]:
        id = moment["id"]

        occurrences: List[Occurrence] = []
        for occurrence in moment["occurrences"]:
            kind = occurrence.pop("kind", None)
            if kind == "Instructions":
                occurrences.append(Instructions(occurrence["content"]))
            elif kind == "Example":
                occurrences.append(Example(**occurrence["content"]))
            elif kind == "Begin":
                occurrences.append(Begin())
            elif kind == "Thought":
                occurrences.append(Thought(occurrence["content"]))
            elif kind == "Motivation":
                occurrences.append(Motivation(occurrence["content"]))
            elif kind == "Observation":
                occurrences.append(Observation(occurrence["content"]))
            elif kind == "Self":
                occurrences.append(Self(**occurrence["content"]))
            elif kind == "Identification":
                occurrences.append(Identification(**occurrence["content"]))
            elif kind == "Context":
                occurrences.append(Context(occurrence["content"]))
            elif kind == "Action":
                occurrences.append(Action(**occurrence["content"]))
            elif kind == "Waiting":
                occurrences.append(Waiting(**occurrence["content"]))
            elif kind == "Resuming":
                occurrences.append(Resuming(**occurrence["content"]))
            elif kind == "Working":
                occurrences.append(Working(**occurrence["content"]))
            elif kind == "Rejected":
                occurrences.append(Rejected(**occurrence["content"]))
            elif kind == "CritiqueRequest":
                occurrences.append(CritiqueRequest(occurrence["content"]))
            elif kind == "Critique":
                occurrences.append(Critique(occurrence["content"]))
            elif kind == "RevisionRequest":
                occurrences.append(RevisionRequest(occurrence["content"]))
            elif kind == "Revision":
                occurrences.append(Revision(**occurrence["content"]))
            elif kind == "Participant":
                occurrences.append(Participant(**occurrence["content"]))

        return id, occurrences

    @classmethod
    def _parse_text(cls, text: str) -> Tuple[str, List[Occurrence]]:
        id: str = ""
        occurrences: List[Occurrence] = []
        parsed = GRAMMAR.parse(text)
        walk(parsed, occurrences)
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
