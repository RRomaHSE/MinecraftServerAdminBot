from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    """Состояния процесса авторизации"""
    waiting_for_host = State()      # host:port
    waiting_for_password = State()  # RCON