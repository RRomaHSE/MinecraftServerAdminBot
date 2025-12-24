# tests/test_rcon_connection.py
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_rcon_sync():
    """Синхронная версия теста RCON"""
    print("🧪 Тестируем RCON подключение (синхронно)...")

    try:
        # Для синхронного теста можно использовать asyncio.run()
        import asyncio

        async def async_test():
            from infrastructure.adapters.rcon_client import RconClientAdapter

            # Тестовые данные
            host = "free-ru.joinserver.xyz"
            port = 25575
            password = "123456789"

            print(f"Подключаемся к {host}:{port}")

            client = RconClientAdapter(host, port, password)

            # Тест подключения
            print("🔍 Тестируем подключение...")
            success, error = await client.test_connection()

            return success, error

        # Запускаем асинхронный код синхронно
        success, error = asyncio.run(async_test())

        if success:
            print("✅ Подключение успешно!")
            assert success is True
        else:
            print(f"❌ Ошибка подключения: {error}")
            assert False, error

    except Exception as e:
        print(f"🔥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise