"""Tests d'intégration pour le flux d'analyse."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.analysis import Analysis, AnalysisStatus
from app.repositories.analysis_repository import AnalysisRepository
from app.cqrs.analysis import CreateAnalysisCommand, CreateAnalysisHandler
from app.events.event_store import EventStore

@pytest.fixture
async def analysis_repository(db_session: AsyncSession):
    return AnalysisRepository(Analysis, db_session)

@pytest.fixture
async def event_store(db_session: AsyncSession):
    return EventStore(db_session)

@pytest.fixture
async def create_analysis_handler(analysis_repository, event_store):
    return CreateAnalysisHandler(analysis_repository, event_store)

class TestAnalysisFlow:
    async def test_create_analysis(self, create_analysis_handler, db_session):
        command = CreateAnalysisCommand(
            user_id="test_user",
            code_snippet="print('hello')",
            language="python"
        )
        
        analysis = await create_analysis_handler.handle(command)
        
        assert analysis.id is not None
        assert analysis.status == AnalysisStatus.PENDING
        assert analysis.language == "python"
        
        # Vérifier que l'événement a été créé
        events = await event_store.get_events(analysis.id)
        assert len(events) == 1
        assert events[0].event_type == "AnalysisCreated" 