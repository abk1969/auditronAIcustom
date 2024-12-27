"""Implémentation CQRS pour les analyses."""
from typing import List, Optional
from pydantic import BaseModel
from app.cqrs.base import Command, Query, CommandHandler, QueryHandler
from app.models.analysis import Analysis, AnalysisStatus
from app.repositories.analysis import AnalysisRepository
from app.events.event_store import EventStore, Event

# Queries
class GetAnalysisByIdQuery(Query):
    id: str

class GetUserAnalysesQuery(Query):
    user_id: str
    skip: int = 0
    limit: int = 10

# Commands
class CreateAnalysisCommand(Command):
    user_id: str
    code_snippet: str
    language: str
    repository_url: Optional[str] = None

class UpdateAnalysisStatusCommand(Command):
    analysis_id: str
    status: AnalysisStatus
    metrics: Optional[dict] = None

# Handlers
class GetAnalysisByIdHandler(QueryHandler[GetAnalysisByIdQuery, Analysis]):
    def __init__(self, repository: AnalysisRepository):
        self.repository = repository

    async def handle(self, query: GetAnalysisByIdQuery) -> Analysis:
        return await self.repository.get(query.id)

class CreateAnalysisHandler(CommandHandler[CreateAnalysisCommand, Analysis]):
    def __init__(self, repository: AnalysisRepository, event_store: EventStore):
        self.repository = repository
        self.event_store = event_store

    async def handle(self, command: CreateAnalysisCommand) -> Analysis:
        analysis = await self.repository.create(
            user_id=command.user_id,
            code_snippet=command.code_snippet,
            language=command.language,
            repository_url=command.repository_url
        )

        # Créer un événement pour le tracking
        event = Event.create(
            aggregate_id=analysis.id,
            aggregate_type="Analysis",
            event_type="AnalysisCreated",
            data={
                "user_id": command.user_id,
                "language": command.language,
                "repository_url": command.repository_url
            }
        )
        await self.event_store.save_event(event)

        return analysis 