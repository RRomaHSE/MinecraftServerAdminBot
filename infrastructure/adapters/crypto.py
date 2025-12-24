# infrastructure/adapters/crypto.py
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)


class CryptoService:
    def __init__(self, secret_key: str = None):
        """Инициализация с исправленной логикой"""

        # 1. Получаем ключ из настроек если не передан
        if not secret_key:
            try:
                from config.settings import settings
                secret_key = getattr(settings, 'ENCRYPTION_KEY', None)
                logger.debug(f"Получен ключ из настроек: {'есть' if secret_key else 'нет'}")
            except:
                secret_key = None

        # 2. Если ключ есть - используем его
        if secret_key:
            logger.info("Использую ключ из конфигурации")
            try:
                key = self._generate_key_from_secret(secret_key)
                self.cipher_suite = Fernet(key)
                logger.debug(f"Ключ создан успешно")
            except Exception as e:
                logger.error(f"Ошибка создания ключа из secret: {e}")
                # Fallback: генерируем новый
                key = Fernet.generate_key()
                self.cipher_suite = Fernet(key)
                logger.warning(f"Сгенерирован новый ключ")
        else:
            # 3. Генерируем новый ключ
            logger.warning("Ключ шифрования не найден. Генерирую новый...")
            key = Fernet.generate_key()
            self.cipher_suite = Fernet(key)
            logger.info(f"Сгенерирован ключ: {key.decode()[:20]}...")

            # Сохраняем в .env если возможно
            self._save_key_to_env(key)

        # 4. Тестируем шифрование
        self._test_encryption()

    def _save_key_to_env(self, key: bytes):
        """Сохраняет ключ в .env файл"""
        try:
            env_path = '.env'
            key_str = key.decode()

            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    content = f.read()

                if 'ENCRYPTION_KEY=' in content:
                    # Заменяем существующий ключ
                    import re
                    content = re.sub(r'ENCRYPTION_KEY=.*', f'ENCRYPTION_KEY={key_str}', content)
                else:
                    # Добавляем новый ключ
                    content += f'\nENCRYPTION_KEY={key_str}'

                with open(env_path, 'w') as f:
                    f.write(content)
            else:
                # Создаем новый .env
                with open(env_path, 'w') as f:
                    f.write(f'ENCRYPTION_KEY={key_str}\n')

            logger.info(f"Ключ сохранен в .env файл")

        except Exception as e:
            logger.error(f"Не удалось сохранить ключ в .env: {e}")

    def _generate_key_from_secret(self, secret: str) -> bytes:
        """Генерирует ключ из секретной фразы - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            # Убедимся что secret - строка
            if not isinstance(secret, str):
                secret = str(secret)

            # Фиксированный salt для совместимости
            salt = b'minecraft_salt_2024_v2'  # Изменен salt!

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )

            # Конвертируем secret в bytes
            secret_bytes = secret.encode('utf-8')
            key = base64.urlsafe_b64encode(kdf.derive(secret_bytes))

            logger.debug(f"Сгенерирован ключ из secret длиной {len(secret)}")
            return key

        except Exception as e:
            logger.error(f"Ошибка генерации ключа: {e}")
            raise

    def _test_encryption(self):
        """Тест шифрования/дешифрования"""
        try:
            test_data = "test_string_123_abc"
            logger.debug(f"Тест шифрования: '{test_data}'")

            encrypted = self.encrypt(test_data)
            logger.debug(f"Зашифровано: {len(encrypted)} байт")

            decrypted = self.decrypt(encrypted)
            logger.debug(f"Расшифровано: '{decrypted}'")

            if decrypted == test_data:
                logger.info("✅ Шифрование работает корректно")
            else:
                logger.error(f"❌ Шифрование не работает: '{decrypted}' != '{test_data}'")

        except Exception as e:
            logger.error(f"❌ Ошибка теста шифрования: {e}")

    def encrypt(self, data: str) -> bytes:
        """Шифрует данные - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            if not isinstance(data, str):
                data = str(data)

            data_bytes = data.encode('utf-8')
            encrypted = self.cipher_suite.encrypt(data_bytes)

            logger.debug(f"Шифрование: '{data[:10]}...' -> {len(encrypted)} байт")
            return encrypted

        except Exception as e:
            logger.error(f"Ошибка шифрования: {e}")
            raise

    def decrypt(self, encrypted_data: bytes) -> str:
        """Расшифровывает данные - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            if not isinstance(encrypted_data, bytes):
                # Пробуем преобразовать если это не bytes
                if isinstance(encrypted_data, str):
                    encrypted_data = encrypted_data.encode('latin-1')
                elif isinstance(encrypted_data, bytearray):
                    encrypted_data = bytes(encrypted_data)
                else:
                    raise TypeError(f"Неверный тип данных: {type(encrypted_data)}")

            logger.debug(f"Дешифровка: {len(encrypted_data)} байт, первые 10: {encrypted_data[:10].hex()}")

            decrypted_bytes = self.cipher_suite.decrypt(encrypted_data)
            decrypted = decrypted_bytes.decode('utf-8')

            logger.debug(f"Успешно дешифровано: '{decrypted[:20]}...'")
            return decrypted

        except InvalidToken:
            logger.error(f"Неверный токен. Возможно неверный ключ шифрования.")
            logger.error(f"Данные (hex): {encrypted_data[:50].hex()}...")
            raise
        except Exception as e:
            logger.error(f"Ошибка дешифровки {type(e).__name__}: {e}")
            logger.error(f"Данные тип: {type(encrypted_data)}, длина: {len(encrypted_data)}")
            raise