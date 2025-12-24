# scripts/test_rcon_detailed.py
import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.adapters.rcon_client import RconClientAdapter


async def test_rcon_detailed(host: str, port: int, password: str):
    print(f"\n{'=' * 60}")
    print(f"🔍 ДЕТАЛЬНЫЙ ТЕСТ RCON: {host}:{port}")
    print(f"{'=' * 60}\n")

    client = RconClientAdapter(host, port, password)

    # Тест 1: Базовое подключение
    print("1. Тест базового подключения...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"   ✅ Порт {port} открыт на {host}")
        else:
            print(f"   ❌ Порт {port} закрыт или недоступен")
            return
    except Exception as e:
        print(f"   ❌ Ошибка проверки порта: {e}")
        return

    # Тест 2: RCON подключение
    print("\n2. Тест RCON подключения...")
    try:
        from rcon.source import Client
        from rcon.exceptions import WrongPassword

        rcon_client = Client(host, port, timeout=10)
        rcon_client.login(password)
        print(f"   ✅ RCON подключение успешно")
        rcon_client.close()
    except WrongPassword:
        print(f"   ❌ Неверный пароль RCON")
        return
    except ConnectionRefusedError:
        print(f"   ❌ Соединение отклонено. Убедитесь, что:")
        print(f"      • RCON включен в server.properties")
        print(f"      • Сервер запущен")
        print(f"      • Порт {port} правильный")
        return
    except Exception as e:
        print(f"   ❌ Ошибка RCON: {type(e).__name__}: {e}")
        return

    # Тест 3: Команды через наш адаптер
    print("\n3. Тест команд через RconClientAdapter...")

    test_commands = [
        "list",  # Базовая команда
        "save-all",  # Команда без вывода
        "time query day",  # Команда с ответом
        "help"  # Команда справки
    ]

    for cmd in test_commands:
        print(f"\n   Команда: '{cmd}'")
        try:
            result = await client.execute_command(cmd)
            if result is None:
                print(f"      📭 Ответ: None")
            elif result == "":
                print(f"      📭 Ответ: пустая строка")
            else:
                print(f"      ✅ Ответ ({len(result)} chars): {result[:100]}...")
        except Exception as e:
            print(f"      ❌ Ошибка: {type(e).__name__}: {e}")


if __name__ == "__main__":
    # Получаем параметры из аргументов или ввода
    import argparse

    parser = argparse.ArgumentParser(description='Тест RCON подключения')
    parser.add_argument('--host', default='localhost', help='Хост сервера')
    parser.add_argument('--port', type=int, default=25575, help='RCON порт')
    parser.add_argument('--password', help='RCON пароль')

    args = parser.parse_args()

    host = args.host or input("Хост [localhost]: ") or "localhost"
    port = args.port or int(input("Порт [25575]: ") or 25575)
    password = args.password or input("RCON пароль: ")

    if not password:
        print("❌ Пароль не указан")
        sys.exit(1)

    asyncio.run(test_rcon_detailed(host, port, password))