import asyncio
from rcon import rcon


class RconClientAdapter:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

    async def test_connection(self) -> bool:
        """Проверяет подключение к RCON серверу"""
        try:
            # Используем asyncio.to_thread для синхронной библиотеки
            response = await asyncio.to_thread(
                rcon, self.host, self.port, self.password, "list"
            )
            return response is not None and "error" not in response.lower()
        except Exception:
            return False

    async def execute_command(self, command: str) -> str:
        """Выполняет команду на сервере"""
        try:
            response = await asyncio.to_thread(
                rcon, self.host, self.port, self.password, command
            )
            return response or "Команда выполнена"
        except Exception as e:
            return f"Ошибка: {str(e)}"
