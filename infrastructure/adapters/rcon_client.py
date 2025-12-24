# infrastructure/adapters/rcon_client.py
import asyncio
import socket
from typing import Optional, Tuple
from rcon.source import rcon as rcon_async
from rcon.exceptions import EmptyResponse, SessionTimeout, WrongPassword

from loggers.app_logger import logger
from config.settings import settings


class RconClientAdapter:
    """
    Адаптер для работы с RCON протоколом Minecraft серверов.
    """

    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

    # infrastructure/adapters/rcon_client.py

    async def test_connection(self) -> Tuple[bool, str]:
        """Упрощенная проверка RCON подключения"""
        try:
            logger.info(f"Проверка RCON: {self.host}:{self.port}")

            # Пробуем выполнить простую команду
            response = await self._execute_with_retry("list")

            # Даже пустой ответ - это ответ (сервер доступен)
            logger.info(f"RCON ответ: '{response}'")

            # В Minecraft сервер может вернуть пустую строку для некоторых команд
            # Это нормально и означает успешное подключение
            return True, f"RCON подключено: {response[:50] if response else 'пустой ответ'}"

        except WrongPassword:
            return False, "Неверный пароль RCON"
        except ConnectionRefusedError:
            return False, "Соединение отклонено. Проверьте порт и включен ли RCON"
        except asyncio.TimeoutError:
            return False, "Таймаут. Сервер не отвечает"
        except Exception as e:
            error_msg = self._parse_rcon_error(e)
            return False, f"Ошибка RCON: {error_msg}"

    async def execute_command(self, command: str) -> str:
        """
        Выполняет команду на сервере с повторными попытками
        """
        return await self._execute_with_retry(command)

    async def send_command(self, command: str) -> Tuple[bool, str]:
        """
        Выполняет команду и возвращает результат
        """
        try:
            result = await self.execute_command(command)
            return True, result
        except Exception as e:
            error_msg = self._parse_rcon_error(e)
            return False, f"Ошибка: {error_msg}"

    async def _execute_with_retry(self, command: str) -> str:
        """
        Внутренний метод с повторными попытками
        """
        last_exception = None

        for attempt in range(settings.RCON_MAX_RETRIES):
            try:
                logger.debug(f"RCON команда [{attempt + 1}/{settings.RCON_MAX_RETRIES}]: {command}")

                response = await rcon_async(
                    command=command,
                    host=self.host,
                    port=self.port,
                    passwd=self.password,
                    timeout=settings.RCON_TIMEOUT
                )

                return response.strip() if response else ""

            except EmptyResponse:
                return ""
            except Exception as e:
                last_exception = e
                logger.warning(f"Попытка {attempt + 1} неудачна: {e}")
                if attempt < settings.RCON_MAX_RETRIES - 1:
                    await asyncio.sleep(settings.RCON_RETRY_DELAY)

        raise last_exception or Exception("Все попытки выполнения команды неудачны")

    def _parse_rcon_error(self, error: Exception) -> str:
        """
        Парсинг ошибок RCON для понятного сообщения
        """
        error_str = str(error).lower()

        if "wrong password" in error_str or "incorrect password" in error_str:
            return "Неверный пароль RCON"
        elif "connection refused" in error_str:
            return "Соединение отклонено. Проверьте RCON порт"
        elif "timed out" in error_str:
            return "Таймаут ожидания ответа"
        elif "authentication" in error_str:
            return "Ошибка аутентификации RCON"
        elif isinstance(error, WrongPassword):
            return "Неверный пароль RCON"
        elif isinstance(error, SessionTimeout):
            return "Таймаут сессии RCON"
        else:
            return f"Ошибка RCON: {type(error).__name__}: {error}"

    async def get_server_status(self) -> dict:
        """
        Получение статуса сервера с проверкой
        """
        status = {
            "online": False,
            "players": "0/0",
            "version": "Неизвестно",
            "motd": "Неизвестно",
            "error": None
        }

        try:
            # Проверяем базовое подключение
            success, message = await self.test_connection()

            if not success:
                status["error"] = message
                return status

            status["online"] = True

            # Получаем список игроков
            try:
                list_response = await self.execute_command("list")
                if list_response:
                    import re
                    # Ищем паттерн "There are X/Y players online:"
                    match = re.search(r'(\d+)/(\d+)', list_response)
                    if match:
                        status["players"] = f"{match.group(1)}/{match.group(2)}"
            except:
                pass

            # Получаем версию
            try:
                version_response = await self.execute_command("version")
                if version_response:
                    status["version"] = version_response.split('\n')[0]
            except:
                pass

            return status

        except Exception as e:
            status["error"] = str(e)
            return status


# Фабрика с улучшенной проверкой
class RconClientFactory:
    @staticmethod
    async def create_and_test(host: str, port: int, password: str) -> Tuple[
        Optional['RconClientAdapter'], Optional[str]]:
        """
        Создает клиент и выполняет полную проверку
        """
        client = RconClientAdapter(host, port, password)
        success, message = await client.test_connection()

        if success:
            return client, None
        else:
            return None, message