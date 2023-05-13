import yaml
from abc import ABC, abstractmethod
from typing import Type
from moments.moment import Moment
from moments.snapshot import Snapshot
from datetime import datetime
from uuid import uuid4

DEFAULT_NAME = "Leela"


class AgentConfig:
    mdl: str
    kind: str
    id: str
    variant: str
    init: str

    @staticmethod
    def from_file(config_file: str) -> "AgentConfig":
        with open(config_file, "r", encoding="utf-8") as file:
            return AgentConfig(**yaml.safe_load(file))

    # pylint: disable=redefined-builtin
    def __init__(
        self: "AgentConfig",
        mdl: str,
        kind: str,
        id: str,
        variant: str,
        init: str,
    ):
        self.mdl = mdl
        self.kind = kind
        self.id = id
        self.variant = variant
        self.init = init


class Agent(ABC):
    id: str
    config: AgentConfig

    # pylint: disable=redefined-builtin
    def __init__(
        self: "Agent",
        id: str,
        name: str,
        config: AgentConfig,
    ):
        self.id = id
        self.name = name
        self.config = config

    def system(self: "Agent") -> Snapshot:
        """Initializes the moment with system part of the prompt"""
        moment = Moment.parse(self.config.init)
        moment.id = str(uuid4())
        return Snapshot(
            id=str(uuid4()),
            moment=moment,
            previous_snapshot_id=None,
            timestamp=datetime.now().isoformat(),
            annotations={},
        )

    def next(self: "Agent", snapshot: Snapshot) -> Snapshot:
        self.before(snapshot.moment)
        self.do(snapshot.moment)
        self.after(snapshot.moment)
        snapshot.previous_snapshot_id = snapshot.id  # Chain it
        snapshot.id = str(uuid4())  # next it
        snapshot.timestamp = datetime.now().isoformat()
        return snapshot

    @abstractmethod
    def before(self: "Agent", moment: Moment):
        """Hook to add context, observations, motivations, etc."""

    @abstractmethod
    def do(self: "Agent", moment: Moment):
        """Ask the LLM for the completion"""

    @abstractmethod
    def after(self: "Agent", moment: Moment):
        """Hook to perform actions, etc."""


class AgentFactory:
    agent_classes: dict = {}

    @classmethod
    def register(cls: Type, agent_cls: Type):
        cls.agent_classes[agent_cls.__name__] = agent_cls

    @classmethod
    def create(cls: Type, agent_instance_id: str, agent_config: AgentConfig) -> "Agent":
        return cls.agent_classes[agent_config.kind](
            id=agent_instance_id,
            name=DEFAULT_NAME,
            config=agent_config,
        )
