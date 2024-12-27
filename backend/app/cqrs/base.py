"""Implémentation du pattern CQRS."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Dict
from pydantic import BaseModel

QueryResult = TypeVar("QueryResult")
CommandResult = TypeVar("CommandResult")

class Query(ABC):
    """Base class for all queries."""
    pass

class Command(ABC):
    """Base class for all commands."""
    pass

class QueryHandler(Generic[Query, QueryResult], ABC):
    @abstractmethod
    async def handle(self, query: Query) -> QueryResult:
        pass

class CommandHandler(Generic[Command, CommandResult], ABC):
    @abstractmethod
    async def handle(self, command: Command) -> CommandResult:
        pass

class QueryBus:
    def __init__(self):
        self._handlers: Dict[type, QueryHandler] = {}

    def register(self, query_type: type, handler: QueryHandler):
        self._handlers[query_type] = handler

    async def execute(self, query: Query) -> Any:
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query {type(query)}")
        return await handler.handle(query)

class CommandBus:
    def __init__(self):
        self._handlers: Dict[type, CommandHandler] = {}

    def register(self, command_type: type, handler: CommandHandler):
        self._handlers[command_type] = handler

    async def execute(self, command: Command) -> Any:
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command {type(command)}")
        return await handler.handle(command) 