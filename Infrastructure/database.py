import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, select
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta

from Domain.models import Server, UserSession

Base = declarative_base()


class ServerModel(Base):
    __tablename__ = 'servers'
    
    server_key = Column(String, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    encrypted_password = Column(LargeBinary)
    host = Column(String)
    port = Column(Integer)


class UserSessionModel(Base):
    __tablename__ = 'user_sessions'
    
    user_id = Column(Integer, primary_key=True)
    server_key = Column(String)
    expires_at = Column(DateTime)


class AdminModel(Base):
    __tablename__ = 'admins'
    
    user_id = Column(Integer, primary_key=True)


class Database:
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./database.db"):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Инициализирует базу данных (создает таблицы)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def is_user_whitelisted(self, user_id: int) -> bool:
        """Проверяет, есть ли пользователь в белом списке админов"""
        async with self.async_session() as session:
            result = await session.execute(
                select(AdminModel).where(AdminModel.user_id == user_id)
            )
            return result.scalar() is not None

    async def save_server(self, server: Server):
        """Сохраняет сервер в базу данных"""
        async with self.async_session() as session:
            server_model = ServerModel(
                server_key=server.server_key,
                user_id=server.user_id,
                encrypted_password=server.encrypted_password,
                host=server.host,
                port=server.port
            )
            session.add(server_model)
            await session.commit()

    async def save_session(self, session: UserSession):
        """Сохраняет сессию пользователя"""
        async with self.async_session() as db_session:
            session_model = UserSessionModel(
                user_id=session.user_id,
                server_key=session.server_key,
                expires_at=session.expires_at
            )
            db_session.add(session_model)
            await db_session.commit()

    async def get_active_session(self, user_id: int) -> Optional[UserSession]:
        """Получает активную сессию пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                select(UserSessionModel).where(
                    UserSessionModel.user_id == user_id,
                    UserSessionModel.expires_at > datetime.utcnow()
                )
            )
            session_model = result.scalar()
            
            if session_model:
                return UserSession(
                    user_id=session_model.user_id,
                    server_key=session_model.server_key,
                    expires_at=session_model.expires_at
                )
            return None
