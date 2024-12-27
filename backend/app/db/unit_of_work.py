"""Implémentation du pattern Unit of Work."""
from __future__ import annotations
from typing import Type
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository

class UnitOfWork(AbstractContextManager):
    def __init__(self, session_factory: Type[Session]):
        self.session_factory = session_factory

    def __enter__(self) -> UnitOfWork:
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def refresh(self, instance):
        self.session.refresh(instance) 