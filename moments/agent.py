import yaml
from abc import ABC, abstractmethod
from typing import Type
from moments.moment import Moment, Self

DEFAULT_NAME = "Leela"


class AgentConfig:
    kind: str
    id: str
    variant: str
    init: dict

    @staticmethod
    def from_file(config_file: str) -> "AgentConfig":
        with open(config_file, "r", encoding="utf-8") as file:
            return AgentConfig(**yaml.safe_load(file))

    # pylint: disable=redefined-builtin
    def __init__(
        self: "AgentConfig",
        kind: str,
        id: str,
        variant: str,
        init: dict,
    ):
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

    def init(self: "Agent") -> Moment:
        """Initializes the moment with system part of the prompt"""
        return Moment.parse(self.config.init)

    @abstractmethod
    def before(self: "Agent", moment: Moment) -> Self:
        """Hook to add context, observations, motivations, etc."""
        pass

    @abstractmethod
    def respond(self: "Agent", moment: Moment) -> Self:
        """Ask the LLM for the completion"""
        pass

    @abstractmethod
    def after(self: "Agent", moment: Moment) -> Self:
        """Hook to perform actions, etc."""
        pass


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
