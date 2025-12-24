import asyncio
import socket
from rcon.source import rcon

async def full_rcon_test():
    print("=" * 50)
    print("ПОЛНЫЙ ТЕСТ RCON ПОСЛЕ ВКЛЮЧЕНИЯ")
    print("=" * 50)
    
    host = "65.21.24.204"
    port = 25575
    password = "123456789"
    
    print(f"Сервер: {host}:{port}")
    print(f"Пароль: {'*' * len(password)}")
    
    # 1. Проверка TCP подключения
    print("\n1. Проверка TCP подключения...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        print("    TCP порт открыт")
        sock.close()
    except Exception as e:
        print(f"    Ошибка TCP: {e}")
        return False
    
    # 2. Тест через библиотеку rcon
    print("\n2. Тест через библиотеку rcon...")
    try:
        response = await rcon(
            command="list",
            host=host,
            port=port,
            passwd=password,
            timeout=5
        )
        print(f"    RCON работает! Ответ:")
        print(f"   '{response.strip()}'")
        return True
    except Exception as e:
        print(f"    Ошибка rcon: {type(e).__name__}: {e}")
        
        # Пробуем другие команды
        print("\n3. Пробуем другие команды...")
        for cmd in ["help", "version", "time query day"]:
            try:
                response = await rcon(
                    command=cmd,
                    host=host,
                    port=port,
                    passwd=password,
                    timeout=3
                )
                print(f"   Команда '{cmd}':  '{response.strip()[:50]}...'")
                return True
            except:
                print(f"   Команда '{cmd}':  не работает")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(full_rcon_test())
    
    if success:
        print("\n" + "=" * 50)
        print(" RCON РАБОТАЕТ! Можно запускать бота в реальном режиме!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print(" RCON все еще не работает")
        print("Проверь:")
        print("1. Сервер перезагружен после включения RCON?")
        print("2. В server.properties: enable-rcon=true")
        print("3. Пароль точно '123456789'?")
        print("=" * 50)
