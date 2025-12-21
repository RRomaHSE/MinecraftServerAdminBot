from datetime import datetime, timedelta
from Domain.models import RconCredentials, Server, UserSession
from Adapters.rcon_client import RconClientAdapter
from Infrastructure.database import Database
from Infrastructure.crypto import CryptoService


class AuthorizeUserUseCase:
    def __init__(self, db: Database, crypto_service: CryptoService):
        self.db = db
        self.crypto_service = crypto_service

    async def execute(self, user_id: int, creds: RconCredentials) -> bool:
        # 1. Whitelist проверка (самый важный пункт!)
        if not await self.db.is_user_whitelisted(user_id):
            return False

        # 2. Проверка подключения через RCON
        rcon_client = RconClientAdapter(creds.host, creds.port, creds.password)
        is_valid = await rcon_client.test_connection()
        if not is_valid:
            return False

        # 3. Шифрование пароля и сохранение Server
        encrypted_pwd = self.crypto_service.encrypt(creds.password)
        server = Server(
            server_key=f"{creds.host}:{creds.port}",
            user_id=user_id,
            encrypted_password=encrypted_pwd,
            host=creds.host,
            port=creds.port
        )
        await self.db.save_server(server)

        # 4. Создание сессии (на 12 часов)
        session = UserSession(
            user_id=user_id,
            server_key=server.server_key,
            expires_at=datetime.utcnow() + timedelta(hours=12)
        )
        await self.db.save_session(session)

        return True
